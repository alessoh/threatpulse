"""
Collectors for agent-to-agent threat intelligence.

New module for backend/app/scrapers/. It gathers raw signals about threats to
and between AI agents from four kinds of sources, then hands each item to
ai_service.synthesize_agent_threat for taxonomy-aware structuring:

  1. GitHub Security Advisories for watched agent frameworks and MCP tooling.
  2. NVD keyword queries for agent, MCP, and prompt-injection related CVEs.
  3. arXiv cs.CR for new multi-agent and prompt-injection security research.
  4. Curated researcher and project feeds covering agentic security.

Design notes relative to the original collectors.py:
  1. Deduplication happens BEFORE the model call, keyed on stable external
     identifiers (GHSA id, CVE id, source URL), so repeated scrape cycles do
     not re-pay for synthesis of items already in the database.
  2. Threats dedupe on identifier, not on the model-generated name, so the
     same CVE arriving from two sources cannot create two rows.
  3. NVD requests honor an optional NVD_API_KEY environment variable and
     sleep between keyword queries to respect published rate limits.

Wiring: add run_agent_scrapers to run.py on its own schedule, or fold it into
run_all_scrapers. seed_agent_threats mirrors the existing seed flow and can be
invoked with: python -m app.scrapers.agent_collectors --seed
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.parse import quote

import httpx
import feedparser
from sqlalchemy.orm import Session

from app.models.user import Threat, ScraperLog
from app.services.ai_service import synthesize_agent_threat
from app.services.email_service import notify_users_of_threat


# ═════════════════════════════════════════════════════════════════
# Watchlists (edit freely; these drive what gets monitored)
# ═════════════════════════════════════════════════════════════════

WATCHED_PACKAGES = {
    "pip": [
        "langchain", "langchain-core", "langgraph", "llama-index",
        "crewai", "autogen-agentchat", "pyautogen", "mcp", "fastmcp",
        "openai-agents", "semantic-kernel", "smolagents",
    ],
    "npm": [
        "@modelcontextprotocol/sdk", "@modelcontextprotocol/inspector",
        "mcp-remote", "langchain", "@langchain/core", "@openai/agents",
    ],
}

NVD_AGENT_KEYWORDS = [
    "model context protocol",
    "prompt injection",
    "LLM agent",
    "langchain",
    "llama index",
    "autogen",
]

# Verify each feed URL once before first production run; publishers move them.
AGENT_RSS_FEEDS = {
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Embrace The Red": "https://embracethered.com/blog/index.xml",
    "OWASP GenAI Security": "https://genai.owasp.org/feed/",
}

ARXIV_QUERY = (
    'cat:cs.CR AND (all:"prompt injection" OR all:"multi-agent security" '
    'OR all:"tool poisoning" OR all:"model context protocol" '
    'OR all:"agent hijacking")'
)


# ═════════════════════════════════════════════════════════════════
# Shared helpers
# ═════════════════════════════════════════════════════════════════

def slugify(text: str) -> str:
    return text.lower().strip().replace(" ", "-").replace("/", "-")[:200]


def log_scrape(db: Session, source: str, status: str, found: int, new: int,
               error: str = None):
    db.add(ScraperLog(source=source, status=status, items_found=found,
                      items_new=new, error_message=error))
    db.commit()


def already_ingested(db: Session, identifier: str = "",
                     source_url: str = "") -> bool:
    """Check for an existing row by external id or source URL.

    Runs BEFORE synthesis so duplicate feed items cost nothing. The
    identifier is matched against cve_ids and slug; the URL against
    source_urls.
    """
    if identifier:
        ident = identifier.strip()
        if ident:
            hit = db.query(Threat.id).filter(
                (Threat.cve_ids.ilike(f"%{ident}%"))
                | (Threat.slug == slugify(ident))
            ).first()
            if hit:
                return True
    if source_url:
        url = source_url.strip()
        if url:
            hit = db.query(Threat.id).filter(
                Threat.source_urls.ilike(f"%{url}%")
            ).first()
            if hit:
                return True
    return False


def upsert_agent_threat(db: Session, data: dict, identifier: str = "",
                        source_url: str = "") -> Optional[Threat]:
    """Insert a synthesized agent threat, or refresh an existing row.

    Dedupe order: external identifier, then source URL, then name slug.
    Returns the Threat only when it is new, mirroring the original upsert
    contract so alerting behaves the same way.
    """
    existing = None
    ident = (identifier or "").strip()
    if ident:
        existing = db.query(Threat).filter(
            (Threat.cve_ids.ilike(f"%{ident}%"))
            | (Threat.slug == slugify(ident))
        ).first()
    if not existing and source_url:
        existing = db.query(Threat).filter(
            Threat.source_urls.ilike(f"%{source_url.strip()}%")
        ).first()
    slug = slugify(ident or data.get("name", "unknown"))
    if not existing:
        existing = db.query(Threat).filter(Threat.slug == slug).first()

    if existing:
        for key in ("summary", "technical_analysis", "affected_systems",
                    "iocs", "remediation_steps", "cvss_score", "severity",
                    "tags"):
            if data.get(key):
                setattr(existing, key, data[key])
        existing.last_updated = datetime.now(timezone.utc)
        db.commit()
        return None

    threat = Threat(
        name=data["name"],
        slug=slug,
        severity=data.get("severity", "medium"),
        threat_type=data.get("threat_type", "other"),
        tags=data.get("tags", ""),
        summary=data.get("summary", ""),
        technical_analysis=data.get("technical_analysis", ""),
        affected_systems=data.get("affected_systems", ""),
        iocs=data.get("iocs", ""),
        remediation_steps=data.get("remediation_steps", "[]"),
        source_urls=source_url or data.get("source_urls", ""),
        cvss_score=data.get("cvss_score"),
        cve_ids=data.get("cve_ids", "") or ident,
        industries_affected=data.get("industries_affected", ""),
    )
    db.add(threat)
    db.commit()
    db.refresh(threat)
    return threat


def _synthesize_and_store(db: Session, raw: dict, identifier: str,
                          source_url: str) -> int:
    """Run one item through synthesis and storage. Returns 1 if new."""
    try:
        profile = synthesize_agent_threat(raw)
    except Exception as exc:
        print(f"Agent synthesis error for {identifier or source_url}: {exc}")
        return 0
    threat = upsert_agent_threat(db, profile, identifier=identifier,
                                 source_url=source_url)
    if threat:
        try:
            notify_users_of_threat(db, threat)
        except Exception as exc:
            print(f"Notify error for {threat.slug}: {exc}")
        return 1
    return 0


def _recent_iso(value: str, days: int) -> bool:
    """True when an ISO-8601 timestamp string falls within the window."""
    if not value:
        return False
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp > datetime.now(timezone.utc) - timedelta(days=days)
    except (ValueError, TypeError):
        return False


# ═════════════════════════════════════════════════════════════════
# 1. GitHub Security Advisories for watched agent packages
# ═════════════════════════════════════════════════════════════════

def scrape_github_advisories(db: Session, days: int = 14) -> int:
    """Pull recent GHSA advisories affecting watched agent frameworks."""
    new_count = 0
    found = 0
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        for ecosystem, packages in WATCHED_PACKAGES.items():
            affects = ",".join(packages)
            url = (
                "https://api.github.com/advisories"
                f"?ecosystem={ecosystem}&affects={quote(affects)}&per_page=15"
            )
            resp = httpx.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            for adv in resp.json():
                if not _recent_iso(adv.get("published_at", ""), days):
                    continue
                found += 1
                ghsa = adv.get("ghsa_id", "")
                cve = adv.get("cve_id") or ""
                link = adv.get("html_url", "")
                ident = cve or ghsa
                if already_ingested(db, identifier=ident, source_url=link):
                    continue
                vulns = adv.get("vulnerabilities") or []
                pkgs = ", ".join(
                    f"{(v.get('package') or {}).get('name', '?')} "
                    f"{v.get('vulnerable_version_range', '')}".strip()
                    for v in vulns[:5]
                )
                raw = {
                    "source": f"GitHub Advisory ({ecosystem})",
                    "ghsa_id": ghsa,
                    "cve_id": cve,
                    "title": adv.get("summary", ""),
                    "description": (adv.get("description") or "")[:4000],
                    "severity": adv.get("severity", ""),
                    "cvss_score": (adv.get("cvss") or {}).get("score"),
                    "affected_packages": pkgs,
                    "published_at": adv.get("published_at", ""),
                }
                new_count += _synthesize_and_store(db, raw, ident, link)
        log_scrape(db, "GHSA agent watchlist", "success", found, new_count)
    except Exception as exc:
        log_scrape(db, "GHSA agent watchlist", "error", found, new_count,
                   str(exc))
    return new_count


# ═════════════════════════════════════════════════════════════════
# 2. NVD keyword search for agent-related CVEs
# ═════════════════════════════════════════════════════════════════

def scrape_nvd_agent_cves(db: Session, days: int = 3) -> int:
    """Search NVD for recently published CVEs matching agent keywords."""
    new_count = 0
    found = 0
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%dT00:00:00.000")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59.999")
    headers = {"Accept": "application/json"}
    api_key = os.environ.get("NVD_API_KEY", "")
    if api_key:
        headers["apiKey"] = api_key

    try:
        for keyword in NVD_AGENT_KEYWORDS:
            url = (
                "https://services.nvd.nist.gov/rest/json/cves/2.0"
                f"?keywordSearch={quote(keyword)}"
                f"&pubStartDate={start}&pubEndDate={end}&resultsPerPage=10"
            )
            resp = httpx.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            for item in resp.json().get("vulnerabilities", []):
                cve = item.get("cve", {})
                cve_id = cve.get("id", "")
                found += 1
                link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                if already_ingested(db, identifier=cve_id, source_url=link):
                    continue
                descs = cve.get("descriptions", [])
                desc = next((d["value"] for d in descs
                             if d.get("lang") == "en"), "")
                metrics = cve.get("metrics", {})
                cvss_list = metrics.get("cvssMetricV31") or []
                score = (cvss_list[0].get("cvssData", {}).get("baseScore")
                         if cvss_list else None)
                raw = {
                    "source": "NVD agent keyword search",
                    "matched_keyword": keyword,
                    "cve_id": cve_id,
                    "description": desc[:4000],
                    "cvss_score": score,
                }
                new_count += _synthesize_and_store(db, raw, cve_id, link)
            # NVD asks unauthenticated clients to stay under 5 requests
            # per rolling 30 seconds; keyed clients get 50.
            time.sleep(2 if api_key else 7)
        log_scrape(db, "NVD agent keywords", "success", found, new_count)
    except Exception as exc:
        log_scrape(db, "NVD agent keywords", "error", found, new_count,
                   str(exc))
    return new_count


# ═════════════════════════════════════════════════════════════════
# 3. arXiv cs.CR research on multi-agent and injection attacks
# ═════════════════════════════════════════════════════════════════

def scrape_arxiv_agent_security(db: Session, max_results: int = 10) -> int:
    """Ingest new agent-security research papers as low/medium items."""
    new_count = 0
    found = 0
    url = (
        "https://export.arxiv.org/api/query?search_query="
        + quote(ARXIV_QUERY)
        + f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        for entry in feed.entries:
            found += 1
            link = entry.get("id", entry.get("link", ""))
            if not link or already_ingested(db, source_url=link):
                continue
            raw = {
                "source": "arXiv cs.CR (research, not an active exploit)",
                "title": entry.get("title", ""),
                "abstract": entry.get("summary", "")[:4000],
                "published": entry.get("published", ""),
                "link": link,
            }
            new_count += _synthesize_and_store(db, raw, "", link)
        log_scrape(db, "arXiv agent security", "success", found, new_count)
    except Exception as exc:
        log_scrape(db, "arXiv agent security", "error", found, new_count,
                   str(exc))
    return new_count


# ═════════════════════════════════════════════════════════════════
# 4. Researcher and project feeds
# ═════════════════════════════════════════════════════════════════

AGENT_SIGNAL_TERMS = (
    "prompt injection", "mcp", "model context protocol", "agent", "a2a",
    "tool poisoning", "jailbreak", "exfiltrat", "langchain", "autogen",
)


def scrape_agent_rss(db: Session, feed_url: str, source_name: str,
                     limit: int = 10) -> int:
    """Ingest agent-relevant posts from a researcher or project feed.

    Entries are filtered on agent-security terms before synthesis so general
    posts from broad feeds do not consume model calls.
    """
    new_count = 0
    found = 0
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            title = entry.get("title", "")
            body = entry.get("summary", entry.get("description", ""))
            haystack = f"{title} {body}".lower()
            if not any(term in haystack for term in AGENT_SIGNAL_TERMS):
                continue
            found += 1
            link = entry.get("link", "")
            if not link or already_ingested(db, source_url=link):
                continue
            raw = {
                "source": source_name,
                "title": title,
                "description": body[:4000],
                "published": entry.get("published", ""),
                "link": link,
            }
            new_count += _synthesize_and_store(db, raw, "", link)
        log_scrape(db, source_name, "success", found, new_count)
    except Exception as exc:
        log_scrape(db, source_name, "error", found, new_count, str(exc))
    return new_count


# ═════════════════════════════════════════════════════════════════
# Orchestration and seed data
# ═════════════════════════════════════════════════════════════════

def run_agent_scrapers(db: Session) -> int:
    """Run every agent-threat collector once."""
    stamp = datetime.now(timezone.utc).isoformat()
    print(f"[{stamp}] Starting agent-threat scrape cycle...")
    total = 0
    total += scrape_github_advisories(db)
    total += scrape_nvd_agent_cves(db)
    total += scrape_arxiv_agent_security(db)
    for name, url in AGENT_RSS_FEEDS.items():
        total += scrape_agent_rss(db, url, name)
    stamp = datetime.now(timezone.utc).isoformat()
    print(f"[{stamp}] Agent scrape complete. {total} new threats added.")
    return total


def seed_agent_threats(db: Session) -> int:
    """Seed illustrative agent-to-agent threats so the pivot demos well.

    Entries reference real, publicly documented issues. Detection signatures
    are defensive descriptions, never working payloads.
    """
    seeds = [
        {
            "name": "MCP Tool Poisoning via Hidden Tool Descriptions",
            "severity": "high",
            "threat_type": "tool-poisoning",
            "tags": "ASI04,surface:tool-layer,propagation:single-hop,MCP",
            "summary": (
                "Malicious or compromised MCP servers embed hidden "
                "instructions in tool metadata that the model reads but the "
                "human approving the tool never sees, steering agents into "
                "data exfiltration or unauthorized actions. First documented "
                "publicly by Invariant Labs in 2025 and since reproduced "
                "across many clients."),
            "technical_analysis": (
                "Tool descriptions are injected into the agent's context at "
                "connection time, before any invocation is approved. "
                "Attackers hide directives in description fields, sometimes "
                "inside emphasis markers, instructing the model to read "
                "sensitive files or route data through attacker parameters. "
                "Variants include rug pulls, where a server's tool "
                "definitions change after initial approval, and cross-server "
                "shadowing, where one server's descriptions manipulate calls "
                "to another server's tools."),
            "affected_systems": (
                "MCP clients that render tool descriptions unsanitized; "
                "protocols: MCP"),
            "iocs": (
                "Tool descriptions containing imperative instructions to the "
                "model rather than plain capability text\n"
                "Tool definitions that change between sessions without a "
                "version bump\n"
                "Parameters that ask for file paths, keys, or prior "
                "conversation content unrelated to the tool's purpose"),
            "remediation_steps": json.dumps([
                {"title": "Pin and verify servers",
                 "description": "Pin MCP server versions and hash tool "
                                "definitions; alert on any drift."},
                {"title": "Show full metadata",
                 "description": "Surface complete tool descriptions in "
                                "approval UIs so hidden text is visible."},
                {"title": "Least-privilege tools",
                 "description": "Scope filesystem and network access per "
                                "tool; deny broad reads by default."},
                {"title": "Scan definitions",
                 "description": "Run static scans over tool metadata for "
                                "instruction-like language before allowing "
                                "connections."},
            ]),
            "cve_ids": "",
            "industries_affected": "Technology,Software Development",
        },
        {
            "name": "mcp-remote OAuth Command Injection (CVE-2025-6514)",
            "severity": "critical",
            "threat_type": "protocol-vulnerability",
            "tags": "ASI04,surface:protocol,propagation:none,MCP,supply-chain",
            "summary": (
                "A critical flaw in the widely used mcp-remote OAuth proxy "
                "let malicious MCP servers achieve remote code execution on "
                "connecting developer machines, turning a routine agent "
                "connection into full host compromise. The package had "
                "hundreds of thousands of downloads before patching."),
            "technical_analysis": (
                "mcp-remote bridges local clients to remote MCP servers and "
                "handles OAuth discovery. A hostile server could supply "
                "authorization metadata that the proxy passed into system "
                "URL handling without validation, yielding command "
                "injection during the connection handshake. Because the "
                "component sits in the trust path for many agent setups, "
                "one malicious endpoint compromised the host running the "
                "agent."),
            "affected_systems": (
                "mcp-remote versions prior to the patched release; "
                "protocols: MCP, OAuth"),
            "iocs": (
                "Agent hosts initiating OAuth flows to unfamiliar MCP "
                "endpoints\n"
                "mcp-remote present at a vulnerable version in lockfiles\n"
                "Unexpected child processes spawned during MCP connection "
                "setup"),
            "remediation_steps": json.dumps([
                {"title": "Update mcp-remote",
                 "description": "Upgrade to the patched release everywhere, "
                                "including CI images and dev containers."},
                {"title": "Allowlist MCP endpoints",
                 "description": "Restrict agents to an approved list of "
                                "remote MCP servers."},
                {"title": "Prefer HTTPS-only remotes",
                 "description": "Reject plain HTTP MCP endpoints in client "
                                "configuration."},
            ]),
            "cvss_score": 9.6,
            "cve_ids": "CVE-2025-6514",
            "industries_affected": "Technology,Software Development",
        },
        {
            "name": "MCP Inspector Unauthenticated RCE (CVE-2025-49596)",
            "severity": "critical",
            "threat_type": "framework-vulnerability",
            "tags": "ASI05,surface:tool-layer,propagation:none,MCP",
            "summary": (
                "The MCP Inspector developer tool shipped a proxy that "
                "lacked authentication, allowing browser-based attackers to "
                "reach it from a malicious web page and execute code on the "
                "developer's machine. Reported by Oligo Security with a "
                "CVSS score of 9.4."),
            "technical_analysis": (
                "Inspector's local proxy accepted commands without "
                "verifying the caller, so a drive-by page could target the "
                "well-known local port and drive the tool into spawning "
                "processes. The pattern generalizes: local agent tooling "
                "that binds unauthenticated servers converts every browser "
                "tab into a potential bridge to the agent host."),
            "affected_systems": (
                "MCP Inspector prior to 0.14.1; protocols: MCP"),
            "iocs": (
                "Inspector proxy ports reachable without a session token\n"
                "Browser-origin requests hitting local agent tooling ports\n"
                "Inspector versions below 0.14.1 in developer environments"),
            "remediation_steps": json.dumps([
                {"title": "Upgrade Inspector",
                 "description": "Move to 0.14.1 or later, which adds session "
                                "tokens and origin checks."},
                {"title": "Bind to localhost with auth",
                 "description": "Require authentication on all local agent "
                                "tooling; never expose it on 0.0.0.0."},
            ]),
            "cvss_score": 9.4,
            "cve_ids": "CVE-2025-49596",
            "industries_affected": "Technology,Software Development",
        },
        {
            "name": "Cross-Agent Prompt Infection in Multi-Agent Pipelines",
            "severity": "high",
            "threat_type": "agent-worm",
            "tags": "ASI01,ASI07,surface:inter-agent-comms,"
                    "propagation:self-propagating",
            "summary": (
                "Adversarial instructions planted in content processed by "
                "one agent can replicate into its outputs and infect "
                "downstream agents, spreading through normal inter-agent "
                "messaging the way the Morris II research worm spread "
                "through AI email assistants."),
            "technical_analysis": (
                "Multi-agent systems pass unvetted natural-language messages "
                "between planners, workers, and tool users. A payload that "
                "convinces one agent to include it verbatim in summaries, "
                "tickets, or memos rides those channels to every consumer "
                "of that output. Each hop can trigger tool calls, memory "
                "writes, or further replication, so a single poisoned "
                "document can contaminate an entire agent network."),
            "affected_systems": (
                "Multi-agent frameworks passing free-form text between "
                "agents (LangGraph, AutoGen, CrewAI and similar); "
                "protocols: A2A, custom message buses"),
            "iocs": (
                "Identical unusual instruction phrases appearing across "
                "multiple agents' outputs\n"
                "Agents citing directives that appear in no system prompt\n"
                "Spikes in agent-initiated messages following ingestion of "
                "a single external document"),
            "remediation_steps": json.dumps([
                {"title": "Validate inter-agent messages",
                 "description": "Schema-constrain agent-to-agent messages; "
                                "strip or flag imperative text in fields "
                                "meant for data."},
                {"title": "Track provenance",
                 "description": "Tag content derived from external inputs "
                                "and lower its privilege downstream."},
                {"title": "Gate consequential actions",
                 "description": "Require human approval for actions "
                                "triggered by externally derived content."},
            ]),
            "cve_ids": "",
            "industries_affected": "Technology,Financial,Professional Services",
        },
        {
            "name": "Agent Memory Poisoning for Persistent Behavior Change",
            "severity": "high",
            "threat_type": "memory-poisoning",
            "tags": "ASI06,surface:memory,propagation:single-hop",
            "summary": (
                "Attackers seed false facts or standing instructions into "
                "an agent's long-term memory or RAG store, quietly steering "
                "decisions across future sessions long after the original "
                "malicious input is gone."),
            "technical_analysis": (
                "Agents that write summaries of conversations, tool "
                "outputs, or scraped pages into persistent memory will "
                "faithfully store attacker-supplied content when it is "
                "framed as a preference or fact. Poisoned entries are later "
                "retrieved as trusted context, enabling privilege "
                "escalation, data leakage, or sabotage that survives "
                "restarts and is hard to trace to its source."),
            "affected_systems": (
                "Agents with writable long-term memory or shared vector "
                "stores; protocols: RAG pipelines"),
            "iocs": (
                "Memory entries containing imperative instructions rather "
                "than facts\n"
                "Writes to memory sourced from external content without "
                "provenance tags\n"
                "Behavioral shifts correlated with specific retrieved "
                "memory records"),
            "remediation_steps": json.dumps([
                {"title": "Validate before writing",
                 "description": "Screen memory writes for instruction-like "
                                "content and require provenance metadata."},
                {"title": "Isolate sessions and tenants",
                 "description": "Partition memory so one user or agent "
                                "cannot poison another's context."},
                {"title": "Snapshot and audit",
                 "description": "Keep memory snapshots to enable diffing, "
                                "forensics, and rollback after suspected "
                                "contamination."},
            ]),
            "cve_ids": "",
            "industries_affected": "Technology,Healthcare,Financial",
        },
    ]

    added = 0
    for item in seeds:
        if upsert_agent_threat(db, item,
                               identifier=item.get("cve_ids", ""),
                               source_url=""):
            added += 1
    print(f"Seeded {added} agent threats.")
    return added


if __name__ == "__main__":
    import sys
    from app.core.database import SessionLocal

    session = SessionLocal()
    try:
        if "--seed" in sys.argv:
            seed_agent_threats(session)
        else:
            run_agent_scrapers(session)
    finally:
        session.close()
