# ThreatPulse

**AI-Powered Cyber Threat Intelligence for small and mid-sized organizations.**

ThreatPulse pulls threat data from CISA, NVD, and major security feeds, has Claude AI write it up in plain English, and delivers it to subscribers through a dashboard, library, AI chat advisor, and email alerts. Free, $39/mo Pro, and $199/mo Enterprise tiers.

---

## Table of contents

1. [What you need before starting](#1-what-you-need-before-starting)
2. [Load this project into Antigravity IDE](#2-load-this-project-into-antigravity-ide)
3. [Create a GitHub repository](#3-create-a-github-repository)
4. [Sign up for the three required services](#4-sign-up-for-the-three-required-services)
5. [Fill in your `.env` file](#5-fill-in-your-env-file)
6. [Run ThreatPulse on your computer (Docker — easiest)](#6-run-threatpulse-on-your-computer-docker--easiest)
7. [Or run without Docker (manual)](#7-or-run-without-docker-manual)
8. [Test that everything works](#8-test-that-everything-works)
9. [Deploy to production](#9-deploy-to-production)
10. [Schedule the weekly email digest](#10-schedule-the-weekly-email-digest)
11. [Troubleshooting](#11-troubleshooting)
12. [Project layout](#12-project-layout)

---

## 1. What you need before starting

A laptop or desktop with internet access, plus these free tools installed:

| Tool | What it is | Where to get it |
|---|---|---|
| **Git** | Version control. Required to push code to GitHub. | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **Docker Desktop** | Runs the app in a sealed container. The fastest way to start. | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| **Antigravity IDE** | The editor you're using to read this. | (you already have it) |
| **A web browser** | For signing up at the service websites. | (you already have one) |

You will also create accounts at four free services later in this guide:
- **GitHub** — to host your code
- **Anthropic** — provides the Claude AI
- **Resend** — sends emails
- **Stripe** — takes credit card payments

You do not need a credit card to test ThreatPulse. Stripe has a "test mode" with fake cards. Anthropic and Resend both have free tiers.

---

## 2. Load this project into Antigravity IDE

1. Unzip `threatpulse.zip` somewhere easy to find, like your `Documents` folder. You should now have a folder called `threatpulse`.
2. Open Antigravity IDE.
3. Click **File → Open Folder** (or the equivalent in your IDE).
4. Pick the `threatpulse` folder you just unzipped. Click **Open**.
5. The file tree on the left should now show folders like `backend/`, `frontend/`, `scripts/`, and files like `README.md`. You're in.

---

## 3. Create a GitHub repository

You'll push your copy of ThreatPulse to a private GitHub repository so you can deploy it later and keep a backup.

### 3.1 Create the GitHub account (skip if you have one)

1. Go to [github.com](https://github.com) and click **Sign up**.
2. Pick a username, email, and password. Verify your email.

### 3.2 Create the empty repository

1. In the top-right of GitHub, click the **+** icon → **New repository**.
2. **Repository name:** `threatpulse`
3. **Description:** `AI-powered cyber threat intelligence platform` (optional)
4. **Visibility:** choose **Private** (recommended).
5. **Do NOT** check "Add a README", "Add .gitignore", or "Choose a license" — your local copy already has those.
6. Click **Create repository**.
7. The next page shows a URL like `https://github.com/YOUR-USERNAME/threatpulse.git`. **Copy that URL** — you'll paste it in the next step.

### 3.3 Push your local copy to GitHub

Open a terminal inside Antigravity IDE (usually **View → Terminal** or **Terminal → New Terminal**). Make sure the terminal is in the `threatpulse` folder. Then run these commands one at a time:

```bash
git init
git add .
git commit -m "Initial commit of ThreatPulse"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/threatpulse.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username. You may be asked to log in to GitHub — follow the prompts. When `git push` finishes without errors, refresh your GitHub repo page in the browser. You should see all the files.

---

## 4. Sign up for the three required services

ThreatPulse needs three external services to be fully functional. You can skip any of these and the app will still run, but the matching feature won't work.

### 4.1 Anthropic (Claude AI) — REQUIRED for AI features

1. Go to [console.anthropic.com](https://console.anthropic.com) and sign up.
2. Add at least $5 of credit (you'll pay as you use it; small testing only costs cents).
3. In the left menu, click **API Keys** → **Create Key**.
4. Name it `threatpulse`. Copy the key (starts with `sk-ant-...`). **You won't see it again** — paste it somewhere safe for now.

### 4.2 Resend (email) — REQUIRED for email alerts

1. Go to [resend.com](https://resend.com) and sign up. Free tier sends 3,000 emails/month.
2. Verify your account email when they send you a confirmation link.
3. In Resend, go to **Domains** → **Add Domain**. Enter a domain you own (e.g., `yourcompany.com`).
4. Resend will show a list of DNS records to add. Log in to wherever you registered your domain (GoDaddy, Namecheap, Cloudflare, etc.) and add those records exactly as shown.
5. Wait 5–60 minutes, then click **Verify** in Resend. You need green checkmarks before email will send.
6. **Don't own a domain?** Resend lets you send from `onboarding@resend.dev` while testing — skip steps 3–5 and use that as your `EMAIL_FROM` later.
7. Go to **API Keys** → **Create API Key**. Name it `threatpulse`. Choose **Sending access**. Copy the key (starts with `re_...`).

### 4.3 Stripe (payments) — REQUIRED for paid subscriptions

1. Go to [stripe.com](https://stripe.com) and sign up.
2. **Stay in Test Mode** while you're getting started — there's a toggle in the top-right of the dashboard. Test mode uses fake cards and costs nothing.
3. Click **Developers → API Keys**. You'll see two keys:
   - A **Publishable key** that starts with `pk_test_...`
   - A **Secret key** that starts with `sk_test_...` (click reveal)
4. Copy both. Paste them somewhere safe.
5. Now create the Pro and Enterprise products. The project includes a script that does this for you. Open a terminal in your `threatpulse` folder and run:
   ```bash
   cd backend
   pip install stripe
   STRIPE_SECRET_KEY=sk_test_paste_yours_here python ../scripts/setup_stripe.py
   ```
6. The script will print two lines like:
   ```
   STRIPE_PRICE_PRO=price_1AbCd...
   STRIPE_PRICE_ENTERPRISE=price_1XyZw...
   ```
   Copy both. You'll paste them into `.env` next.

> **Webhook secret comes later** — you'll set that up after the app is running, in [section 8.4](#84-set-up-the-stripe-webhook).

---

## 5. Fill in your `.env` file

The `.env` file holds every secret key. It's the heart of your configuration.

### 5.1 Copy the template

In a terminal, in the `threatpulse` folder:

```bash
cp .env.example .env
```

(On Windows PowerShell: `copy .env.example .env`)

### 5.2 Generate a JWT secret

JWT_SECRET is the secret key that signs login tokens. The app **will refuse to start** if this is empty or set to the default — that's intentional, to prevent accidentally deploying with an unsafe value.

In a terminal:

```bash
openssl rand -hex 32
```

This prints a long random string. Copy it.

(No `openssl`? On Windows you can also use Git Bash, or just go to [random.org/strings](https://www.random.org/strings/?num=1&len=64&digits=on&upperalpha=on&loweralpha=on&unique=on&format=html&rnd=new) and grab any 64-character hex string.)

### 5.3 Fill in the values

Open `.env` in Antigravity IDE and paste each value into the matching slot:

```env
# Database — leave as is for local Docker; replace for production
DATABASE_URL=postgresql://threatpulse:threatpulse_dev@localhost:5432/threatpulse

# Auth — paste your random hex string here
JWT_SECRET=paste-your-openssl-output-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Anthropic — your Claude API key
ANTHROPIC_API_KEY=sk-ant-paste-here

# Stripe — your test keys + the price IDs from step 4.3
STRIPE_SECRET_KEY=sk_test_paste-here
STRIPE_WEBHOOK_SECRET=                       # Leave blank for now
STRIPE_PRICE_PRO=price_paste-here
STRIPE_PRICE_ENTERPRISE=price_paste-here

# Resend
RESEND_API_KEY=re_paste-here
EMAIL_FROM=alerts@yourdomain.com             # Use onboarding@resend.dev if no verified domain

# URLs
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000

# Frontend (Next.js reads NEXT_PUBLIC_* values)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_paste-here
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_paste-here              # Same value as STRIPE_PRICE_PRO
NEXT_PUBLIC_STRIPE_PRICE_ENTERPRISE=price_paste-here       # Same value as STRIPE_PRICE_ENTERPRISE

# Scraper schedule
SCRAPE_CISA_INTERVAL_HOURS=1
SCRAPE_NVD_INTERVAL_HOURS=4
SCRAPE_VENDOR_INTERVAL_HOURS=12
```

Save the file.

> **Important:** never commit `.env` to GitHub. The included `.gitignore` already excludes it, but if you accidentally `git add .env`, undo with `git rm --cached .env`.

---

## 6. Run ThreatPulse on your computer (Docker — easiest)

### 6.1 Make sure Docker Desktop is running

Open Docker Desktop. Wait until the whale icon at the top of the screen says "Docker is running".

### 6.2 Start everything

In a terminal in the `threatpulse` folder:

```bash
docker-compose up --build
```

The first time, this downloads several gigabytes (Postgres, Python, Node.js images) and takes 5–10 minutes. You'll see a lot of build output. When it's done you'll see lines like:

```
backend_1   |  INFO:     Uvicorn running on http://0.0.0.0:8000
frontend_1  |  ▲ Next.js 14.2.15
frontend_1  |  - Local:        http://localhost:3000
```

Leave that terminal running. Open a **second** terminal for the next steps.

### 6.3 Seed the database with sample threats

In your second terminal:

```bash
docker-compose exec backend python -m app.scrapers.run --seed
```

This adds 5 demo threats so the dashboard isn't empty. You should see `Seeded 5 threats.`.

### 6.4 Open the app

In your browser, go to **[http://localhost:3000](http://localhost:3000)**. You should see the dashboard with sample threats. Click **Sign In** at the top right, switch to **Sign Up**, and create a test account.

### 6.5 Stopping the app

Back in the first terminal, press **Ctrl+C**. To start it again later, just run `docker-compose up` (no `--build` needed unless you change code).

---

## 7. Or run without Docker (manual)

Use this route if you don't want to install Docker. You'll need:
- **Python 3.11** ([python.org](https://www.python.org/downloads))
- **Node.js 20** ([nodejs.org](https://nodejs.org))
- **PostgreSQL 16** ([postgresql.org/download](https://www.postgresql.org/download))

### 7.1 Create the database

After installing PostgreSQL, run in a terminal:

```bash
createdb threatpulse
```

Then update `.env`:
```env
DATABASE_URL=postgresql://YOUR_PG_USER:YOUR_PG_PASSWORD@localhost:5432/threatpulse
```

### 7.2 Start the backend

In one terminal:

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scrapers.run --seed
uvicorn app.main:app --reload --port 8000
```

### 7.3 Start the frontend

In a **second** terminal:

```bash
cd frontend
npm install
npm run dev
```

### 7.4 Open the app

Browse to **[http://localhost:3000](http://localhost:3000)**.

---

## 8. Test that everything works

### 8.1 Test signup and login

1. Go to [http://localhost:3000](http://localhost:3000).
2. Click **Sign In** → **Sign Up**.
3. Use any email and a password of 8+ characters.
4. After signup, the top-right shows your tier as `FREE`.

### 8.2 Test the dashboard

You should see threat counts, the trending threats list, and an AI insight panel.

### 8.3 Test email (optional but recommended)

Open a terminal in the `threatpulse` folder:

```bash
docker-compose exec backend python -c "
from app.services.email_service import send_threat_alert
from app.models.user import User
u = User(email='YOUR-REAL-EMAIL@example.com', full_name='Test')
send_threat_alert(u, 'Test Threat', 'critical', 'This is a test email from ThreatPulse.')
print('Email sent.')
"
```

(If running manually without Docker: `cd backend && source venv/bin/activate` then run the python code without the `docker-compose exec backend` prefix.)

If it lands in your inbox, email works. If you get an error, double-check your `RESEND_API_KEY` and `EMAIL_FROM` in `.env`.

### 8.4 Set up the Stripe webhook

For the `Subscribe` button to actually upgrade users after they pay, Stripe needs to send notifications to your backend. While running locally, use the **Stripe CLI**:

1. Install Stripe CLI from [stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli).
   - macOS: `brew install stripe/stripe-cli/stripe`
   - Windows: download the installer from the link above
   - Linux: see the link
2. Log in: `stripe login` (opens your browser to confirm).
3. In a third terminal, run:
   ```bash
   stripe listen --forward-to localhost:8000/api/webhook/stripe
   ```
4. The CLI prints a line like `Your webhook signing secret is whsec_abc123...`. **Copy that value**.
5. Paste it into `.env` as `STRIPE_WEBHOOK_SECRET=whsec_abc123...`.
6. Restart the backend (in Docker: `docker-compose restart backend`; manually: Ctrl+C, then `uvicorn app.main:app --reload --port 8000`).

### 8.5 Test the payment flow

1. While logged in, click **Pricing** → **Start Pro Trial**.
2. You'll land on Stripe's checkout page. Use test card:
   - **Card number:** `4242 4242 4242 4242`
   - **Expiry:** any future date (e.g., `12/30`)
   - **CVC:** any 3 digits (e.g., `123`)
   - **ZIP:** any (e.g., `10001`)
3. Click **Subscribe**. You should redirect back to the dashboard.
4. Refresh the page — your tier badge should now say `PRO`.
5. Visit a playbook page — the remediation steps should no longer be blurred out.

If the tier doesn't update, check the **Stripe CLI** terminal for errors. Most common: webhook secret mismatch.

---

## 9. Deploy to production

These are the recommended free-tier services. Total cost: about **$5–25/month** depending on usage.

| Layer | Service | Free tier | Why |
|---|---|---|---|
| Database | [Supabase](https://supabase.com) | 500 MB free | Managed Postgres, easy URL |
| Backend | [Railway](https://railway.app) | $5/mo Hobby | Auto-deploys from GitHub, supports Dockerfile |
| Frontend | [Vercel](https://vercel.com) | Free | Built for Next.js |

### 9.1 Database — Supabase

1. Sign up at [supabase.com](https://supabase.com).
2. Click **New Project**. Name it `threatpulse`. Pick a region close to you. Set a strong database password and **save it somewhere safe**.
3. Wait 2 minutes while the database provisions.
4. In your project, click **Settings** (gear icon) → **Database** → **Connection string** → **URI**.
5. Copy the URI (it looks like `postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres`). Replace `[YOUR-PASSWORD]` with the password you just set.

### 9.2 Backend — Railway

1. Sign up at [railway.app](https://railway.app) — sign in with GitHub for easiest setup.
2. Click **New Project** → **Deploy from GitHub Repo** → pick your `threatpulse` repo.
3. Railway will scan and find the Dockerfile. It will ask which folder — pick `backend`.
4. Click **Variables** in your service and add every variable from your `.env` file:
   - `DATABASE_URL` → use the Supabase URL from step 9.1
   - `JWT_SECRET`, `ANTHROPIC_API_KEY`, `STRIPE_SECRET_KEY`, all the others
   - `FRONTEND_URL` → leave as `http://localhost:3000` for now; we'll update after Vercel
   - `CORS_ORIGINS` → same; update after Vercel
5. Click **Settings** → **Networking** → **Generate Domain**. Copy the URL it gives you (like `threatpulse-backend.up.railway.app`).
6. Open Railway's shell (top-right **⋯** menu → **Open Shell**) and run:
   ```bash
   alembic upgrade head
   python -m app.scrapers.run --seed
   ```

### 9.3 Add a second Railway service for the scraper

1. In the same Railway project, click **New** → **Empty Service** → connect to the same GitHub repo, `backend` folder.
2. Copy all the same variables as the backend service.
3. **Settings** → **Start Command** → set it to: `python -m app.scrapers.run --watch`
4. Deploy. This service runs forever, scraping CISA hourly, NVD every 4h, RSS every 12h.

### 9.4 Frontend — Vercel

1. Sign up at [vercel.com](https://vercel.com) with GitHub.
2. **Add New Project** → import your `threatpulse` repo.
3. Set **Root Directory** to `frontend`.
4. **Environment Variables** — add:
   - `NEXT_PUBLIC_API_URL` → `https://YOUR-RAILWAY-URL` (from step 9.2)
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` → your `pk_test_...` (or `pk_live_...` when going live)
   - `NEXT_PUBLIC_STRIPE_PRICE_PRO` → your Pro price ID
   - `NEXT_PUBLIC_STRIPE_PRICE_ENTERPRISE` → your Enterprise price ID
5. Click **Deploy**. Wait 2 minutes.
6. Vercel gives you a URL like `threatpulse-abc123.vercel.app`. **Copy it.**

### 9.5 Wire the URLs together

Now go back to Railway → backend service → **Variables** and update:

```
FRONTEND_URL=https://threatpulse-abc123.vercel.app
CORS_ORIGINS=https://threatpulse-abc123.vercel.app
```

Click **Deploy** to apply. Do the same for the scraper service if needed.

### 9.6 Production Stripe webhook

1. In Stripe dashboard, switch off **Test mode** (top-right toggle) when you're ready to charge real money. Get your live `sk_live_...` and `pk_live_...` keys.
2. Go to **Developers → Webhooks → Add endpoint**.
3. **URL:** `https://YOUR-RAILWAY-URL/api/webhook/stripe`
4. **Events:** check `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`.
5. Click **Add endpoint**. Copy the **Signing secret** (starts with `whsec_...`).
6. In Railway, update `STRIPE_WEBHOOK_SECRET` to that value.

### 9.7 (Optional) Custom domain

1. In Vercel: **Settings → Domains → Add** your domain (e.g., `threatpulse.io`).
2. Add the DNS records Vercel shows you at your domain registrar.
3. Update Railway's `FRONTEND_URL` and `CORS_ORIGINS` to your custom domain.

---

## 10. Schedule the weekly email digest

The digest script exists at `scripts/weekly_digest.py` but doesn't run on a schedule by default.

**Easy option — Railway cron:**
1. Railway dashboard → your backend service → **Settings** → **Cron Schedule**.
2. Cron expression: `0 13 * * 1` (Mondays at 1pm UTC = 9am Eastern).
3. Command: `python -m scripts.weekly_digest`
4. Save.

**Alternative — your own server:**
```bash
crontab -e
# Add this line, replacing /path/to/threatpulse:
0 13 * * 1 cd /path/to/threatpulse && python -m scripts.weekly_digest
```

---

## 11. Troubleshooting

**`docker-compose up` fails with "JWT_SECRET is missing or set to the default value"**
You forgot to fill `JWT_SECRET` in `.env`. See [step 5.2](#52-generate-a-jwt-secret).

**Email test returns "Invalid API key"**
Re-check `RESEND_API_KEY` in `.env`. Be sure there are no quotes or trailing spaces. If you used a domain you didn't fully verify, set `EMAIL_FROM=onboarding@resend.dev`.

**Stripe checkout button does nothing**
Check the browser dev console (F12). If it says `priceId` is empty, you forgot to set `NEXT_PUBLIC_STRIPE_PRICE_PRO` in `.env` and restart the frontend.

**After paying with the test card, my tier stays "free"**
The webhook isn't reaching the backend. Locally: make sure `stripe listen` is running and `STRIPE_WEBHOOK_SECRET` matches its output. In production: check Stripe Dashboard → Developers → Webhooks → click your endpoint → see the **Recent attempts** log; failed attempts will show why.

**Dashboard is empty / "Loading threats..." never finishes**
Run the seed command:
```bash
docker-compose exec backend python -m app.scrapers.run --seed
```
Or wait for the scraper service to pick up real threats (first run may take 5–10 minutes).

**`alembic upgrade head` fails with "relation already exists"**
You've previously created tables. Reset:
```bash
docker-compose down -v        # WARNING: deletes the database
docker-compose up --build
```

**CORS errors in the browser console**
Your frontend URL isn't in the backend's `CORS_ORIGINS` setting. Update it in `.env` (or in Railway's variables) and restart the backend.

**Free-tier user can't use the AI advisor — "Free tier limit reached"**
That's by design — 3 questions per day for free, then upgrade to Pro. Your test account hit the limit. Either log in as a Pro user, or wait until tomorrow, or change `FREE_TIER_DAILY_LIMIT` in `backend/app/api/routes.py`.

---

## 12. Project layout

```
threatpulse/
├── backend/                          Python FastAPI server
│   ├── app/
│   │   ├── api/routes.py             All HTTP endpoints
│   │   ├── core/
│   │   │   ├── auth.py               JWT login + tier guards
│   │   │   ├── config.py             Settings, env loading
│   │   │   └── database.py           SQLAlchemy setup
│   │   ├── models/user.py            Database tables
│   │   ├── schemas/schemas.py        Request/response shapes
│   │   ├── services/
│   │   │   ├── ai_service.py         Talks to Claude
│   │   │   ├── email_service.py      Talks to Resend
│   │   │   └── stripe_service.py     Talks to Stripe
│   │   ├── scrapers/
│   │   │   ├── collectors.py         Scrapes CISA, NVD, RSS feeds
│   │   │   └── run.py                Scheduler + seed data
│   │   └── main.py                   FastAPI app entry
│   ├── alembic/                      Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                         Next.js 14 web app
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/            Main dashboard
│   │   │   ├── library/              Searchable threat list
│   │   │   ├── playbook/[slug]/      Threat detail + AI advisor
│   │   │   ├── pricing/              Subscription tiers
│   │   │   └── layout.tsx
│   │   ├── components/ui/Nav.tsx     Top nav + sign-in modal
│   │   ├── lib/
│   │   │   ├── api.ts                Calls the backend
│   │   │   └── auth.tsx              Login state
│   │   └── types/index.ts            TypeScript types
│   ├── Dockerfile
│   └── package.json
├── scripts/
│   ├── deploy.sh                     Step-by-step deployment notes
│   ├── setup_stripe.py               Creates Stripe products
│   └── weekly_digest.py              Sends Monday digest emails
├── docker-compose.yml                Local dev stack
├── .env.example                      Template for your secrets
└── README.md                         You are here
```

---

## License

MIT. See `LICENSE`.

## Support

This project is provided as-is. For issues or questions, open an issue in the GitHub repository you created in section 3.
