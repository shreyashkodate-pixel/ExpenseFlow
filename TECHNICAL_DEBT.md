# ExpenseFlow — Pending Work & Technical Roadmap

**Last Updated:** August 31, 2026

This document tracks completed features, system architecture status, and technical roadmap items for ExpenseFlow.

---

## 📋 Completed Core Tasks

### 1. Backend Core & Database (`backend/app/core/`, `models/`, `seed/`, `alembic/`)
- [x] Configured environment variables via `pydantic-settings` (`DATABASE_URL`, `CORS_ORIGINS`, `API_V1_PREFIX`).
- [x] Implemented SQLAlchemy engine, declarative models (`Category`, `Expense`, `Budget`), and session dependencies.
- [x] Executed Alembic database migration (`48cef29c36e8_initial_schema`) with automatic seeding on startup.
- [x] Configured Supabase PostgreSQL production cloud database with connection pooling.

---

### 2. Services & API Layer (`backend/app/services/` & `routers/v1/`)
- [x] Paginated Expense CRUD with multi-field search, date/category/amount/method filtering, and sorting.
- [x] Category CRUD with in-use reassignment protection (`?reassign_to=`).
- [x] Monthly and Category-specific budget limits with real-time status utilization calculation (`on_track`, `warning`, `exceeded`).
- [x] Daily, Monthly, and Yearly analytics aggregations with continuous calendar-day breakdowns.
- [x] CSV and PDF expense report export streams via ReportLab.
- [x] Configured Starlette CORS regex matching Vercel and Render dynamic production & preview domains.

---

### 3. Frontend Architecture, UI & Design System (`frontend/`)
- [x] Next.js 14 App Router layout with `Plus Jakarta Sans` typography and responsive viewport configuration.
- [x] Dual-mode Light & Dark theme system (`next-themes`, `ThemeToggle`, reactive `.glass-panel` and `.glass-card` styling).
- [x] Full multi-device responsiveness:
  - Mobile top app bar (`MobileNav.tsx`) with animated slide-over menu drawer (`Sidebar.tsx`).
  - Mobile stacked glass transaction cards + tablet/desktop horizontal overflow data tables.
  - Keyboard-safe scrollable modal dialogs (`max-h-[90vh] overflow-y-auto`).
  - Responsive Recharts analytics charts with adaptive radiuses and height breakpoints.
- [x] Progressive Web App (PWA) setup:
  - Web App Manifest (`manifest.json`) for standalone native-like mobile execution.
  - Offline Service Worker (`sw.js`).
  - In-app install banner, sidebar install button, and iOS Home Screen guidance modal.

---

### 4. Containerization & Production Deployment
- [x] Backend Docker container (`python:3.11-slim`) with automated Alembic migration runner.
- [x] Frontend multi-stage Docker container (`node:20-alpine`) with non-root security execution.
- [x] Root `docker-compose.yml` for unified local/production orchestration.
- [x] Live cloud deployments on Render (FastAPI) and Vercel (Next.js).

---

### 5. API Testing & Postman Collection
- [x] Standardized Postman Collection v2.1.0 ([`docs/ExpenseFlow.postman_collection.json`](file:///Users/apple/Documents/Projects/ExpenseFlow/docs/ExpenseFlow.postman_collection.json)) covering all 18 endpoints across Health, Categories, Expenses, Budgets, and Dashboard/Analytics.
- [x] Verified parameter validation, category in-use reassignment safeguards (`INVALID_REASSIGNMENT`), and PDF/CSV export streams.

---

## 🚀 Optional Future Enhancements (V2 Roadmap)

1. **Multi-Currency Support**:
   - Allow users to configure their base currency (e.g. USD `$`, EUR `€`, GBP `£`, INR `₹`) in Settings.
2. **Recurring Subscriptions & Scheduled Expenses**:
   - Automated recurring expense generator for recurring monthly bills (rent, streaming services, utilities).
3. **Receipt & Invoice OCR Upload**:
   - Image attachment upload with optical character recognition to extract total amount and merchant automatically.
4. **Push Notifications**:
   - Web push notification alerts when monthly category spending crosses the 80% budget threshold.
