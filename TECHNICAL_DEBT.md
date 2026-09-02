# ExpenseFlow — Pending Work & Technical Roadmap

**Last Updated:** September 1, 2026

This document tracks completed features, system architecture status, and technical roadmap items for ExpenseFlow.

---

## 📋 Completed Core Tasks

### 1. Backend Core & Database (`backend/app/core/`, `models/`, `seed/`, `alembic/`)
- [x] Configured environment variables via `pydantic-settings` (`DATABASE_URL`, `CORS_ORIGINS`, `API_V1_PREFIX`, `JWT_SECRET_KEY`, `COOKIE_SECURE`, `GOOGLE_CLIENT_ID`, `SMTP_*`, `FRONTEND_URL`).
- [x] Implemented SQLAlchemy engine, declarative models (`User`, `RefreshToken`, `PasswordResetToken`, `Category`, `Expense`, `Budget`), and session dependencies.
- [x] Executed Alembic database migrations (`48cef29c36e8_initial_schema` and `7a8e9f1b2c3d_auth_and_user_isolation`).
- [x] Configured PostgreSQL production database with connection pooling and idempotent category seeding.

---

### 2. Authentication & User Data Isolation (`backend/app/services/` & `routers/v1/auth.py`)
- [x] Short-lived (15-minute) signed JWT Access Tokens + long-lived (14-day) HttpOnly/Secure Refresh Tokens.
- [x] Refresh Token Rotation (RTR) and Token Reuse Detection with instant user session invalidation.
- [x] Password hashing using native BCrypt (12 work rounds) and SHA-256 token hashing for database storage.
- [x] Complete auth endpoint suite: `/register`, `/login`, `/google`, `/refresh`, `/logout`, `/logout-all`, `/me`, `/change-password`, `/forgot-password`, `/reset-password`.
- [x] Google Identity Services (GIS) OpenID Connect integration with audience verification and account linking.
- [x] Transactional SMTP email delivery service (`email_service.py`) for branded password reset emails.
- [x] Strict user data isolation across all expenses, budgets, custom categories, dashboard summaries, analytics, and PDF/CSV exports.
- [x] 100% passing automated test suite (27/27 tests) in `backend/tests/`.

---

### 3. Services & Business Logic (`backend/app/services/` & `routers/v1/`)
- [x] Paginated Expense CRUD with multi-field search, date/category/amount/method filtering, and sorting scoped to authenticated user.
- [x] Category CRUD with system defaults vs. user-owned custom categories and in-use reassignment protection (`?reassign_to=`).
- [x] Monthly and Category-specific budget limits with real-time status utilization calculation (`on_track`, `warning`, `exceeded`) scoped to authenticated user.
- [x] Daily, Monthly, and Yearly analytics aggregations with continuous calendar-day breakdowns scoped to authenticated user.
- [x] CSV and PDF expense report export streams via ReportLab scoped to authenticated user.
- [x] Dynamic cross-origin cookie support (`SameSite=None; Secure=True`) for production domain separation (Vercel ↔ Render).

---

### 4. Frontend Architecture, UI & Design System (`frontend/`)
- [x] Next.js 14 App Router layout with `Plus Jakarta Sans` typography and responsive viewport configuration.
- [x] Dual-mode Light & Dark theme system (`next-themes`, `ThemeToggle`, reactive `.glass-panel` and `.glass-card` styling).
- [x] In-memory access token storage with automatic silent 401 retry interceptor.
- [x] `AuthProvider` and `ProtectedRoute` for global session management and private route guarding.
- [x] Complete auth pages:
  - `/login`: Email/password and official Google GIS sign-in button with registration confirmation banner.
  - `/register`: Registration form with real-time password strength indicator, redirecting to login.
  - `/forgot-password`: Email-only password recovery with 404 validation for unregistered emails.
  - `/reset-password`: Single-use token validation and session invalidation.
- [x] Settings page with Category Management and Account & Security tab (Profile, Password Change, Logout All Devices).
- [x] Sidebar user profile badge and one-click sign out.
- [x] Multi-device responsiveness (mobile top app bar `MobileNav.tsx`, slide-over drawer, stacked transaction cards, and keyboard-safe modal dialogs).
- [x] Progressive Web App (PWA) setup with Web App Manifest and offline Service Worker.

---

### 5. Containerization & Production Deployment
- [x] Backend Docker container (`python:3.11-slim`) with automated Alembic migration runner.
- [x] Frontend multi-stage Docker container (`node:20-alpine`) with non-root security execution.
- [x] Root `docker-compose.yml` for unified local/production orchestration.
- [x] Live cloud deployments on Render (FastAPI) and Vercel (Next.js).

---

## 🚀 Upcoming Enhancements (V2.1 Roadmap)

1. **Multi-Currency Support & Regional Formatting**:
   - Base currency preference selector in `/settings` (INR `₹`, USD `$`, EUR `€`, GBP `£`, CAD `$`, AUD `$`, JPY `¥`).
   - Dynamic locale formatting throughout Dashboard, Expense tables, Budget cards, and PDF exports.
2. **Recurring Subscriptions & Scheduled Expenses**:
   - Automated recurring expense tracker for monthly bills (rent, streaming services, utilities).
   - Upcoming bill alerts on the dashboard.
3. **Receipt & Invoice OCR Upload**:
   - Image attachment upload (PNG, JPG, PDF) with optical character recognition to extract total amount and merchant automatically.
4. **Push Notifications & Budget Alert Thresholds**:
   - Web push notification alerts when monthly category spending crosses 80% or 100% of budget goals.
