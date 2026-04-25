# arb_finder — project context for Claude Code

## What this project is

A **read-only, decision-support** football arbitrage detector for regulated betting
operators in Argentina. It scrapes odds from licensed sportsbooks, detects sure-bet
opportunities across operators, and delivers alerts via a Telegram bot. A human places
the bets; this system never automates bet placement, KYC, or CAPTCHA resolution.

Full system design: `Football Arbitration Detector Report.pdf` (repo root).

## Compliance guardrails — non-negotiable

- Only scrape **licensed operator hostnames** keyed by `(operator_brand, jurisdiction, hostname)`.
- Never bypass geo-controls; scrape only anonymous public surfaces or sessions that
  are legitimate for the given jurisdiction.
- Never store KYC data, DNI images, or payment data (Ley 25.326 AR).
- Cookies/tokens go to Vault/KMS only, never plain files.
- No CAPTCHA automation, no automated bet placement.

## Operator scraping strategy (from the PDF)

| Operator | Strategy | Notes |
|---|---|---|
| bplay | HTTP-first | Best MVP target; wide public surface |
| Betsson | HTTP-first | Public pages per jurisdiction |
| Betano | HTTP-first | Public odds visible pre-login |
| Jugadón | HTTP-first | Public sports pages per jurisdiction |
| Easybet Misiones | HTTP-first | Mobile public route |
| Codere | Browser-first | Mobile webapp `m.caba.codere.bet.ar` |
| bet365 | Browser-first | Observe XHR/WS, don't rely on DOM |
| BetWarrior | Browser-first | Playwright + network capture |
| Sportsbet PBA | Browser/session | Session required from day one |

## Tech stack (locked in Phase 0)

| Component | Choice |
|---|---|
| Language | Python 3.12 |
| HTTP collection | httpx + selectolax |
| Browser collection | Playwright (Selenium as fallback) |
| Event bus | Redpanda (Kafka-compatible) |
| Cache / dedupe | Redis |
| Database | PostgreSQL + TimescaleDB |
| ORM / migrations | SQLAlchemy 2.0 async + Alembic |
| API | FastAPI |
| Config | pydantic-settings (.env) |
| Logging | structlog (JSON) |
| Metrics | Prometheus + Grafana |
| Linting | ruff (strict) |
| Types | mypy (strict) |
| Tests | pytest + pytest-asyncio |
| Deploy | Docker + Kubernetes |
| Secrets | Vault/KMS |

## Package layout

```
src/arb_finder/
  api/          FastAPI app — /healthz, /metrics
  collectors/
    http/       httpx + selectolax collectors
    browser/    Playwright collectors (persistent context)
  normalizer/   Canonical fixture + market resolution
  engine/       Arbitrage math, stake calc, risk filters
  notifier/     Telegram bot integration
  shared/       config.py, logging.py, models.py (DB schema)
infra/          prometheus.yml, k8s/ (future)
migrations/     Alembic — env.py, versions/
tests/
```

## Kafka topics

| Topic | Producer | Consumer |
|---|---|---|
| `odds.snapshot.raw` | collectors | normalizer |
| `odds.snapshot.normalized` | normalizer | engine |
| `arb.opportunity.candidate` | engine | engine (requote) |
| `arb.opportunity.confirmed` | engine | notifier |

## Key data model (implement in Phase 1)

Primary table: `odds_snapshot` — immutable, append-only, hypertable on `fetched_at_utc`.

Important fields: `snapshot_id` (UUID), `operator_brand`, `jurisdiction`, `hostname`,
`source_kind` (html_public | browser_dom | browser_xhr | browser_ws),
`requires_session` (bool), `fetched_at_utc`, `canonical_fixture_id`, `sport` (always
"football"), `competition`, `home_team`, `away_team`, `kickoff_utc`, `is_live` (bool),
`market_family` (FT_1X2 | FT_OU | FT_BTTS), `period` (FT | 1H), `line_value` (nullable),
`selection_code` (HOME | DRAW | AWAY | OVER | UNDER), `odds_decimal` (numeric 10,4),
`source_url`, `raw_hash`, `raw_payload` (jsonb ref).

Supporting tables: `arb_opportunity`, `arb_leg`, `notification_delivery`, raw audit store.

## Arbitrage math

```
S = Σ (1 / oᵢ)          # sum of implied probabilities
arb exists when S < 1
P = T / S                # common payout for total stake T
sᵢ = P / oᵢ             # stake per outcome
margin % = (1/S - 1) × 100
```

Operational threshold: `S < 0.99` (buffer for rounding + latency). Always store both
theoretical margin and realizable margin (post-rounding) separately.

## Arbitrage engine algorithm

1. Resolve canonical fixture + market.
2. Select best available odds per outcome across eligible operators.
3. Compute `S`; if below threshold → calculate stakes, apply min/max limits.
4. **Requote immediately** (re-fetch only the involved legs).
5. Only if edge survives requote → promote to `confirmed` → emit to Kafka → Telegram.

Extra filters in production:
- **Stale-state filter**: for live, score/clock/cards must match across books.
- **Rounding/stake-step filter**: a book requiring ARS 10 multiples may kill the edge.

## Telegram alert lifecycle

States: `new` → `improved` → `stale` → `expired`.
Send once (sendMessage), then edit (editMessageText) — never spam.
Dedupe key: `hash(fixture + market + selected_books + selected_odds)`.

## Polling cadence

| Mode | Interval |
|---|---|
| Fixture discovery | 2–5 min |
| Pre-match active | 15–30 s |
| Pre-match T-15 min | 5–10 s (priority fixtures only) |
| Live (shortlisted) | 2–5 s |

## Development phases

- [x] **Phase 0** — Repo layout, docker-compose stack, FastAPI skeleton, Alembic skeleton,
  structlog, Prometheus, ruff/mypy/pytest. *(3 smoke tests passing)*
- [ ] **Phase 1** — DB schema: `odds_snapshot`, `arb_opportunity`, `arb_leg`,
  `notification_delivery`. Timescale hypertable. Canonical alias dictionaries.
- [ ] **Phase 2** — First HTTP collector: **bplay** pre-match FT_1X2. Token bucket,
  jitter, backoff. Raw HTML audit. Kafka producer.
- [ ] **Phase 3** — Normalizer: fixture resolver + market resolver. Kafka consumer/producer.
- [ ] **Phase 4** — Arbitrage engine: best-price selector, S calculator, stake calc,
  requote loop, risk filters.
- [ ] **Phase 5** — Add Betsson + Betano HTTP collectors. First real arb opportunities.
- [ ] **Phase 6** — Telegram notifier: sendMessage, editMessageText, dedup, 4-state lifecycle.
- [ ] **Phase 7** — Browser collectors: Codere, bet365, BetWarrior, Sportsbet PBA (Playwright).
- [ ] **Phase 8** — Layered polling scheduler.
- [ ] **Phase 9** — Observability: Grafana dashboards, Timescale continuous aggregates.
- [ ] **Phase 10** — Live betting (after compliance review).

## Local dev quickstart

```bash
cp .env.example .env          # fill in values
make install-dev              # install + pre-commit hooks
make up                       # start postgres, redis, redpanda, prometheus, grafana
make migrate                  # apply alembic migrations
make api                      # FastAPI on http://localhost:8000
make test                     # pytest
make lint                     # ruff
make typecheck                # mypy
```

## Current branch

`claude/detect-pdf-files-FzXwY`

