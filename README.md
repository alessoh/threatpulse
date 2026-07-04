# ThreatPulse

**Threat intelligence for the age of AI agents.** ThreatPulse leads with **AI-agent and agent-to-agent threats** (prompt injection, MCP tool poisoning, agent worms, memory poisoning) — the primary feed — with conventional vulnerabilities tracked as a secondary watchlist. Every threat carries an explicit `category` (`agent` or `conventional`), set at ingestion.

**Live site:** https://threatpulse.dev

ThreatPulse scrapes CISA, NVD, GitHub Security Advisories, arXiv, and curated security feeds daily, uses Claude to turn each raw item into a plain-English threat profile with severity, taxonomy tags, and remediation guidance, and presents everything through a dashboard, searchable library, AI-generated response playbooks, and a chat advisor.

## Features

- **Agent threat dashboard** — agent-focused stat tiles, a trending feed of agent threats, and a compact conventional watchlist below it
- **Gemini daily insight** — a landscape briefing written by Google Gemini each day from the week's ingested threats (agent threats first), refreshed after every scrape
- **Threat library** — searchable, filterable catalog; defaults to the agent view with human-readable OWASP ASI labels, with conventional and combined views one click away
- **Agent-threat taxonomy** — threats classified against the OWASP Agentic Top 10 (ASI01–ASI10), with attack-surface and propagation tags
- **AI playbooks** — per-threat incident-response playbooks generated on demand and cached (Pro tier)
- **AI advisor** — chat interface for asking questions about any threat
- **Automated collection** — daily scrape via Vercel Cron; deduplication by CVE ID / source URL before any AI call
- **Accounts & billing** — JWT auth, Free/Pro/Enterprise tiers via Stripe
- **Email** — weekly AI-written digest for subscribers via Resend

## Architecture

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python), SQLAlchemy, Alembic |
| Database | PostgreSQL (Neon in production) |
| AI | Anthropic Claude for threat synthesis (`claude-sonnet-5`; override with `ANTHROPIC_MODEL`) + Google Gemini for the daily insight (`gemini-2.5-flash`; override with `GEMINI_MODEL`) |
| Hosting | Vercel (two projects: frontend + serverless backend), Vercel Cron for scraping |
| Payments / Email | Stripe, Resend (both optional) |

```
threatpulse/
├── frontend/          # Next.js app (dashboard, library, playbooks, pricing)
├── backend/
│   ├── app/
│   │   ├── api/       # REST routes + cron endpoints
│   │   ├── core/      # config, database, auth
│   │   ├── models/    # SQLAlchemy models
│   │   ├── scrapers/  # conventional + agent-threat collectors
│   │   └── services/  # AI synthesis, email, Stripe, digest
│   └── alembic/       # database migrations
├── docs/DEPLOY_VERCEL.md  # step-by-step production deployment guide
└── docker-compose.yml     # local development stack
```

## Installation (local development)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, Mac, or Linux)
- An [Anthropic API key](https://console.anthropic.com) (required for threat synthesis)
- Stripe and Resend keys (optional — payments and email are disabled without them)

### Quick start with Docker

```bash
git clone https://github.com/alessoh/threatpulse.git
cd threatpulse

# Create your environment file
cp .env.example .env   # if no example file exists, create .env with the variables below
```

Minimum `.env` contents:

```env
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=any-long-random-string
```

Then start everything:

```bash
docker-compose up
```

This launches Postgres, the FastAPI backend (with migrations applied automatically), the Next.js frontend, and a scraper worker.

- Frontend: http://localhost:3000
- API: http://localhost:8000 (interactive docs at http://localhost:8000/docs)

### Seed demo data

```bash
docker-compose exec backend python -m app.scrapers.run --seed
```

This loads 10 real, documented threats (5 conventional, 5 agent-focused) so the dashboard is populated immediately.

### Run without Docker (backend only)

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "postgresql://user:pass@host:5432/threatpulse"
$env:JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
alembic upgrade head
uvicorn app.main:app --reload
```

Mac/Linux: same steps with `source .venv/bin/activate` and `export VAR=value`.

## Configuration

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | ✅ | Postgres connection string |
| `JWT_SECRET` | ✅ | Signing key for auth tokens (app refuses to boot with the default) |
| `ANTHROPIC_API_KEY` | ✅ | Claude API access for threat synthesis |
| `ANTHROPIC_MODEL` | — | Override the Claude model (default `claude-sonnet-5`) |
| `GEMINI_API_KEY` | — | Google Gemini key for the daily dashboard insight (falls back to static text without it) |
| `GEMINI_MODEL` | — | Override the Gemini model (default `gemini-2.5-flash`) |
| `CRON_SECRET` | prod | Bearer token protecting the cron endpoints |
| `FRONTEND_URL` / `CORS_ORIGINS` | prod | Frontend origin for redirects and CORS |
| `NEXT_PUBLIC_API_URL` | ✅ (frontend) | Backend URL, baked in at build time |
| `RESEND_API_KEY` / `EMAIL_FROM` | — | Email alerts and weekly digest |
| `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` / `STRIPE_PRICE_*` | — | Subscriptions |
| `NVD_API_KEY` | — | Higher NVD rate limits for the collectors |

## Deployment

The full production setup — Neon Postgres, two Vercel projects, cron jobs, Stripe webhooks, and Windows-friendly commands throughout — is documented step by step in **[docs/DEPLOY_VERCEL.md](docs/DEPLOY_VERCEL.md)**.

To trigger a scrape manually in production:

```powershell
# Windows PowerShell
Invoke-RestMethod -Uri "https://api.threatpulse.dev/api/cron/scrape-all" -Headers @{ Authorization = "Bearer YOUR_CRON_SECRET" }
```

```bash
# Mac/Linux
curl -H "Authorization: Bearer YOUR_CRON_SECRET" https://api.threatpulse.dev/api/cron/scrape-all
```

## Progress

### Done ✅

- [x] Full-stack app deployed on Vercel (frontend + serverless FastAPI backend)
- [x] Neon Postgres with migrations and seed data
- [x] Daily automated scraping via Vercel Cron (CISA KEV, NVD, security RSS, GitHub advisories, arXiv, researcher blogs)
- [x] Claude-powered threat synthesis with JSON validation, retry, and taxonomy clamping
- [x] Deduplication before AI calls (by CVE ID / source URL) to control cost
- [x] Agent-threat taxonomy aligned with OWASP Agentic Top 10
- [x] On-demand, cached AI playbooks
- [x] JWT auth with bcrypt and database-backed rate limiting
- [x] Idempotent alert/digest sends via `alert_logs`
- [x] Fixed in production: retired Claude model replacement, NVD collector 404, arXiv collector redirect
- [x] Custom domain: [threatpulse.dev](https://threatpulse.dev) + api.threatpulse.dev

### In progress / planned 🚧

- [x] Gemini-generated daily insight on the dashboard (cached per day, refreshed after each scrape)
- [ ] Dashboard polish: computed source counts, honest delta arrows, last-scrape timestamp
- [ ] Dedicated agent-threats view with human-readable ASI tag labels
- [ ] Email alerts for new critical threats (Resend)
- [ ] End-to-end Stripe checkout and tier gating
- [ ] Faster scraping cadence (GitHub Actions hourly trigger)
- [ ] Test suite around synthesis and deduplication
- [ ] Structured logging / observability

## Contact

- **Author:** Harry Peter Alesso
- **GitHub:** [@alessoh](https://github.com/alessoh)
- **Issues & feature requests:** [GitHub Issues](https://github.com/alessoh/threatpulse/issues)

## License

[MIT](LICENSE) © 2026 Harry Peter Alesso
