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

### 6. AI Financial Intelligence Suite (`backend/app/services/ai/`, `routers/v1/ai.py`, `frontend/components/ai/`)
- [x] **Smart Spending Insights & Actionable Saving Tips (Step 1)**: 7-day category surge detection, dynamic 0–100 Financial Health Score, and monthly ₹ saving opportunities.
- [x] **Predictive Budget Overspending Alerts & Velocity Pacing (Step 2)**: Daily burn rate (₹/day), exact exhaustion calendar date prediction, and safe daily ceiling calculation.
- [x] **Subscription & Recurring Expense Audit (Step 3)**: 90-day recurring merchant pattern detection (Netflix, Spotify, Gym, Wi-Fi, Rent, SIPs) and monthly overhead quantification.
- [x] **50/30/20 Budget Optimization Rule (Step 4)**: Automated Needs (50%), Wants (30%), and Savings (20%) mapping with segmented 3-color progress meter and rebalancing advice.
- [x] **"Ask ExpenseFlow AI" Conversational Assistant (Step 5 Structured RAG)**: Live database facts injection, strict finance-only scope guardrails, 1-click follow-up chips, and global slide-out drawer (`AIChatDrawer.tsx`).
- [x] **Multi-Provider Adapter Engine**: Unified interface (`BaseAIProvider`) supporting Google Gemini, OpenAI, Anthropic Claude, and local Rule-engine.
- [x] **Multi-Model Auto-Rotation & Failover**: Automatic rotation across `gemini-3.5-flash`, `gemini-3.7-flash`, and `gemini-3.6-flash` upon 429 quota limits or 503 high-demand spikes.
- [x] **Intelligent Question-Aware Fallback**: Offline rule engine computing answers dynamically from live database records if external APIs are unreachable.
- [x] **100% Passing AI Test Suite**: 7/7 AI automated tests passing (`39/39` total backend tests).

---

## ⚠️ Operational Considerations & Technical Debt

1. **Google Gemini Free-Tier Quota & Multi-Model Failover (Resolved)**:
   - *Status*: Google Gemini free tier enforces a strict per-model daily quota limit (20 requests/day for preview/flash models).
   - *Resolution*: Implemented dynamic multi-model rotation in [`backend/app/services/ai/gemini_provider.py`](file:///Users/apple/Documents/Projects/ExpenseFlow/backend/app/services/ai/gemini_provider.py) that seamlessly cycles through `gemini-3.5-flash`, `gemini-3.7-flash`, and `gemini-3.6-flash` when encountering 429, 404, or 503 errors. Additionally, an intelligent local rule engine serves as a fallback to guarantee 100% platform availability with zero generic static responses.

2. **Resend Sandbox vs. Custom Domain (Critical for Production User Signups)**:
   - *Status*: The production setup currently uses `onboarding@resend.dev`.
   - *Limitation*: In Resend's free/sandbox mode, outgoing emails are restricted **strictly** to the account owner's email address. Any registration from an external email address is rejected by Resend with `451: You can only send to your verified email address while in sandbox mode`.
   - *Action Item*: Configure and verify a custom domain (e.g. `expenseflow.app` or user-owned domain) in the Resend dashboard by adding DKIM, SPF, and DMARC DNS records. Once verified, update `SMTP_FROM_EMAIL=noreply@yourdomain.com`.

3. **Render Free Tier Port Block & Resend REST API (Resolved)**:
   - *Status*: Render Free Tier blocks outbound ports 25, 465, and 587.
   - *Resolution*: Implemented Resend HTTPS REST API delivery via `httpx` (Port 443) in [`backend/app/services/email_service.py`](file:///Users/apple/Documents/Projects/ExpenseFlow/backend/app/services/email_service.py). Outbound verification codes and welcome emails bypass SMTP socket restrictions.

4. **AI Rate Limiting & Response Caching**:
   - *Status*: `/api/v1/ai/recommendations` utilizes a 1-hour in-memory cache to prevent redundant LLM API calls.
   - *Protection*: Rate-limited at 60 req/min for cached reads, 5 req/min for forced re-analysis (`/refresh`), and 15 req/min for conversational chat (`/chat`).

---

## 🚀 Upcoming Enhancements (V2.1 Roadmap)

1. **Multi-Currency Support & Regional Formatting**:
   - Base currency preference selector in `/settings` (INR `₹`, USD `$`, EUR `€`, GBP `£`, CAD `$`, AUD `$`, JPY `¥`).
   - Dynamic locale formatting throughout Dashboard, Expense tables, Budget cards, and PDF exports.
2. **Receipt & Invoice OCR Upload**:
   - Image attachment upload (PNG, JPG, PDF) with optical character recognition to extract total amount and merchant automatically into expense fields.
3. **Web Push Notifications**:
   - Browser push notification alerts when monthly category spending crosses 80% or 100% of budget goals.


