# ThreatPulse — AI-Powered Cyber Threat Intelligence Platform

Full-stack production application for aggregating, synthesizing, and delivering cyber threat intelligence to small and mid-sized organizations.

## Architecture

```
threatpulse/
├── backend/          # Python FastAPI server
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── core/     # Config, auth, database
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   ├── services/ # Business logic (stripe, email, AI)
│   │   └── scrapers/ # Threat data collection pipeline
│   ├── alembic/      # Database migrations
│   └── requirements.txt
├── frontend/         # Next.js 14 React application
│   ├── src/
│   │   ├── app/      # Pages and API routes
│   │   ├── components/
│   │   ├── lib/      # Utilities and API client
│   │   └── types/    # TypeScript definitions
│   └── package.json
├── scripts/          # Utility scripts
├── docker-compose.yml
└── .env.example
```

## Tech Stack

- **Frontend:** Next.js 14, React, Tailwind CSS, TypeScript
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL (Supabase or Neon free tier)
- **AI:** Anthropic Claude API (Sonnet for synthesis, Opus for complex analysis)
- **Payments:** Stripe (subscriptions + webhooks)
- **Email:** Resend (transactional + digest emails)
- **Scraping:** CISA, NVD, MITRE ATT&CK, vendor advisories, open feeds
- **Deployment:** Vercel (frontend) + Railway (backend) + Supabase (database)

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/threatpulse.git
cd threatpulse
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start with Docker (recommended)

```bash
docker-compose up --build
```

Frontend: http://localhost:3000
Backend: http://localhost:8000
API docs: http://localhost:8000/docs

### 3. Or start manually

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### 4. Seed the database with initial threat data

```bash
cd backend
python -m app.scrapers.run --seed
```

### 5. Run the scraping pipeline

```bash
python -m app.scrapers.run          # One-time scrape
python -m app.scrapers.run --watch  # Continuous (hourly CISA, daily others)
```

## Environment Variables

See `.env.example` for all required variables. At minimum you need:

- `DATABASE_URL` — PostgreSQL connection string
- `ANTHROPIC_API_KEY` — For AI threat synthesis
- `STRIPE_SECRET_KEY` — For payment processing
- `STRIPE_WEBHOOK_SECRET` — For subscription events
- `RESEND_API_KEY` — For email notifications
- `JWT_SECRET` — For authentication tokens

## Subscription Tiers

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | Dashboard, trending threats, executive summaries |
| Professional | $39/mo | Full profiles, IOCs, playbooks, AI advisor, email alerts |
| Enterprise | $199/mo | API access (STIX), SIEM guides, custom reports, 25 seats |

## License

Proprietary. All rights reserved.
