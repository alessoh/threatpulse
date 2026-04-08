import sys
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from app.core.database import SessionLocal
from app.core.config import get_settings
from app.scrapers.collectors import run_all_scrapers, scrape_cisa_kev, scrape_nvd_recent, scrape_rss_feed, RSS_FEEDS


def run_once():
    db = SessionLocal()
    try:
        run_all_scrapers(db)
    finally:
        db.close()


def run_cisa():
    db = SessionLocal()
    try:
        scrape_cisa_kev(db)
    finally:
        db.close()


def run_nvd():
    db = SessionLocal()
    try:
        scrape_nvd_recent(db)
    finally:
        db.close()


def run_rss():
    db = SessionLocal()
    try:
        for name, url in RSS_FEEDS.items():
            scrape_rss_feed(db, url, name)
    finally:
        db.close()


def seed():
    """Seed database with initial threat data for development."""
    from app.scrapers.collectors import upsert_threat
    db = SessionLocal()

    seed_threats = [
        {"name": "LockBit 4.0 Ransomware", "severity": "critical", "threat_type": "ransomware",
         "tags": "Ransomware,Healthcare,RaaS", "summary": "Fourth-generation LockBit ransomware-as-a-service with enhanced encryption completing full-disk encryption in under four minutes. Actively targeting hospitals, municipal governments, and manufacturing.",
         "technical_analysis": "Initial access via CVE-2024-XXXX (Citrix NetScaler RCE) and CVE-2024-YYYY (FortiGate SSL-VPN). Uses ChaCha20-Poly1305 encryption with RSA-2048 wrapped keys. Deploys via DLL sideloading through legitimate Windows binaries.",
         "affected_systems": "Windows Server 2016-2025, VMware ESXi 7.x/8.x, Linux with exposed SSH",
         "iocs": "sha256:a3f5b...e91d\nC2: 185.220.xx.xx:443\nRESTORE-FILES.txt\nHKLM\\SOFTWARE\\LockBit4",
         "remediation_steps": '[{"title":"Patch Edge Devices","description":"Patch Citrix NetScaler and FortiGate immediately"},{"title":"Disable ESXi SSH","description":"Run vim-cmd hostsvc/disable_ssh on all ESXi hosts"},{"title":"Rotate Credentials","description":"Reset KRBTGT twice with 12h interval"},{"title":"Deploy Canary Files","description":"Place decoy files in high-value directories"}]',
         "cvss_score": 9.8, "cve_ids": "CVE-2024-XXXX,CVE-2024-YYYY", "industries_affected": "Healthcare,Government,Manufacturing"},
        {"name": "Ivanti Connect Secure Zero-Day Chain", "severity": "critical", "threat_type": "zero-day",
         "tags": "Zero-Day,VPN,Edge Device", "summary": "Two chained zero-days in Ivanti VPN appliances enabling unauthenticated remote code execution. Mass exploitation targeting government and defense across 12 countries.",
         "affected_systems": "Ivanti Connect Secure pre-22.7R2.5, Policy Secure, Neurons for ZTA",
         "iocs": "Web shells in /dana-na/auth/\nModified /home/perl/DSLogConfig.pm\nIntegrity checker bypass",
         "remediation_steps": '[{"title":"Patch or Disconnect","description":"Apply Ivanti patches immediately or disconnect appliances"},{"title":"Run Integrity Check","description":"Compare against known-good baselines"},{"title":"Factory Reset","description":"Reset before patching if compromise found"},{"title":"Rotate VPN Credentials","description":"Rotate all credentials that transited the VPN"}]',
         "cvss_score": 9.1, "industries_affected": "Government,Defense,Financial"},
        {"name": "Volt Typhoon Infrastructure Pre-positioning", "severity": "high", "threat_type": "apt",
         "tags": "APT,State-Sponsored,Critical Infrastructure", "summary": "Chinese state-sponsored group maintaining persistent access in US energy, water, and telecom networks using living-off-the-land techniques that blend with normal admin activity.",
         "affected_systems": "Fortinet FortiGuard, Cisco routers, SOHO equipment, Windows AD environments",
         "iocs": "ntdsutil abuse\nnetsh port forwarding\nCompromised SOHO routers as proxies\nUnusual LDAP from edge devices",
         "remediation_steps": '[{"title":"Audit Edge Devices","description":"Check for unauthorized config changes and unknown admin accounts"},{"title":"Replace EOL Routers","description":"Remove all end-of-life SOHO networking equipment"},{"title":"Enhanced Logging","description":"Enable PowerShell, WMI, and LDAP logging on domain controllers"},{"title":"Review CISA AA24-038A","description":"Follow comprehensive detection guidance"}]',
         "industries_affected": "Energy,Water,Telecommunications"},
        {"name": "Scattered Spider Social Engineering", "severity": "high", "threat_type": "phishing",
         "tags": "Social Engineering,Identity,MFA Bypass", "summary": "English-speaking group using SIM-swapping and MFA fatigue attacks to compromise enterprise identity providers via IT help desk impersonation calls.",
         "affected_systems": "Okta, Azure AD, IT help desks without strict identity verification",
         "iocs": "MFA push floods >10/min\nResidential proxy credential stuffing\nHelp desk calls for exec resets\nAnomalous MFA registrations",
         "remediation_steps": '[{"title":"Deploy FIDO2 Keys","description":"Implement hardware security keys and deprecate SMS/push MFA"},{"title":"Verified Callbacks","description":"Establish callback verification for all help desk requests"},{"title":"Impossible Travel Detection","description":"Alert on geographically impossible authentication patterns"},{"title":"Help Desk Training","description":"Regular social engineering tabletop exercises"}]',
         "industries_affected": "Technology,Financial,Telecommunications"},
        {"name": "PyPI Malicious Package Campaign", "severity": "high", "threat_type": "supply-chain",
         "tags": "Supply Chain,Python,Developer Tools", "summary": "Coordinated campaign publishing typosquatted Python packages to steal environment variables, SSH keys, and cloud credentials from developer workstations and CI/CD pipelines.",
         "affected_systems": "Python developers, CI/CD pulling from PyPI, AWS/GCP/Azure credentials in env vars",
         "iocs": "Typosquatted package names\nPost-install encoded payloads\n.env and .ssh exfiltration\nDNS-based data exfiltration",
         "remediation_steps": '[{"title":"Package Allowlisting","description":"Implement allowlists in CI/CD pipelines"},{"title":"Hash Verification","description":"Use pip --require-hashes for all dependencies"},{"title":"Secret Scanning","description":"Deploy scanning for credentials in env vars and repos"},{"title":"DNS Monitoring","description":"Watch for unusual queries from build servers"}]',
         "industries_affected": "Technology,Software Development"},
    ]

    try:
        for t in seed_threats:
            upsert_threat(db, t)
        print(f"Seeded {len(seed_threats)} threats.")
    finally:
        db.close()


if __name__ == "__main__":
    if "--seed" in sys.argv:
        seed()
    elif "--watch" in sys.argv:
        settings = get_settings()
        print("Starting scheduled scraper...")
        run_once()
        scheduler = BlockingScheduler()
        scheduler.add_job(run_cisa, "interval", hours=settings.scrape_cisa_interval_hours, id="cisa")
        scheduler.add_job(run_nvd, "interval", hours=settings.scrape_nvd_interval_hours, id="nvd")
        scheduler.add_job(run_rss, "interval", hours=settings.scrape_vendor_interval_hours, id="rss")
        scheduler.start()
    else:
        run_once()
