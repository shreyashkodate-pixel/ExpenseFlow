# Software Requirements Specification (SRS)
## ExpenseFlow — Personal Expense & Budget Tracker

**Document Version:** 2.0  
**Status:** Approved Architecture & Implementation Spec  
**Based on:** ExpenseFlow PRD & Production Authentication Architecture Spec  
**Prepared for:** Full-stack development, multi-user cloud deployment (Supabase + Vercel + Render)

---

## 1. Introduction

### 1.1 Purpose
This SRS specifies the complete technical requirements for **ExpenseFlow**, including its secure JWT-based authentication layer, Google OAuth 2.0 / OpenID Connect integration, strict user data isolation, dynamic category management, budget goal tracking, spending analytics, and automated multi-format data exports (CSV and PDF).

### 1.2 Scope
ExpenseFlow is a responsive, multi-user web application where every authenticated user manages their own private financial records. The system provides:
* Secure Sign-Up, Login, Google OAuth 2.0 Sign-In, and Password Reset lifecycle.
* Short-lived JWT Access Tokens (15 min) + HttpOnly/Secure Refresh Tokens (14 days) with automatic token rotation, reuse detection, and server-side revocation.
* Strict per-user data isolation (User A can never read, modify, or delete User B's records).
* Dynamic category management (global starter categories + custom user categories).
* Real-time budget utilization tracking (`on_track`, `warning`, `exceeded`).
* Interactive analytics (Daily, Monthly, Yearly trends, and Category spending breakdowns).
* ReportLab PDF and CSV expense report export streams.
* Progressive Web App (PWA) offline resilience and multi-device responsive design.

### 1.3 Definitions & Abbreviations
| Term | Meaning |
|---|---|
| SRS | Software Requirements Specification |
| JWT | JSON Web Token (RFC 7519) |
| OAuth 2.0 / OIDC | OpenID Connect identity layer on top of OAuth 2.0 |
| RTR | Refresh Token Rotation (one-time use tokens with theft detection) |
| ORM | Object-Relational Mapper (SQLAlchemy 2.0) |
| CRUD | Create, Read, Update, Delete |
| DTO | Data Transfer Object (Pydantic v2 schemas / TypeScript types) |

---

## 2. Overall Description

### 2.1 Product Perspective
A standalone, multi-user web application with a decoupled Next.js frontend and FastAPI backend. All state is persisted in a PostgreSQL database (Supabase). The backend is fully stateless with server-side token validation and database-backed refresh token revocation.

### 2.2 Security & Data Isolation Philosophy (Critical Architectural Rules)
1. **Zero Trust on Frontend Identifiers:** The backend *never* trusts a `user_id` supplied in request bodies, query parameters, or URL paths. The user identity is derived exclusively from the verified JWT in the `Authorization: Bearer <token>` header.
2. **Strict Resource Ownership:** Every database query for expenses, budgets, analytics, and custom categories must filter by `user_id == current_user.id`. Any attempt to read or mutate another user's entity returns `404 Not Found` (never leaking existence).
3. **Defense-in-Depth Token Storage:** Access tokens reside exclusively in client-side memory (never stored in `localStorage`). Refresh tokens reside in `HttpOnly`, `Secure`, `SameSite=Lax` cookies. Database stores only cryptographic SHA-256 hashes of refresh tokens.
4. **Token Reuse Detection:** If an already-revoked or rotated refresh token is presented, all active sessions for that user session family are immediately invalidated.
5. **BCrypt Password Security:** Passwords hashed with BCrypt (cost factor 12). Plaintext passwords never logged or returned.
6. **No Admin/RBAC Overhead:** The system enforces flat, isolated single-user perimeters without unnecessary role-based access control complexity.

### 2.3 Assumptions & Dependencies
* Python 3.11+, Node.js 18+, PostgreSQL 15+ (local dev) / PostgreSQL 16 (Supabase cloud).
* Google Cloud Console OAuth 2.0 Client ID and Secret configured for Google Sign-In.
* Currency format standard (₹ INR default with extensible symbol formatting).

---

## 3. System Architecture

```
┌────────────────────────────────────────────────────────┐
│  FRONTEND — Next.js 14 (App Router) + TypeScript       │
│  Tailwind CSS + Glassmorphism Tokens + Framer Motion   │
│  AuthContext + In-Memory JWT + 401 Silent Refresh       │
│  Deployed: Vercel                                      │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS (Bearer JWT / HttpOnly Cookie)
                            ↓
┌────────────────────────────────────────────────────────┐
│  BACKEND — FastAPI (Python 3.11/3.14)                  │
│  Security Layer (BCrypt, PyJWT, Google Auth)           │
│  User Ownership Dependencies (`get_current_user`)      │
│  SQLAlchemy 2.0 ORM + Alembic Migrations               │
│  Deployed: Render (Dockerized)                         │
└───────────────────────────┬────────────────────────────┘
                            │ PostgreSQL Protocol (psycopg)
                            ↓
┌────────────────────────────────────────────────────────┐
│  DATABASE — PostgreSQL (Supabase / Local)              │
│  Tables: users, refresh_tokens, password_reset_tokens, │
│          categories, expenses, budgets                 │
└────────────────────────────────────────────────────────┘
```

---

## 4. Backend Requirements (FastAPI)

### 4.1 Folder Structure
```
backend/
├── app/
│   ├── main.py                     # FastAPI app, CORS middleware, global exception handler, lifespan
│   ├── core/
│   │   ├── config.py               # Pydantic Settings (JWT secrets, DB URL, CORS origins, Google OAuth)
│   │   ├── database.py             # SQLAlchemy engine & session maker
│   │   ├── security.py             # BCrypt hashing, JWT creation/decoding, SHA-256 token hashing
│   │   ├── dependencies.py         # get_current_user, rate limiter dependency
│   │   └── exceptions.py           # Standard AppException and handlers
│   ├── models/
│   │   ├── user.py                 # User ORM model
│   │   ├── refresh_token.py        # Hashed RefreshToken ORM model
│   │   ├── password_reset_token.py # Hashed PasswordResetToken ORM model
│   │   ├── expense.py              # Expense model with user_id FK
│   │   ├── category.py             # Category model with nullable user_id FK
│   │   └── budget.py               # Budget model with user_id FK
│   ├── schemas/
│   │   ├── auth.py                 # UserRegister, UserLogin, GoogleAuth, TokenResponse, etc.
│   │   ├── expense.py              # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   │   ├── category.py             # CategoryCreate, CategoryUpdate, CategoryResponse
│   │   ├── budget.py               # BudgetCreate, BudgetUpdate, BudgetStatusItem
│   │   ├── analytics.py            # DashboardSummary, Daily/Monthly/Yearly analytics
│   │   └── common.py               # PaginatedResponse, ErrorResponse
│   ├── routers/v1/
│   │   ├── auth.py                 # Register, Login, Google, Refresh, Logout, Reset Password
│   │   ├── expenses.py             # User-isolated Expense CRUD & Export
│   │   ├── categories.py           # Global + User custom Category CRUD
│   │   ├── budgets.py              # User-isolated Budget CRUD & Status
│   │   ├── dashboard.py            # User-isolated Dashboard Summary
│   │   ├── analytics.py            # User-isolated Spending Trends
│   │   └── health.py               # Health check
│   ├── services/
│   │   ├── auth_service.py         # Core auth, token rotation, session management, Google validation
│   │   ├── expense_service.py      # User-scoped expense queries and mutations
│   │   ├── category_service.py     # Global + user custom categories logic
│   │   ├── budget_service.py       # User-scoped budget status calculations
│   │   ├── analytics_service.py    # User-scoped metrics and aggregations
│   │   └── export_service.py       # User-scoped CSV & PDF report builder
│   └── seed/
│       └── seed_data.py            # Starter category seeder
├── alembic/
│   └── versions/                   # Versioned database migrations
├── tests/
│   ├── conftest.py                 # Test DB fixtures, mock users, client helpers
│   ├── test_auth.py                # Registration, login, password reset tests
│   ├── test_token_flow.py          # Token rotation, reuse detection, revocation tests
│   ├── test_data_isolation.py      # Multi-user data isolation verification
│   └── test_expenses.py            # Expense CRUD & validation tests
└── requirements.txt
```

### 4.2 Backend Environment Configuration (`.env.example`)
```env
# --- Application ---
APP_NAME=ExpenseFlow
APP_ENV=development
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO

# --- Database ---
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/expenseflow

# --- CORS ---
CORS_ORIGINS=http://localhost:3000

# --- JWT & Security ---
JWT_SECRET_KEY=generate_a_secure_random_64_character_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=14
PASSWORD_RESET_EXPIRE_MINUTES=60
COOKIE_SECURE=false
COOKIE_SAMESITE=lax

# --- Google OAuth 2.0 ---
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

---

## 5. Frontend Requirements (Next.js 14 App Router)

### 5.1 Structure & Authentication Components
```
frontend/
├── app/
│   ├── layout.tsx                  # Root layout with ThemeProvider, ToastProvider, AuthProvider
│   ├── page.tsx                    # Dashboard (Protected)
│   ├── expenses/page.tsx           # Expense Management (Protected)
│   ├── analytics/page.tsx          # Analytics (Protected)
│   ├── budget/page.tsx             # Budget Goals (Protected)
│   ├── settings/page.tsx           # Settings & Account Security (Protected)
│   ├── login/page.tsx              # Sign-In View with Google OAuth button
│   ├── register/page.tsx           # Sign-Up View with Password Strength indicator
│   ├── forgot-password/page.tsx    # Password Reset Request View
│   └── reset-password/page.tsx     # Password Reset Confirmation View
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.tsx      # Client auth guard & redirect handler
│   ├── dashboard/                  # Dashboard cards and widgets
│   ├── expenses/                   # ExpenseTable, ExpenseFilters, ExpenseModal
│   ├── shared/                     # Sidebar, MobileNav, Header, ThemeToggle, PWAInstall
│   └── ui/                         # Modal, Toast, Button, Input primitives
├── context/
│   └── AuthContext.tsx             # Global Auth State, login, logout, refresh handlers
├── lib/
│   ├── api/
│   │   ├── client.ts               # In-memory JWT storage, fetch wrapper & 401 refresh interceptor
│   │   ├── auth.ts                 # Typed auth API endpoints
│   │   ├── expenses.ts
│   │   ├── categories.ts
│   │   ├── budgets.ts
│   │   └── analytics.ts
│   └── validation/                 # Zod validation schemas
└── types/
    └── auth.ts                     # User, Token, AuthState TypeScript interfaces
```

---

## 6. Database Schema & Relations (PostgreSQL)

### 6.1 Entity Relational Schema

```mermaid
erDiagram
    USERS ||--o{ EXPENSES : "owns"
    USERS ||--o{ BUDGETS : "sets"
    USERS ||--o{ REFRESH_TOKENS : "issues"
    USERS ||--o{ PASSWORD_RESET_TOKENS : "requests"
    USERS ||--o{ CATEGORIES : "creates (optional)"
    CATEGORIES ||--o{ EXPENSES : "classifies"
    CATEGORIES ||--o{ BUDGETS : "targets"

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string avatar_url
        boolean is_verified
        boolean is_active
        string google_id UK
        datetime created_at
        datetime updated_at
    }

    REFRESH_TOKENS {
        int id PK
        int user_id FK
        string token_hash UK
        string device_info
        string ip_address
        boolean is_revoked
        datetime expires_at
        datetime created_at
        datetime revoked_at
    }

    PASSWORD_RESET_TOKENS {
        int id PK
        int user_id FK
        string token_hash UK
        boolean used
        datetime expires_at
        datetime created_at
    }

    CATEGORIES {
        int id PK
        string name
        int user_id FK "nullable (NULL for system categories)"
        datetime created_at
    }

    EXPENSES {
        int id PK
        int user_id FK
        decimal amount
        int category_id FK
        string description
        text notes
        date date
        string payment_method
        datetime created_at
        datetime updated_at
    }

    BUDGETS {
        int id PK
        int user_id FK
        int month
        int year
        decimal amount
        int category_id FK "nullable (NULL for overall)"
        datetime created_at
        datetime updated_at
    }
```

---

## 7. REST API Contract

All endpoints are versioned under `/api/v1`.

### 7.1 Authentication & Session Management (`/api/v1/auth`)

| Method | Endpoint | Access | Request Body | Response | Notes |
|---|---|---|---|---|---|
| POST | `/api/v1/auth/register` | Public | `{email, password, full_name?}` | `201` + `{user, access_token, token_type}` | Sets HttpOnly `refresh_token` cookie. |
| POST | `/api/v1/auth/login` | Public | `{email, password}` | `200` + `{user, access_token, token_type}` | Sets HttpOnly `refresh_token` cookie. Rate limited. |
| POST | `/api/v1/auth/google` | Public | `{credential}` | `200` + `{user, access_token, token_type}` | Verifies Google ID token / OpenID payload. |
| POST | `/api/v1/auth/refresh` | Cookie | Optional body fallback `{refresh_token?}` | `200` + `{access_token, token_type}` | Rotates refresh token; updates cookie. Invalidation on reuse. |
| POST | `/api/v1/auth/logout` | Cookie / Bearer | — | `204 No Content` | Revokes active session & clears cookie. |
| POST | `/api/v1/auth/logout-all` | Protected | — | `200` + `{"status": "all_sessions_revoked"}` | Revokes all active refresh tokens for current user in DB. |
| GET | `/api/v1/auth/me` | Protected | — | `200` + `UserResponse` | Returns active user profile. |
| PUT | `/api/v1/auth/me` | Protected | `{full_name?, avatar_url?}` | `200` + `UserResponse` | Updates current user profile. |
| POST | `/api/v1/auth/change-password` | Protected | `{old_password, new_password}` | `200` + `{"status": "password_updated"}` | Updates password and revokes other sessions. |
| POST | `/api/v1/auth/forgot-password` | Public | `{email}` | `200` + `{"status": "success", "message": "..."}` | Generates reset token hash with 1h expiry. Rate limited. |
| POST | `/api/v1/auth/reset-password` | Public | `{token, new_password}` | `200` + `{"status": "password_reset_success"}` | Resets password, marks token used, revokes all sessions. |

### 7.2 Expenses (`/api/v1/expenses`) — User Isolated

All expense endpoints require `Authorization: Bearer <access_token>` and derive `user_id` from the token.

| Method | Endpoint | Access | Query / Body | Response | Data Isolation Rule |
|---|---|---|---|---|---|
| POST | `/api/v1/expenses` | Protected | Body: `{amount, category_id, description, date, payment_method?, notes?}` | `201` + Expense | Assigns `user_id = current_user.id`. |
| GET | `/api/v1/expenses` | Protected | Query: `search, category_id, payment_method, amount_min, amount_max, date_from, date_to, sort, page, page_size` | `200` + Paginated Expenses | Filters strictly by `user_id == current_user.id`. |
| GET | `/api/v1/expenses/{id}` | Protected | — | `200` + Expense | Returns `404` if expense does not belong to user. |
| PUT | `/api/v1/expenses/{id}` | Protected | Body: Partial/Full expense fields | `200` + Expense | Modifies only if `user_id == current_user.id` (`404` otherwise). |
| DELETE | `/api/v1/expenses/{id}` | Protected | — | `204 No Content` | Deletes only if `user_id == current_user.id` (`404` otherwise). |
| GET | `/api/v1/expenses/export` | Protected | Query: `format=csv\|pdf`, plus filter parameters | `200` + CSV / PDF Stream | Streams file containing only the authenticated user's records. |

### 7.3 Categories (`/api/v1/categories`) — Global Starter + User Custom

| Method | Endpoint | Access | Request Body | Response | Notes |
|---|---|---|---|---|---|
| GET | `/api/v1/categories` | Protected | — | `200` + List of Categories | Returns system categories (`user_id IS NULL`) + user custom categories (`user_id == current_user.id`) with user-scoped `expense_count`. |
| POST | `/api/v1/categories` | Protected | `{name}` | `201` + Category | Creates custom category with `user_id = current_user.id`. |
| PUT | `/api/v1/categories/{id}` | Protected | `{name}` | `200` + Category | Only custom categories belonging to user can be edited. |
| DELETE | `/api/v1/categories/{id}` | Protected | Query: `?reassign_to={id}` | `204 No Content` | Blocks deletion of system categories or other users' categories. |

### 7.4 Budgets (`/api/v1/budgets`) — User Isolated

| Method | Endpoint | Access | Query / Body | Response | Notes |
|---|---|---|---|---|---|
| GET | `/api/v1/budgets` | Protected | Query: `month, year, category_id` | `200` + List of Budgets | Scoped to `user_id == current_user.id`. |
| POST | `/api/v1/budgets` | Protected | Body: `{month, year, amount, category_id?}` | `201`/`200` + Budget | Upserts budget scoped to `user_id == current_user.id`. |
| PUT | `/api/v1/budgets/{id}` | Protected | Body: `{amount?, month?, year?, category_id?}` | `200` + Budget | Ownership verified; `404` if not found/owned. |
| DELETE | `/api/v1/budgets/{id}` | Protected | — | `204 No Content` | Ownership verified; `404` if not found/owned. |

### 7.5 Dashboard & Analytics (`/api/v1/dashboard`, `/api/v1/analytics/*`) — User Isolated

| Method | Endpoint | Access | Query Params | Response | Ownership Scope |
|---|---|---|---|---|---|
| GET | `/api/v1/dashboard` | Protected | — | `200` + DashboardSummary | Calculates monthly spend, recent 5 expenses, highest expense, and budget status solely from `current_user.id`'s records. |
| GET | `/api/v1/analytics/daily` | Protected | `date=YYYY-MM-DD` | `200` + DailyAnalytics | Aggregated solely for `current_user.id`. |
| GET | `/api/v1/analytics/monthly` | Protected | `month=MM&year=YYYY` | `200` + MonthlyAnalytics | Daily spending curve for calendar days of month for `current_user.id`. |
| GET | `/api/v1/analytics/yearly` | Protected | `year=YYYY` | `200` + YearlyAnalytics | Month-by-month spending trends for `current_user.id`. |
| GET | `/api/v1/analytics/categories` | Protected | `month=MM&year=YYYY` | `200` + List of CategorySpending | Category % distribution for `current_user.id`. |

### 7.6 AI Financial Intelligence & Recommendations (`/api/v1/ai/*`) — Environment-Driven & User-Isolated

The AI subsystem implements a **Provider-Agnostic Adapter Pattern** (`BaseAIProvider`), enabling dynamic switching between Google Gemini, OpenAI (ChatGPT), and Anthropic (Claude) using environment variables (`AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`, `AI_BASE_URL`) with zero hardcoding.

| Method | Endpoint | Access | Body / Query | Response | Purpose & Security |
|---|---|---|---|---|---|
| GET | `/api/v1/ai/recommendations` | Protected | — | `200` + AIRecommendations | Returns structured financial insights (unusual category spikes, actionable monthly savings opportunities, budget pacing alerts, financial health score). Pre-cached per user for 6h. |
| POST | `/api/v1/ai/recommendations/refresh` | Protected | — | `200` + AIRecommendations | Forces cache invalidation and generates fresh insights. Rate-limited (3 req/min). |
| POST | `/api/v1/ai/chat` | Protected | Body: `{message: str}` | `200` + AIChatResponse | Natural language financial assistant grounded exclusively in user's anonymized spending aggregates. |

#### AI Data Contract & Predictive Budget Alerts (Step 2):
`AIRecommendationResponse` includes `predictive_budget_alerts: List[PredictiveBudgetAlert]`:
* `category`: Budget category name or "Overall"
* `current_spend`: Actual money spent so far this month (₹)
* `budget_limit`: Configured budget cap (₹)
* `daily_burn_rate`: Spending velocity (`current_spend / days_elapsed`) in ₹/day
* `projected_total`: Month-end total forecast at current rate (`daily_burn_rate * total_days_in_month`)
* `projected_exhaustion_date`: Forecasted exhaustion calendar day (e.g. "September 18" or "Exceeded")
* `days_until_exhaustion`: Days remaining until budget runs out
* `safe_daily_ceiling`: Recommended daily spending cap to stay within budget for the remaining days of the month
* `pacing_status`: `"safe"` | `"caution"` | `"critical"` | `"exceeded"`
* `alert_message`: Proactive early-warning pacing message generated with AI context

#### AI Privacy & Isolation Rules:
* User financial metrics are aggregated server-side for `current_user.id` only.
* No Personally Identifiable Information (PII) such as email, name, or password is ever transmitted to external LLM APIs.
* In-memory sliding caching prevents redundant LLM billing and latency on frequent dashboard visits.

---

## 8. Non-Functional & Security Requirements

| Area | Requirement | Specification |
|---|---|---|
| **Password Security** | BCrypt / Argon2 | Hashed with BCrypt (12 rounds) or Argon2id. Plaintext never stored or logged. |
| **JWT Access Tokens** | RFC 7519 HMAC-SHA256 | Signed using server secret (`JWT_SECRET_KEY`). Short lifespan (15 minutes). Claims: `sub` (user_id), `email`, `exp`, `iat`. |
| **Refresh Tokens** | Cryptographic Random & SHA-256 Hashed | 64-character URL-safe string stored in DB as SHA-256 hash. Rotated on every use. Revoked on logout. |
| **Token Reuse Detection** | Automatic Theft Mitigation | If a previously rotated refresh token is presented, all active sessions in the token family are immediately revoked. |
| **Cookie Security** | HttpOnly, Secure, SameSite | Refresh token cookie set with `HttpOnly=True`, `Secure=True` (in production/HTTPS), `SameSite="Lax"`, `Path="/api/v1/auth"`. |
| **Rate Limiting** | Brute-force Protection | In-memory / SlowAPI rate limiting applied to `/api/v1/auth/login` (5 req/min) and `/api/v1/auth/forgot-password` (3 req/min). |
| **CORS Policy** | Restricted Dynamic Match | Starlette CORS middleware restricts requests to verified origins (`localhost:3000`, verified Vercel app domains) with `allow_credentials=True`. |
| **Cross-User Data Isolation** | Backend Enforced | Zero trust on client identity parameters; all resource endpoints scope database queries directly to the authenticated user ID. |

---

## 9. Verification & Acceptance Criteria

1. **Registration & Login:**
   - Registration creates a new user, hashes password with BCrypt, returns access token, and sets HttpOnly refresh token cookie.
   - Duplicate email registration is rejected with `400 Bad Request` (`EMAIL_ALREADY_EXISTS`).
   - Login validates credentials, issues fresh tokens, and records session in DB.
2. **Google OAuth 2.0:**
   - Google ID token verified on backend; links existing user by verified email or creates new user.
3. **Token Flow & Rotation:**
   - Access token expires after 15 minutes; client 401 interceptor automatically refreshes token via `/api/v1/auth/refresh` without user interruption.
   - Using an expired or tampered access token returns `401 Unauthorized`.
   - Refresh token rotation issues a new refresh token and marks the previous one revoked.
   - Replay attack using a revoked refresh token triggers immediate invalidation of all user sessions.
4. **Logout & Session Management:**
   - `POST /auth/logout` revokes current refresh token and clears cookie.
   - `POST /auth/logout-all` revokes all active refresh tokens for the user in the database.
5. **Multi-User Data Isolation:**
   - User A logs in and creates expenses and budgets.
   - User B logs in and queries `/expenses`, `/budgets`, `/dashboard`, `/analytics` -> receives only User B's empty/own data.
   - User B attempts `GET /expenses/{id_of_User_A}` -> returns `404 Not Found`.
   - User B attempts `PUT /expenses/{id_of_User_A}` or `DELETE /expenses/{id_of_User_A}` -> returns `404 Not Found`.
6. **Password Recovery:**
   - `POST /auth/forgot-password` generates a single-use hashed token with 1-hour expiry.
   - `POST /auth/reset-password` updates password and revokes all active sessions.
