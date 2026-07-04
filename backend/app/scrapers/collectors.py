import httpx
import feedparser
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import Threat, ScraperLog
from app.services.ai_service import synthesize_threat
from app.services.email_service import notify_users_of_threat


def slugify(text: str) -> str:
    return text.lower().strip().replace(" ", "-").replace("/", "-")[:200]


def log_scrape(db: Session, source: str, status: str, found: int, new: int, error: str = None):
    db.add(ScraperLog(source=source, status=status, items_found=found, items_new=new, error_message=error))
    db.commit()


def already_have(db: Session, cve_id: str = "", url: str = "") -> bool:
    """Dedup check that runs BEFORE the Claude call, keyed on stable external
    identifiers, so scrape cycles never re-pay to synthesize a threat that is
    already stored."""
    if cve_id:
        ident = cve_id.strip()
        if ident and db.query(Threat.id).filter(Threat.cve_ids.ilike(f"%{ident}%")).first():
            return True
    if url:
        u = url.strip()
        if u and db.query(Threat.id).filter(Threat.source_urls.ilike(f"%{u}%")).first():
            return True
    return False


def upsert_threat(db: Session, data: dict) -> Optional[Threat]:
    """Insert or update a threat profile. Returns the threat if new."""
    slug = slugify(data.get("name", "unknown"))
    existing = db.query(Threat).filter(Threat.slug == slug).first()

    if existing:
        for key in ["summary", "technical_analysis", "affected_systems", "iocs", "remediation_steps", "cvss_score", "severity"]:
            if data.get(key):
                setattr(existing, key, data[key])
        existing.last_updated = datetime.now(timezone.utc)
        db.commit()
        return None

    remediation = data.get("remediation_steps", "")
    if isinstance(remediation, list):
        remediation = json.dumps(remediation)

    threat = Threat(
        name=data["name"],
        slug=slug,
        severity=data.get("severity", "medium"),
        threat_type=data.get("threat_type", "other"),
        category=data.get("category", "conventional"),
        tags=data.get("tags", ""),
        summary=data.get("summary", ""),
        technical_analysis=data.get("technical_analysis", ""),
        affected_systems=data.get("affected_systems", ""),
        iocs=data.get("iocs", ""),
        remediation_steps=remediation,
        source_urls=data.get("source_urls", ""),
        cvss_score=data.get("cvss_score"),
        cve_ids=data.get("cve_ids", ""),
        industries_affected=data.get("industries_affected", ""),
    )
    db.add(threat)
    db.commit()
    db.refresh(threat)
    return threat


# ── CISA Known Exploited Vulnerabilities ──

def scrape_cisa_kev(db: Session, limit: int = 20) -> int:
    """Scrape CISA Known Exploited Vulnerabilities catalog."""
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    new_count = 0
    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        vulns = data.get("vulnerabilities", [])
        recent = [v for v in vulns if _is_recent(v.get("dateAdded", ""), days=7)]

        processed = 0
        for vuln in recent:
            if processed >= limit:
                break
            if already_have(db, cve_id=vuln.get("cveID", "")):
                continue
            processed += 1
            raw = {
                "cve_id": vuln.get("cveID", ""),
                "vendor": vuln.get("vendorProject", ""),
                "product": vuln.get("product", ""),
                "name": vuln.get("vulnerabilityName", ""),
                "description": vuln.get("shortDescription", ""),
                "date_added": vuln.get("dateAdded", ""),
                "due_date": vuln.get("dueDate", ""),
                "source": "CISA KEV",
            }
            try:
                synthesized = synthesize_threat(raw)
                synthesized["source_urls"] = f"https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
                threat = upsert_threat(db, synthesized)
                if threat:
                    new_count += 1
                    notify_users_of_threat(db, threat)
            except Exception as e:
                print(f"Synthesis error for {raw.get('cve_id')}: {e}")

        log_scrape(db, "CISA KEV", "success", len(recent), new_count)
    except Exception as e:
        log_scrape(db, "CISA KEV", "error", 0, 0, str(e))
    return new_count


# ── NVD Recent CVEs ──

def scrape_nvd_recent(db: Session, limit: int = 15) -> int:
    """Scrape NVD for recently published high-severity CVEs."""
    new_count = 0
    # NVD rejects requests that set pubStartDate without pubEndDate (404)
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=3)).strftime("%Y-%m-%dT00:00:00.000")
    end = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?pubStartDate={start}&pubEndDate={end}&cvssV3Severity=CRITICAL"

    try:
        resp = httpx.get(url, timeout=60, headers={"Accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        vulns = data.get("vulnerabilities", [])

        processed = 0
        for item in vulns:
            cve = item.get("cve", {})
            desc_list = cve.get("descriptions", [])
            desc = next((d["value"] for d in desc_list if d["lang"] == "en"), "")
            cve_id = cve.get("id", "")
            if processed >= limit:
                break
            if already_have(db, cve_id=cve_id):
                continue
            processed += 1

            metrics = cve.get("metrics", {})
            cvss_data = metrics.get("cvssMetricV31", [{}])
            cvss_score = cvss_data[0].get("cvssData", {}).get("baseScore") if cvss_data else None

            raw = {
                "cve_id": cve_id,
                "description": desc,
                "cvss_score": cvss_score,
                "source": "NVD",
            }
            try:
                synthesized = synthesize_threat(raw)
                synthesized["cve_ids"] = cve_id
                synthesized["cvss_score"] = cvss_score
                synthesized["source_urls"] = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                threat = upsert_threat(db, synthesized)
                if threat:
                    new_count += 1
                    notify_users_of_threat(db, threat)
            except Exception as e:
                print(f"Synthesis error for {cve_id}: {e}")

        log_scrape(db, "NVD", "success", len(vulns), new_count)
    except Exception as e:
        log_scrape(db, "NVD", "error", 0, 0, str(e))
    return new_count


# ── RSS Feed Scraper (CISA Alerts, Vendor Blogs) ──

def scrape_rss_feed(db: Session, feed_url: str, source_name: str, limit: int = 10) -> int:
    """Generic RSS feed scraper for security advisories."""
    new_count = 0
    try:
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:10]

        processed = 0
        for entry in entries:
            if processed >= limit:
                break
            if already_have(db, url=entry.get("link", "")):
                continue
            processed += 1
            raw = {
                "title": entry.get("title", ""),
                "description": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": source_name,
            }
            try:
                synthesized = synthesize_threat(raw)
                synthesized["source_urls"] = entry.get("link", "")
                threat = upsert_threat(db, synthesized)
                if threat:
                    new_count += 1
                    notify_users_of_threat(db, threat)
            except Exception as e:
                print(f"Synthesis error for RSS entry: {e}")

        log_scrape(db, source_name, "success", len(entries), new_count)
    except Exception as e:
        log_scrape(db, source_name, "error", 0, 0, str(e))
    return new_count


# ── Helpers ──

def _is_recent(date_str: str, days: int = 7) -> bool:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt > datetime.now(timezone.utc) - timedelta(days=days)
    except (ValueError, TypeError):
        return False


# ── RSS Feed URLs ──

RSS_FEEDS = {
    "CISA Alerts": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "US-CERT": "https://www.us-cert.gov/ncas/current-activity.xml",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
}


def run_all_scrapers(db: Session):
    """Run all scrapers."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting scrape cycle...")

    total = 0
    total += scrape_cisa_kev(db)
    total += scrape_nvd_recent(db)

    for name, url in RSS_FEEDS.items():
        total += scrape_rss_feed(db, url, name)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Scrape complete. {total} new threats added.")
    return total
