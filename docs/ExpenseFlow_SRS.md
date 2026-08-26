# Software Requirements Specification (SRS)
## ExpenseFlow — Personal Expense & Budget Tracker

**Document Version:** 1.0
**Status:** Draft
**Based on:** ExpenseFlow PRD v1.0 (Merged)
**Prepared for:** Solo/small-team development, local-first → cloud deployment (Supabase + Vercel + Render)

---

## 1. Introduction

### 1.1 Purpose
This SRS translates the ExpenseFlow PRD into precise, implementable technical requirements across frontend, backend, database, API, and deployment layers, so the application can be built correctly in a single, coherent pass with minimal rework between local development and cloud production.

### 1.2 Scope
ExpenseFlow is a responsive web application for personal expense tracking, dynamic category management, budget goal tracking with alerts, and spending analytics — built as a REST API–driven full-stack app (Next.js frontend, FastAPI backend, PostgreSQL database).

### 1.3 Definitions & Abbreviations
| Term | Meaning |
|---|---|
| SRS | Software Requirements Specification |
| ORM | Object-Relational Mapper (SQLAlchemy) |
| CRUD | Create, Read, Update, Delete |
| FE / BE | Frontend / Backend |
| DTO | Data Transfer Object (Pydantic schema) |

### 1.4 References
- ExpenseFlow PRD v1.0 (Merged)
- FastAPI, Next.js, SQLAlchemy, Alembic official documentation
- Supabase, Vercel, Render platform documentation

---

## 2. Overall Description

### 2.1 Product Perspective
A new, standalone, single-user web application. No dependency on legacy systems. Designed so local development requires zero cloud dependency, and swapping to cloud services (Supabase Postgres, Render, Vercel) at deployment time requires **only environment variable changes** — no code changes.

### 2.2 Development & Deployment Philosophy (critical constraint)
1. **Local-first development:** Build and fully test on local machine — local Postgres (or Supabase free-tier dev project), FastAPI run via `uvicorn`, Next.js via `npm run dev`. **No Docker at this stage.**
2. **Dockerize for production only:** Once locally verified, containerize FE and BE separately for deployment.
3. **Cloud production stack:** Supabase (Postgres), Render (FastAPI backend container), Vercel (Next.js frontend, typically without Docker since Vercel builds natively — see §9.3).
4. Every config that differs between local and cloud (DB URL, API base URL, CORS origins, secrets) **must** be environment-variable-driven — never hardcoded — so the same codebase runs unmodified in both environments.

### 2.3 User Characteristics
Single non-technical end user (or a handful, ~1–15, no auth in V1) who wants a simple, fast, visually clear way to log and understand personal spending.

### 2.4 Assumptions & Dependencies
- No authentication in V1 (see PRD §11 risk note — flagged for Phase 2)
- One fixed currency (₹ INR)
- Single environment credentials for Supabase/Render/Vercel obtained before production deployment
- Node.js 18+, Python 3.11+, PostgreSQL 15+ available locally for dev

---

## 3. System Architecture

```
┌─────────────────────────────────────────┐
│  FRONTEND — Next.js (App Router) + TS    │
│  Tailwind CSS + shadcn/ui + Framer Motion│
│  Recharts + Three.js/R3F (3D accents)    │
│  Deployed: Vercel                        │
└──────────────────┬────────────────────────┘
                   │ REST API (JSON, HTTPS)
                   ↓
┌─────────────────────────────────────────┐
│  BACKEND — FastAPI + Pydantic            │
│  SQLAlchemy (ORM) + Alembic (migrations) │
│  Deployed: Render (Dockerized)           │
└──────────────────┬────────────────────────┘
                   │ SQL (asyncpg / psycopg)
                   ↓
┌─────────────────────────────────────────┐
│  DATABASE — PostgreSQL                   │
│  Deployed: Supabase                      │
└─────────────────────────────────────────┘
```

**Architecture principles:**
- Backend is fully stateless; all state lives in PostgreSQL — required for Render's horizontally-restartable containers.
- Frontend never talks to the DB directly — always through the REST API.
- CORS is environment-driven — dev allows `localhost:3000`; prod allows only the deployed Vercel domain.

---

## 4. Backend Requirements (FastAPI)

### 4.1 Standard Folder Structure
```
backend/
│
├── app/
│   ├── main.py                     # FastAPI app instance, router registration, CORS, startup events
│   │
│   ├── core/
│   │   ├── config.py                # Pydantic Settings — loads all env vars, single source of truth
│   │   ├── database.py              # SQLAlchemy engine/session setup
│   │   └── security.py              # Reserved for Phase 2 auth — no logic in V1, boundary exists early
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── expense.py
│   │   ├── category.py
│   │   └── budget.py
│   │
│   ├── schemas/                     # Pydantic request/response DTOs
│   │   ├── expense.py
│   │   ├── category.py
│   │   ├── budget.py
│   │   └── common.py                # shared: pagination, error response shapes
│   │
│   ├── routers/
│   │   └── v1/                      # API versioned from day one
│   │       ├── expenses.py
│   │       ├── categories.py
│   │       ├── budgets.py
│   │       ├── dashboard.py
│   │       ├── analytics.py
│   │       └── health.py
│   │
│   ├── services/                    # Business logic — testable independent of HTTP layer
│   │   ├── expense_service.py
│   │   ├── category_service.py
│   │   ├── budget_service.py
│   │   ├── analytics_service.py
│   │   └── alert_service.py
│   │
│   ├── utils/
│   │   ├── validators.py
│   │   └── formatters.py
│   │
│   └── seed/
│       └── seed_data.py             # Idempotent seed script (starter categories)
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── conftest.py                  # shared fixtures (test DB session, test client)
│   ├── test_expenses.py
│   ├── test_categories.py
│   ├── test_budgets.py
│   ├── test_analytics.py
│   └── test_health.py
│
├── .env.example
├── .gitignore                       # backend-specific
├── requirements.txt
├── alembic.ini
├── Dockerfile                       # production only
└── README.md                        # local setup instructions (see §9.1)
```

**Layering rule (enforced, non-negotiable):** `routers` never contain business logic or raw SQL — they call `services`, which use `models` via SQLAlchemy sessions and return/accept `schemas`. This is what makes the codebase safe to hand off or extend without introducing bugs.

**API versioning implication:** since routers live under `routers/v1/`, all endpoint paths in §7 are prefixed `/api/v1/...` (not `/api/...`) — `API_V1_PREFIX` in `core/config.py` controls this centrally.

### 4.2 Backend `.env.example`
```env
# --- App ---
APP_ENV=development                # development | production
APP_DEBUG=true
APP_NAME=ExpenseFlow API
API_V1_PREFIX=/api/v1

# --- Database ---
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/expenseflow
# In production (Supabase): postgresql+psycopg://<user>:<pass>@<supabase-host>:5432/postgres

# --- CORS ---
CORS_ORIGINS=http://localhost:3000
# In production: https://your-app.vercel.app

# --- Misc ---
LOG_LEVEL=info
SEED_ON_STARTUP=false              # true only for fresh dev DB
```

### 4.3 Configuration Loading
- `config.py` uses `pydantic-settings.BaseSettings` to read all values from environment (loaded from `.env` via `python-dotenv` locally; via platform env vars on Render).
- **No value in `config.py` or anywhere else in the codebase may be hardcoded** — every DB URL, secret, CORS origin, and feature flag flows through `Settings`.
- Fails fast (raises on startup) if a required env var is missing — prevents "works on my machine" bugs from reaching Render.

### 4.4 Migrations & Seeding
- All schema changes go through **Alembic** migrations — never manual `create_all()` in production.
- `alembic upgrade head` runs as part of the Render deploy step (pre-start command).
- **Seed data:** `seed/seed_data.py` inserts the starter categories (Food, Transport, Rent, Shopping, Bills, Entertainment, Health, Education, Other) idempotently (checks existence before insert) — safe to run repeatedly, runs automatically only when `SEED_ON_STARTUP=true` (local/dev), never blindly in production.

### 4.5 Health Endpoint
| Method | Endpoint | Response | Purpose |
|---|---|---|---|
| GET | `/api/v1/health` | `{"status": "ok", "db": "connected", "version": "1.0.0"}` | Render health checks, uptime monitors. Verifies DB connectivity, not just process liveness. |

Returns `503` with `{"status": "error", "db": "disconnected"}` if the DB ping fails — so Render correctly flags an unhealthy instance instead of routing traffic to a broken one.

### 4.6 Error Handling Contract
All error responses follow one shape, app-wide (enforced via a global FastAPI exception handler):
```json
{
  "detail": "Human-readable message",
  "error_code": "EXPENSE_NOT_FOUND",
  "status_code": 404
}
```
| Status | Usage |
|---|---|
| 200 | Success |
| 201 | Resource created |
| 400 | Bad request (malformed input) |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

---

## 5. Frontend Requirements (Next.js)

### 5.1 Standard Folder Structure
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                 # Dashboard (landing)
│   ├── expenses/
│   │   └── page.tsx
│   ├── analytics/
│   │   └── page.tsx
│   ├── budget/
│   │   └── page.tsx
│   └── settings/
│       └── page.tsx
│
├── components/
│   ├── dashboard/                # Summary cards, charts
│   ├── expenses/                 # Table, form, filters, modal
│   ├── analytics/
│   ├── budget/
│   ├── shared/                   # Loading skeletons, empty states, error states
│   └── ui/                       # shadcn/ui primitives
│
├── lib/
│   ├── api/                      # Typed API client functions (one file per resource)
│   │   ├── expenses.ts
│   │   ├── categories.ts
│   │   ├── budget.ts
│   │   └── analytics.ts
│   ├── validation/                # Zod schemas mirroring backend Pydantic schemas
│   └── utils.ts
│
├── hooks/                         # Custom hooks (useExpenses, useBudget, etc.)
├── types/                         # Shared TypeScript types (mirrors API contract)
├── styles/
│
├── .env.example
├── .env.local                     # gitignored, local only
├── .gitignore                     # frontend-specific
├── next.config.js
├── tailwind.config.ts
├── Dockerfile                     # production only
└── package.json
```

### 5.2 Frontend `.env.example`
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
# In production (Vercel): https://your-backend.onrender.com/api
NEXT_PUBLIC_APP_ENV=development
```

### 5.3 UI/UX & Interaction Requirements
| Requirement | Detail |
|---|---|
| **Validation** | Client-side validation via Zod + react-hook-form, mirroring backend Pydantic rules exactly (positive amount, no future date, required title ≤50 chars) — user gets instant feedback before the API round-trip. |
| **Design system** | shadcn/ui components throughout (buttons, dialogs, dropdowns, tables, tabs, toasts, tooltips); Tailwind for layout/spacing; rounded cards, soft shadows, clear hierarchy. |
| **Framer Motion** | Page transitions, list item enter/exit (e.g. expense added/removed), modal open/close, chart reveal-on-scroll. Used purposefully — not decoratively on every element. |
| **Micro-interactions** | Button press feedback, form field focus states, success toast on save, subtle hover states on cards/rows, animated number counters on dashboard totals. |
| **3D accents** | Optional lightweight 3D (e.g. React Three Fiber) reserved for a hero/empty-state illustration or an interactive budget visualization — not applied to core data tables, to protect performance and clarity. |
| **Responsive design** | Mobile-first Tailwind breakpoints; dashboard grid collapses to single column on mobile; tables become scrollable/stacked cards on small screens; tested at 375px, 768px, 1024px, 1440px. |
| **Theming** | Light/dark mode via a theme provider (e.g. `next-themes`), persisted in `localStorage`, applied consistently via Tailwind's `dark:` variants. |
| **App states** | Every data view implements: loading (skeleton), empty (with CTA), no-search-results, error (with retry), success (toast). No screen is ever left blank or stuck. |

### 5.4 API Integration Rules
- All API calls go through a single typed client in `lib/api/` — no ad-hoc `fetch()` calls scattered in components.
- Base URL always read from `NEXT_PUBLIC_API_BASE_URL` — never hardcoded, so switching from local FastAPI to Render requires zero code change.
- TypeScript types in `types/` are hand-kept in sync with backend Pydantic schemas (see §7 API Contract) to prevent shape-mismatch bugs.

---

## 6. Database Requirements (PostgreSQL + SQLAlchemy + Alembic)

### 6.1 Schema

**`categories`**
| Column | Type | Constraints |
|---|---|---|
| id | UUID / SERIAL | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |
| created_at | TIMESTAMP | default now() |

**`expenses`**
| Column | Type | Constraints |
|---|---|---|
| id | UUID / SERIAL | PK |
| amount | DECIMAL(10,2) | NOT NULL, CHECK (amount > 0) |
| category_id | FK → categories.id | NOT NULL, ON DELETE RESTRICT* |
| description | VARCHAR(50) | NOT NULL |
| notes | TEXT | nullable |
| date | DATE | NOT NULL, CHECK (date <= CURRENT_DATE) |
| payment_method | VARCHAR(30) | nullable (e.g. Cash, GPay, Credit Card, UPI, Bank Transfer, Others; tagging only, no gateway integration) |
| created_at | TIMESTAMP | default now() |
| updated_at | TIMESTAMP | auto-update on change |

*\*`ON DELETE RESTRICT`: matches PRD requirement that a category can't be deleted while expenses reference it, unless the user explicitly reassigns/cascades via the API layer (handled in `category_service.py`, not at the DB constraint level, so the app can show a proper warning instead of a raw DB error).*

**`budgets`**
| Column | Type | Constraints |
|---|---|---|
| id | UUID / SERIAL | PK |
| month | INTEGER | NOT NULL, CHECK (1–12) |
| year | INTEGER | NOT NULL |
| amount | DECIMAL(10,2) | NOT NULL, CHECK (amount > 0) |
| category_id | FK → categories.id | nullable (null = overall budget) |
| created_at / updated_at | TIMESTAMP | |

*Analytics, budget-used-%, and alerts are computed dynamically at query time — not stored — matching both source PRDs and keeping the schema simple and bug-resistant (no risk of stale aggregates).*

### 6.2 Migrations
- Alembic autogenerate used for schema changes; every migration reviewed manually before commit (autogenerate can miss constraint nuances).
- Migration naming: `YYYYMMDD_HHMM_short_description.py`.
- `alembic upgrade head` is part of the deploy pipeline on Render, run before the app starts serving traffic.

### 6.3 Seeding
- Idempotent seed script (`seed_data.py`) inserts starter categories in the backend database only if the table is empty.
- Categories are dynamically loaded by the frontend from `/api/v1/categories`; categories are **never** hardcoded or seeded in the frontend directly.
- Runs automatically when `SEED_ON_STARTUP=true` (local/dev), never blindly in production.

---

## 7. REST API Contract

All endpoints prefixed `/api/v1` (per `routers/v1/` structure, §4.1). All list endpoints support pagination, filtering, and sorting per the query parameters below.

### 7.1 Expenses
| Method | Endpoint | Request Body | Response | Notes |
|---|---|---|---|---|
| POST | `/api/v1/expenses` | `{amount, category_id, description, date, payment_method?, notes?}` | `201` + expense object | Validates per §4.6/§6.1 |
| GET | `/api/v1/expenses` | Query: `search, category_id, payment_method, amount_min, amount_max, date_from, date_to, sort, page, page_size` | `200` + `{items: [...], total, page, page_size}` | |
| GET | `/api/v1/expenses/{id}` | — | `200` + expense object | `404` if missing |
| PUT | `/api/v1/expenses/{id}` | Same as POST (partial allowed) | `200` + updated object | |
| DELETE | `/api/v1/expenses/{id}` | — | `204` | |
| GET | `/api/v1/expenses/export` | Query: `format=csv\|pdf`, plus filters (`search, category_id, date_from, ...`) | `200` + CSV or PDF file stream | Export format controlled by `format` query param |

### 7.2 Categories
| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/v1/categories` | `{name}` → `201` |
| GET | `/api/v1/categories` | Returns list with `expense_count` per category |
| PUT | `/api/v1/categories/{id}` | Rename |
| DELETE | `/api/v1/categories/{id}` | `400` if in use, unless `?reassign_to={id}` query param given |

### 7.3 Budget
| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/budgets?month=&year=` | Overall + per-category budgets for the period |
| POST | `/api/v1/budgets` | `{month, year, amount, category_id?}` |
| PUT | `/api/v1/budgets/{id}` | |
| DELETE | `/api/v1/budgets/{id}` | |

### 7.4 Dashboard & Analytics
| Method | Endpoint | Returns |
|---|---|---|
| GET | `/api/v1/dashboard` | Summary cards, recent expenses, highest expense, budget status |
| GET | `/api/v1/analytics/daily?date=` | Daily total + breakdown |
| GET | `/api/v1/analytics/monthly?month=&year=` | Monthly trend |
| GET | `/api/v1/analytics/yearly?year=` | Month-by-month totals for the year |
| GET | `/api/v1/analytics/categories?month=&year=` | Per-category totals + % of spend |

### 7.5 Health
| Method | Endpoint | Returns |
|---|---|---|
| GET | `/api/v1/health` | `{status, db, version}` — see §4.5. Note: some platforms expect an unversioned `/health` too; if Render's health-check config needs that, add a thin unversioned alias in `main.py` that proxies to this handler — don't duplicate logic. |

### 7.6 Contract Discipline
- Every request/response shape defined as a Pydantic schema in `backend/app/schemas/` **and** mirrored as a TypeScript type in `frontend/types/` — treated as the single point of truth on each side.
- Breaking changes to any endpoint require updating both simultaneously, in the same commit, to prevent FE/BE drift.

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Paginated lists (20/page); dashboard makes a single aggregated call, not N+1 requests; charts render smoothly with up to several thousand expense rows. |
| **Reliability** | DB operations wrapped in transactions; API always returns structured errors (§4.6); frontend gracefully handles all API failure states. |
| **Security** | All inputs validated server-side (never trust client validation alone); secrets only via env vars; CORS restricted to known origins per environment; DB credentials never exposed to frontend or committed to git. |
| **Maintainability** | Strict layering (router → service → model) on backend; typed, componentized frontend; migrations versioned; consistent error/response contract. |
| **Portability** | Zero hardcoded environment assumptions — same codebase runs local or cloud via env vars only. |
| **Testability** | Backend services unit-testable independent of HTTP layer; `tests/` covers CRUD, budget calculation, and alert logic at minimum. |
| **Usability** | Add-expense flow completable in <30 seconds; all states (loading/empty/error/success) always present, never a blank screen. |

---

## 9. DevOps & Deployment Design

### 9.1 Local Development (no Docker)
1. **Database:** Local PostgreSQL instance, or a free Supabase dev project — either works; connection via `DATABASE_URL` in `backend/.env`.
2. **Backend:** `pip install -r requirements.txt` → `alembic upgrade head` → `uvicorn app.main:app --reload`.
3. **Frontend:** `npm install` → `npm run dev`, pointing `NEXT_PUBLIC_API_BASE_URL` at `http://localhost:8000/api/v1`.
4. Full manual + automated test pass locally before any Docker/deployment work begins.

### 9.2 Production Dockerization
- **`backend/Dockerfile`** — multi-stage build (install deps → copy app → run via `uvicorn`/`gunicorn` with `uvicorn.workers.UvicornWorker`), reads all config from environment at container start, runs `alembic upgrade head` as a pre-start step.
- **`frontend/Dockerfile`** — only needed if not using Vercel's native build; if deploying to Vercel, Vercel's own build pipeline is used instead of this Dockerfile (Vercel doesn't require Docker). The Dockerfile is kept for portability (e.g. if you later self-host the frontend elsewhere) but isn't the deployment path for Vercel itself.
- Both Dockerfiles live only in their respective `backend/` and `frontend/` folders — **not used or referenced during local development** (§2.2).

### 9.3 Cloud Platform Mapping
| Layer | Platform | Notes |
|---|---|---|
| Database | **Supabase** | Managed Postgres; `DATABASE_URL` from Supabase connection string set as a Render env var |
| Backend | **Render** | Deploys `backend/Dockerfile`; env vars set in Render dashboard; health check path set to `/api/health` |
| Frontend | **Vercel** | Deploys directly from `frontend/`; env vars (`NEXT_PUBLIC_API_BASE_URL`, pointing to the Render backend URL) set in Vercel dashboard |

### 9.4 Deployment Order (to avoid chicken-and-egg bugs)
1. Provision Supabase project → get `DATABASE_URL`.
2. Deploy backend to Render with that `DATABASE_URL` → run migrations → confirm `/api/health` is green.
3. Deploy frontend to Vercel with `NEXT_PUBLIC_API_BASE_URL` pointing at the live Render URL.
4. Update backend `CORS_ORIGINS` to include the live Vercel domain, redeploy backend.

---

## 10. Git & Repository Structure

```
project-root/
├── .gitignore              # root-level — OS files, IDE configs, general artifacts
├── backend/
│   └── .gitignore          # backend-specific — venv, __pycache__, .env, alembic local cache
├── frontend/
│   └── .gitignore          # frontend-specific — node_modules, .next, .env.local
├── docs/
│   ├── PRD.md
│   └── SRS.md
└── README.md
```

Each `.gitignore` is scoped to its own layer's tooling — prevents accidentally committing `node_modules/`, Python virtualenvs, or any `.env` file with real secrets.

---

## 11. Acceptance Criteria (per module)

**Expense CRUD:** form validates client- and server-side; invalid amounts/future dates rejected at both layers; new expense reflects instantly in list and dashboard totals.

**Categories:** deleting an in-use category is blocked or requires explicit reassignment; category list always reflects live expense counts.

**Budget & Alerts:** color status matches thresholds exactly (green <85%, yellow 85–99.99%, red ≥100%); alerts are computed fresh on each dashboard load, never stale.

**Search/Filter/Sort:** all combinable simultaneously; pagination metadata (`total`, `page`) always accurate.

**Deployment:** app runs identically local vs. production with only env vars changed; `/api/health` returns `200` post-deploy before frontend is pointed at it.

---

## 12. Traceability Note
Every functional requirement in this SRS traces back to a PRD requirement ID (FR-1 through FR-34) and forward to a specific API endpoint (§7) and DB table (§6.1) — maintained this way intentionally so no requirement is implemented ambiguously or inconsistently across layers.
