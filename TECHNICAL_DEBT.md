# ExpenseFlow — Pending Work & Technical Roadmap

**Last Updated:** August 27, 2026

This document lists all pending implementation tasks and technical debt items to resume work seamlessly in the next session.

---

## 📋 Pending Tasks & Action Plan

### 1. Backend Core Setup (`backend/app/core/`)
- [x] Implement `core/config.py`: Load `DATABASE_URL` and `CORS_ORIGINS` from `.env` via `pydantic-settings.BaseSettings`, with sensible code defaults for optional parameters (`API_V1_PREFIX`, `APP_NAME`, `APP_ENV`, `SEED_ON_STARTUP`, `LOG_LEVEL`).
- [x] Implement `core/database.py`: Configure SQLAlchemy engine, session maker, and DB dependency `get_db()`.

---

### 2. Models & Schemas (`backend/app/models/` & `backend/app/schemas/`)
- [x] Create SQLAlchemy ORM models:
  - `Category` (`id`, `name`, `created_at`)
  - `Expense` (`id`, `amount`, `category_id`, `description`, `notes`, `date`, `payment_method`, `created_at`, `updated_at`)
  - `Budget` (`id`, `month`, `year`, `amount`, `category_id`, `timestamps`)
- [x] Create Pydantic schemas for request validation & API responses (`ExpenseCreate`, `ExpenseResponse`, `CategoryCreate`, `CategoryResponse`, `BudgetCreate`, `BudgetResponse`, `DashboardSummaryResponse`, `DailyAnalyticsResponse`, `MonthlyAnalyticsResponse`, `YearlyAnalyticsResponse`, `PaginatedResponse`, `ErrorResponse`).

---

### 3. Database Migrations & Seeding (`backend/alembic/` & `backend/app/seed/`)
- [x] Initialize Alembic migration scripts for initial database tables (`48cef29c36e8_initial_schema`).
- [x] Implement `seed/seed_data.py`: Idempotent script to seed default categories (*Food, Transport, Rent, Shopping, Bills, Entertainment, Health, Education, Other*) in DB on first startup.

---

### 4. Services & API Routers (`backend/app/services/` & `backend/app/routers/v1/`)
- [x] Implement `services/expense_service.py` & `routers/v1/expenses.py` (CRUD + Search, Filter, Sort, Pagination).
- [x] Implement `services/category_service.py` & `routers/v1/categories.py` (CRUD + In-use deletion protection/reassignment).
- [x] Implement `services/budget_service.py` & `routers/v1/budgets.py` (Monthly/Per-category budget tracking & remaining balance calculation).
- [x] Implement `services/analytics_service.py` & `routers/v1/analytics.py` & `routers/v1/dashboard.py` (Daily, monthly, yearly trends, top categories, single-call dashboard summary).
- [x] Implement `services/export_service.py` (`/api/v1/expenses/export?format=csv|pdf` file generation via ReportLab / CSV writer).
- [x] Implement `/api/v1/health` and `/health` endpoints.

---

### 5. Frontend Development (`frontend/`)
- [ ] Build shared UI components in `components/ui/` (Buttons, Inputs, Cards, Dialogs, Tables, Toasts).
- [ ] Build typed API client in `lib/api/` (`expenses.ts`, `categories.ts`, `budget.ts`, `analytics.ts`).
- [ ] Build custom hooks (`useExpenses`, `useCategories`, `useBudget`).
- [ ] Construct main pages:
  - `app/page.tsx` (Dashboard summary, charts, budget widget, recent expenses).
  - `app/expenses/page.tsx` (Expense table, search/filter controls, add/edit modal, CSV/PDF export buttons).
  - `app/analytics/page.tsx` (Spending breakdown charts).
  - `app/budget/page.tsx` (Budget goal setup & status alerts).

---

### 6. Automated Testing & Verification
- [x] Write unit tests under `backend/tests/` (`test_health.py`, `test_categories.py`, `test_expenses.py`, `test_budgets.py`, `test_analytics.py`) covering CRUD, search, pagination, category reassignment, budget alert rules, analytics, and exports (11/11 tests passing, 0 Pyright errors).
- [ ] Perform end-to-end frontend integration test.
