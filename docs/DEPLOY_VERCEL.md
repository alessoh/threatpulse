# Deploying ThreatPulse entirely on Vercel

This guide takes ThreatPulse from "runs on my laptop" to fully hosted on
Vercel: the Next.js frontend and the FastAPI backend each run as a Vercel
project, Postgres comes from the Vercel Marketplace, and the scrapers run on
Vercel Cron. Follow the steps in order; each one tells you exactly where to
click and what to paste.

## What you need before starting

- Your GitHub account with this repository pushed to it
- A Vercel account (vercel.com, sign in with GitHub) — the frontend project
  you already have
- An Anthropic API key (console.anthropic.com → API Keys)
- Optional, for payments and email: Stripe and Resend accounts

You will also need a terminal on your laptop once, to run database
migrations.

---

## Step 1: Create the Postgres database

1. Go to **vercel.com/dashboard** and open the **Storage** tab.
2. Click **Create Database** and choose **Neon** (Postgres). Accept the free
   plan defaults and name it `threatpulse`.
3. When it finishes, open the database page and find **Connection strings**.
   You will see two kinds:
   - a **pooled** connection string (host contains `-pooler`) — this is the
     one the backend will use;
   - a **direct** connection string — this is the one migrations will use.
4. Copy both somewhere safe.

## Step 2: Run migrations and seed data (from your laptop, once)

**Windows (PowerShell)** — from the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Use the DIRECT (non-pooler) connection string here:
$env:DATABASE_URL = "postgresql://...direct connection string..."
# Generate a secret. Keep this value! You reuse it in Step 3.
$env:JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
echo $env:JWT_SECRET

alembic upgrade head
python -m app.scrapers.run --seed
```

If PowerShell refuses to run `Activate.ps1` ("running scripts is disabled"),
either run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use
Command Prompt (cmd) instead:

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt

set DATABASE_URL=postgresql://...direct connection string...
python -c "import secrets; print(secrets.token_hex(32))"
rem Copy the printed value, then:
set JWT_SECRET=paste-the-printed-value-here

alembic upgrade head
python -m app.scrapers.run --seed
```

**Mac/Linux (bash)** — from the repository root:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Use the DIRECT (non-pooler) connection string here:
export DATABASE_URL="postgresql://...direct connection string..."
export JWT_SECRET="$(openssl rand -hex 32)"   # keep this value! You reuse it in Step 3

alembic upgrade head
python -m app.scrapers.run --seed
```

You should see `Seeded 5 conventional and 5 agent threats.` Save the
JWT_SECRET value you generated — the deployed backend must use the same one
only if you want existing logins to survive; otherwise any strong value
works.

## Step 3: Deploy the backend as a new Vercel project

1. Go to **vercel.com/new** and import the same GitHub repository again
   (yes, a second project from the same repo).
2. On the configure screen:
   - **Project Name**: `threatpulse-api`
   - **Root Directory**: click **Edit** and select `backend`
   - **Framework Preset**: leave as **Other**
3. Open **Environment Variables** on that same screen and add:

   | Name | Value |
   |---|---|
   | `DATABASE_URL` | the **pooled** connection string from Step 1 |
   | `JWT_SECRET` | the value from Step 2 (or generate a new one, see below) |
   | `CRON_SECRET` | generate another one the same way |
   | `ANTHROPIC_API_KEY` | your key from console.anthropic.com |
   | `GEMINI_API_KEY` | (optional) from aistudio.google.com — enables the Gemini daily insight |
   | `FRONTEND_URL` | your frontend URL, e.g. `https://threatpulse.dev` |
   | `CORS_ORIGINS` | same value as `FRONTEND_URL` |
   | `RESEND_API_KEY` | (optional) from resend.com |
   | `EMAIL_FROM` | (optional) a verified sender, e.g. `alerts@yourdomain.com` |
   | `STRIPE_SECRET_KEY` | (optional) from dashboard.stripe.com |
   | `STRIPE_WEBHOOK_SECRET` | (optional) after Step 6 |
   | `STRIPE_PRICE_PRO` | (optional) Stripe Price ID |
   | `STRIPE_PRICE_ENTERPRISE` | (optional) Stripe Price ID |

   To generate a secret on Windows: `python -c "import secrets; print(secrets.token_hex(32))"`
   (on Mac/Linux, `openssl rand -hex 32` also works).

4. Click **Deploy**. When it finishes, note the URL, e.g.
   `https://api.threatpulse.dev`.
5. Test it: open `https://api.threatpulse.dev/health` in your browser.
   You should see `{"status":"ok","service":"threatpulse-api"}`.

`CRON_SECRET` matters: Vercel automatically sends it as a Bearer token when
it invokes the cron routes, and the routes reject any request without it.

## Step 4: Point the frontend at the new backend

1. Open your **existing frontend project** in the Vercel dashboard.
2. Go to **Settings → Environment Variables** and set:
   - `NEXT_PUBLIC_API_URL` = `https://api.threatpulse.dev`
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` = your `pk_...` key (optional)
3. Go to **Deployments** and click **Redeploy** on the latest deployment
   (env vars are baked in at build time for `NEXT_PUBLIC_*`).
4. Open the site: the dashboard should show the seeded threats.

## Step 5: Confirm the cron jobs

The backend's `vercel.json` registers two cron jobs (visible under the
backend project's **Settings → Cron Jobs** after deploying):

- `/api/cron/scrape-all` — daily at 06:00 UTC: runs every collector (CISA
  KEV, NVD, security RSS feeds, and the agent-threat collectors) with small
  batch caps, deduplicating before any Claude call.
- `/api/cron/weekly-digest` — Mondays at 09:00 UTC: AI-written digest email
  to Pro/Enterprise subscribers (idempotent; safe to re-run).

To trigger a scrape immediately instead of waiting for the schedule —
Windows (PowerShell; note the `.exe`, which bypasses PowerShell's built-in
`curl` alias):

```powershell
curl.exe -H "Authorization: Bearer YOUR_CRON_SECRET" https://api.threatpulse.dev/api/cron/scrape-all
```

Or with a native PowerShell command:

```powershell
Invoke-RestMethod -Uri "https://api.threatpulse.dev/api/cron/scrape-all" -Headers @{ Authorization = "Bearer YOUR_CRON_SECRET" }
```

If `curl.exe` fails with `schannel ... CRYPT_E_NO_REVOCATION_CHECK`, your
network is blocking Windows' certificate-revocation lookup. Use the
`Invoke-RestMethod` version above, or add `--ssl-no-revoke` after
`curl.exe` (the certificate itself is still verified).

Mac/Linux:

```bash
curl -H "Authorization: Bearer YOUR_CRON_SECRET" \
  https://api.threatpulse.dev/api/cron/scrape-all
```

**Plan note:** the Hobby plan allows limited, roughly daily cron jobs. If
you upgrade to Vercel Pro you can add more schedules to
`backend/vercel.json` — e.g. run `/api/cron/scrape-agents` every 6 hours —
and redeploy. Alternatively, a free GitHub Actions scheduled workflow can
curl the endpoints hourly using the same header.

## Step 6: Stripe webhook (only if you use payments)

1. Go to **dashboard.stripe.com → Developers → Webhooks → Add endpoint**.
2. URL: `https://api.threatpulse.dev/api/webhook/stripe`
3. Events: `checkout.session.completed`,
   `customer.subscription.updated`, `customer.subscription.deleted`.
4. Copy the signing secret into the backend project's
   `STRIPE_WEBHOOK_SECRET` env var and redeploy the backend.

## Step 7: Final checklist

- [ ] `https://api.threatpulse.dev/health` returns ok
- [ ] Frontend dashboard shows the 10 seeded threats
- [ ] You can register and log in
- [ ] `curl` to `/api/cron/scrape-all` with the secret returns a JSON report
- [ ] (Pro test) opening a threat's playbook page generates a playbook —
      the first load takes ~30 seconds, subsequent loads are instant

## Architecture notes (what changed to make this work)

- **Serverless entrypoint** — `backend/api/index.py` + `backend/vercel.json`
  route every request into the FastAPI app; `maxDuration` is 300s so Claude
  calls and scrape batches fit.
- **Database connections** — the engine uses `NullPool`, so always point
  `DATABASE_URL` at the pooled connection string in production.
- **No always-on scheduler** — Vercel Cron replaces APScheduler in
  production. `python -m app.scrapers.run --watch` still works for local
  Docker development.
- **Serverless-safe state** — the auth rate limiter lives in the
  `auth_attempts` table; alert and digest sends are recorded in `alert_logs`
  and checked before sending, so retries never double-email.
- **Cost control** — collectors check the database (by CVE ID / source URL)
  *before* calling Claude, so a scrape cycle only pays for genuinely new
  items.
- **Playbooks** — generated on demand on first request per threat and cached
  in the `playbooks` table (one per threat, enforced by a unique index).

Local development is unchanged: `docker-compose up` still runs the whole
stack on your laptop.
