# ExpenseFlow — Pending Work & Technical Roadmap

**Last Updated:** September 3, 2026

This document tracks completed features, system architecture status, operational considerations, and technical roadmap items for ExpenseFlow.

---

## 📋 Completed Core Tasks

### 1. Backend Core & Database (`backend/app/core/`, `models/`, `seed/`, `alembic/`)
- [x] Configured environment variables via `pydantic-settings` (`DATABASE_URL`, `CORS_ORIGINS`, `API_V1_PREFIX`, `JWT_SECRET_KEY`, `COOKIE_SECURE`, `GOOGLE_CLIENT_ID`, `SMTP_*`, `FRONTEND_URL`).
- [x] Implemented SQLAlchemy engine, declarative models (`User`, `RefreshToken`, `PasswordResetToken`, `EmailVerificationToken`, `Category`, `Expense`, `Budget`), and session dependencies.
- [x] Executed Alembic database migrations:
  - `48cef29c36e8_initial_schema`
  - `7a8e9f1b2c3d_auth_and_user_isolation`
  - `8b9f0e2a3c4d_email_verification_tokens`
- [x] Configured PostgreSQL production database with connection pooling and idempotent category seeding.

---

### 2. Authentication, Verification & User Data Isolation (`backend/app/services/` & `routers/v1/auth.py`)
- [x] Short-lived (15-minute) signed JWT Access Tokens + long-lived (14-day) HttpOnly/Secure Refresh Tokens.
- [x] Refresh Token Rotation (RTR) and Token Reuse Detection with instant user session invalidation.
- [x] Password hashing using native BCrypt (12 work rounds) and SHA-256 token hashing for database storage.
- [x] Complete auth endpoint suite (13 endpoints): `/register`, `/verify-email`, `/resend-verification`, `/login`, `/google`, `/refresh`, `/logout`, `/logout-all`, `/me`, `/change-password`, `/forgot-password`, `/reset-password`.
- [x] **Mandatory Email Verification Workflow**:
  - Accounts created unverified (`is_verified=False`).
  - 24-hour single-use token sent via verification email link.
  - Unverified logins blocked with `403 EMAIL_NOT_VERIFIED`.
  - Account activation via `/verify-email` sets `is_verified=True`, creates session, and dispatches Welcome Email.
- [x] Google Identity Services (GIS) OpenID Connect integration with audience verification, account linking, and auto-verification.
- [x] Branded transactional email delivery (`email_service.py`) for Account Verification, Welcome Onboarding, and Password Reset.
- [x] Strict user data isolation across all expenses, budgets, custom categories, dashboard summaries, analytics, and PDF/CSV exports.
- [x] 100% passing automated test suite (**32/32 tests**) in `backend/tests/`.

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
  - `/login`: Email/password and official Google GIS sign-in button with registration confirmation banner and 1-click unverified resend link.
  - `/register`: Registration form with real-time password strength indicator, transitioning to "Verify Your Email" screen.
  - `/verify-email`: Automated activation route with animated confirmation and inline resend option.
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

## ⚠️ Operational Considerations & Technical Debt

1. **Resend Sandbox vs. Custom Domain (Critical for Production User Signups)**:
   - *Status*: The production setup currently uses `onboarding@resend.dev`.
   - *Limitation*: In Resend's free/sandbox mode, outgoing emails are restricted **strictly** to the account owner's email address. Any registration from an external email address is rejected by Resend with `451: You can only send to your verified email address while in sandbox mode`.
   - *Action Item*: Configure and verify a custom domain (e.g. `expenseflow.app` or user-owned domain) in the Resend dashboard by adding DKIM, SPF, and DMARC DNS records. Once verified, update `SMTP_FROM_EMAIL=noreply@yourdomain.com`.

2. **Background Email Task Reliability & Queuing**:
   - *Status*: Transactional emails are currently queued using FastAPI's in-process `BackgroundTasks`.
   - *Limitation*: If the server container restarts while a task is queued, or if the SMTP connection hangs, workers may experience delays.
   - *Action Item*: As traffic scales, move email delivery to an asynchronous task queue (e.g., Celery/ARQ with Redis) or use Resend's REST API with async `httpx` instead of synchronous SMTP connection pools.

3. **Frontend Resend Cooldown Timer**:
   - *Status*: Basic rate limiting is enforced on the backend endpoint (`5 requests / 60 seconds`).
   - *Enhancement*: Add a visual 60-second cooldown timer on the frontend "Resend Verification Email" button to prevent repeated clicks and provide clear user feedback.

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

