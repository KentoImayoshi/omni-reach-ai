# OmniReach AI

![CI](https://github.com/KentoImayoshi/omni-reach-ai/actions/workflows/ci.yml/badge.svg?branch=main)

[CI] [Django] [DRF] [Celery] [Redis] [Postgres] [Docker]

OmniReach is a multi-tenant marketing analytics backend built with Django, Django REST Framework, Celery, Redis, and Postgres. It ingests integration metrics, aggregates them for fast dashboards, and generates rule-based plus anomaly insights.

## Navigation
1. Overview
2. Highlights
3. Architecture
4. Quickstart (Docker)
5. Configuration
6. Authentication
7. API Surface
8. Webhooks
9. Insights and ML
10. Security Notes
11. Performance Notes
12. Testing
13. CI
14. Roadmap

## Overview
OmniReach focuses on fast analytics dashboards and safe multi-tenant data access. Daily aggregates power summaries, while insights combine rules and anomaly detection for signal-rich reporting.

## Highlights
- [*] Multi-tenant safe APIs (scoped by company)
- [*] JWT authentication with rate limiting
- [*] Encrypted integration tokens at rest
- [*] Cached and aggregated analytics endpoints
- [*] ML-lite anomaly detection (z-score baseline)
- [*] Dockerized local dev setup
- [*] CI (GitHub Actions) running tests

## Architecture
```
[Clients]
   |
   v
[Django API] ---> [Postgres]
   |   \----> [Redis Cache]
   |          [Celery Worker]
   +----> [Webhook Ingress]
```

## Quickstart (Docker)
1. Ensure Docker Desktop is running.
2. Copy `.env.example` to `.env` and adjust values (see Configuration below).
3. Build and run services:

```bash
docker compose up --build
```

4. Run migrations:

```bash
docker compose exec web python manage.py migrate
```

5. (Optional) Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

6. Access the dashboard page:

```text
http://localhost:8000/dashboard/
```

## Configuration
Copy `.env.example` to `.env` in the project root and adjust values. Example values:

```env
# Django
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=omnireach
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis / Celery
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1
CACHE_TTL=300

# JWT
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=1

# Webhooks
META_WEBHOOK_SECRET=change-me

# Security (prod)
SECURE_HSTS_SECONDS=3600
```

Notes:
- If your secret values contain `$`, escape them as `$$` in `.env` so Docker Compose does not treat them as variable references.
- In production, set `DJANGO_DEBUG=false` and configure HTTPS-related settings.
- `.env.example` is safe to commit; keep `.env` local only.

## Authentication
JWT endpoints (rate-limited):
- `POST /api/token/`
- `POST /api/token/refresh/`

## API Surface
| Area | Endpoint | Notes |
| --- | --- | --- |
| Companies | `GET/POST /api/companies/` | CRUD for companies |
| Integrations | `GET/POST /api/integrations/` | Tokens are write-only |
| Raw Metrics | `GET/POST /api/metrics/` | Paginated |
| Metrics Summary | `GET /api/metrics/summary/` | Aggregated totals |
| Metrics Daily | `GET /api/metrics/daily/` | Daily breakdown |
| Metrics Monthly | `GET /api/metrics/monthly/` | Monthly breakdown |
| Dashboard | `GET /api/dashboard/` | Cached dashboard data |
| Insights | `GET /api/insights/` | Paginated + cached |
| Latest Insight | `GET /api/insights/latest/` | Cached |

## Webhooks
Simulated Meta webhook endpoint (rate-limited):
- `POST /api/webhooks/meta/`

The request must include `X-Hub-Signature-256` with an HMAC SHA256 signature computed using `META_WEBHOOK_SECRET`.

## Insights and ML
- Rule-based insights (CPC and CTR checks)
- Anomaly detection using z-score over recent daily aggregates
- All insights are stored in `analytics.Insight` and scoped by company

## Security Notes
- Integration tokens are encrypted at rest and never returned by the API.
- Throttling is enabled for auth and webhooks.
- Set `DJANGO_DEBUG=false` and configure HTTPS-related settings for production.

## Performance Notes
- Daily aggregates are stored in `MetricsAggregate`.
- Dashboard reads from aggregates instead of raw snapshots.
- Insights endpoints are cached with a short TTL.

## Testing
Run tests locally:

```bash
docker compose exec web python manage.py test
```

## CI
GitHub Actions runs migrations and tests on each push or PR.

## Roadmap
- [ ] Add forecasting for weekly trend baselines
- [ ] Add anomaly classification and severity tiers
- [ ] Add advanced filters (campaign, platform, region)
- [ ] Add export jobs (CSV and JSON)


