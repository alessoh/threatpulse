import anthropic
import json
from typing import Optional, List
from app.core.config import get_settings


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_settings().anthropic_api_key)


def synthesize_threat(raw_data: dict) -> dict:
    """Take raw threat data from scrapers and produce a structured threat profile."""
    client = get_client()

    prompt = f"""Analyze this raw cyber threat data and produce a structured threat profile.

Raw data:
{json.dumps(raw_data, indent=2)}

Return ONLY a JSON object with these fields:
{{
  "name": "Threat name",
  "severity": "critical|high|medium|low",
  "threat_type": "ransomware|apt|zero-day|supply-chain|phishing|malware|other",
  "tags": "comma,separated,tags",
  "summary": "2-3 sentence executive summary",
  "technical_analysis": "3-5 sentence technical analysis with specific CVEs, encryption methods, attack vectors",
  "affected_systems": "Specific systems, versions, and configurations affected",
  "iocs": "Newline-separated indicators of compromise (hashes, IPs, domains, file names)",
  "remediation_steps": "JSON array of step objects: [{{\\"title\\": \\"Step name\\", \\"description\\": \\"What to do\\"}}]",
  "cvss_score": null or float,
  "cve_ids": "comma-separated CVE IDs if applicable",
  "industries_affected": "comma-separated industries"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]

    return json.loads(cleaned)


def advisor_chat(message: str, threat_context: Optional[str] = None, history: List[dict] = None) -> str:
    """AI Threat Advisor conversation."""
    client = get_client()

    system = """You are the ThreatPulse AI Threat Advisor, a cybersecurity expert assistant.
Keep answers concise: 3-6 sentences maximum. Be practical and actionable.
Use plain text without markdown. When recommending actions, prioritize by urgency.
Reference specific tools, commands, or configurations when possible."""

    if threat_context:
        system += f"\n\nCurrent threat context:\n{threat_context}"

    messages = []
    if history:
        messages.extend(history[-18:])
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system=system,
        messages=messages,
    )

    return response.content[0].text


def generate_weekly_digest(threats: list) -> str:
    """Generate a weekly threat digest email body."""
    client = get_client()

    threat_summaries = "\n".join(
        [f"- {t.name} ({t.severity}): {t.summary}" for t in threats[:10]]
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Write a concise weekly cyber threat digest email based on these threats from the past week:

{threat_summaries}

Format as a professional email body (plain text, no markdown) with:
- A 2-sentence overview of the week's threat landscape
- The top 3 threats with one-sentence descriptions
- One recommended action item

Keep it under 300 words. Be direct and actionable.""",
        }],
    )

    return response.content[0].text
