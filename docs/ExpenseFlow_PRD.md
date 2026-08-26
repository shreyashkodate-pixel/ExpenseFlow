# Product Requirements Document (PRD)
## ExpenseFlow — Personal Expense & Budget Tracker
*(Merged from FinTrack PRD + Expense Tracker PRD — best of both)*

**Document Version:** 1.0 (Merged)
**Status:** Draft
**Platform:** Responsive Web App

---

## 1. Overview

**Summary:** ExpenseFlow is a personal finance web app that lets a user log daily expenses into categories they define themselves, instantly see the impact on totals, charts, and a live budget, and get proactive alerts before they overspend — turning scattered notes/spreadsheet habits into one searchable, analytics-driven place to track spending.

**Tech Stack:** Next.js + TypeScript + Tailwind CSS + shadcn/ui + Recharts (frontend) · FastAPI + Pydantic + SQLAlchemy + Alembic (backend) · PostgreSQL (database)

---

## 2. Problem Statement

Most people don't track expenses properly — they forget to log them, or use notes/spreadsheets that are hard to search or understand at a glance. As a result, they can't easily answer:

- "How much have I spent?"
- "Where is my money going?"
- "Am I within budget, or over it?"
- "Is this month better or worse than last month?"

ExpenseFlow solves this with one place to log expenses, dynamic categories that match how the user actually thinks about spending, and a dashboard that turns raw entries into real insight and proactive budget alerts.

---

## 3. Product Vision

> **Record → Organize → Analyze → Budget → Improve**

V1 focuses only on this core loop. Login, recurring expenses, bank sync, multi-currency, and notifications infrastructure are deferred to later phases (Section 14) — this keeps V1 simple to build, test, and actually use.

---

## 4. Goals & Success Metrics

| Goal | Why It Matters |
|---|---|
| Add an expense in under 30 seconds | Easy logging = the user keeps using it |
| Show spending visually, at multiple time grains | Understand "where money is going" without effort |
| Show a live remaining budget with proactive alerts | Turns tracking into real budgeting, not just note-taking |
| Make old expenses easy to find | A log is useless if you can't search/filter/sort it |
| Build on a clean, scalable architecture | Later phases shouldn't require rebuilding the core |

**Success Metrics:**
- Expenses logged per active user per week
- % of users who set a budget goal
- Time to add a single expense (target: <30s)
- Search/filter usage frequency
- 30-day retention

---

## 5. Target Users & Persona

**Primary:** An individual (e.g., a student or budget-conscious professional) who wants to manually track their own spending, stay under a monthly budget, and understand spending patterns without a complex finance platform.

**Pain points:** Forgets small expenses; doesn't know which category eats the most money; struggles to stay within budget; finds full finance apps overkill.

**Not for V1:** Teams/families sharing an account, businesses, investment tracking.

---

## 6. Scope

### ✅ In Scope (V1)
- Full expense CRUD (Add / View / Detail / Edit / Delete)
- **User-defined dynamic categories** (create/rename/delete — not a fixed enum), with starter categories pre-seeded in the backend database and fetched dynamically via API (never hardcoded in frontend)
- Payment method tagging (Cash, GPay, Credit Card, UPI, Bank Transfer, Others, etc. — tagging only; online payment gateway processing is out of scope)
- Dashboard: summary cards, category pie/donut chart, monthly trend chart, budget progress, recent + highest expenses
- Daily / Monthly / Yearly analytics views
- Search (description, category, payment method) + Filters (category, payment method, amount range, date range, quick filters like Today/This Week/This Month/Last Month) + Sort (newest, oldest, highest, lowest) — usable together
- Pagination (20/page)
- Budget: overall monthly + optional per-category, with live remaining-balance and color-coded status
- Rule-based spending alerts (no notification infra required)
- Light/dark mode
- Full field validation, and empty/loading/error/no-results/success states everywhere
- Single fixed currency (₹ INR, 2 decimals)
- **CSV and PDF export**

### ❌ Out of Scope (V1)
- Login / multi-user accounts / auth (single-user app; see Section 11 risk note)
- Online payment gateway integrations (no payment processing/gateways)
- Multiple currencies, bank/UPI/SMS auto-import, income tracking
- Recurring expenses, push/email notifications
- Native mobile app (responsive web only)
- Excel export (CSV and PDF are included in V1)

---

## 7. Functional Requirements

### 7.1 Navigation
| ID | Requirement | Priority |
|---|---|---|
| FR-1 | Primary nav: Dashboard · Expenses · Analytics · Budget · Settings. "Add Expense" accessible from Dashboard and Expenses. | P0 |

### 7.2 Expense Fields & Validation
Fields: Amount, Category (dynamic, pick-or-create), Description/Title (required, ≤50 chars), Date (defaults today, no future dates), Payment Method (optional), Notes (optional).

| Rule | Why |
|---|---|
| Amount must be a positive number | Prevents bad data skewing totals/charts |
| Date cannot be in the future | Keeps the log honest |
| Description required, max 50 chars | Keeps the list scannable |

### 7.3 Expense CRUD
| ID | Action | Priority | User Story |
|---|---|---|---|
| FR-2 | Add | P0 | As a user, I want to quickly add an expense so logging doesn't feel like a chore. |
| FR-3 | View (paginated list) | P0 | As a user, I want to view my past expenses to review my history. |
| FR-4 | View Details (modal/dialog) | P0 | As a user, I want to open one expense and see its full detail without a page change. |
| FR-5 | Edit | P0 | As a user, I want to correct a past expense so my records stay accurate. |
| FR-6 | Delete (with confirmation) | P0 | As a user, I want to delete an expense safely, without losing data by accident. |

### 7.4 Category Management (dynamic — key differentiator)
| ID | Action | Priority | User Story |
|---|---|---|---|
| FR-7 | Create category inline while logging an expense, or from a category list | P0 | So my spending is organized the way I actually think about it. |
| FR-8 | Rename a category | P0 | So I can keep organization consistent over time. |
| FR-9 | Delete a category — only if unused, or reassign/cascade with a warning | P0 | So I don't accidentally orphan expense data. |
| FR-10 | View category list with expense counts | P1 | So I understand my category usage. |
| FR-11 | Ship with starter categories (Food, Transport, Rent, Shopping, Bills, Entertainment, Health, Education, Other) seeded in the database and fetched via API (never hardcoded in frontend) | P2 | So the app isn't empty on first use. |

### 7.5 Search, Filter & Sort
| ID | Requirement | Priority |
|---|---|---|
| FR-12 | Search by description, category, payment method | P0 |
| FR-13 | Filter by category, payment method, amount range, date range | P0 |
| FR-14 | Quick filters: Today / This Week / This Month / Last Month / This Year / Custom Range | P1 |
| FR-15 | Sort: newest, oldest, highest amount, lowest amount | P0 |
| FR-16 | All of the above usable together, backend-paginated (20/page) | P0 |

### 7.6 Dashboard
| ID | Requirement | Priority |
|---|---|---|
| FR-17 | Summary cards: total spent, this month, today, remaining budget, highest expense, top category | P0 |
| FR-18 | Recent expenses list (snapshot) | P0 |
| FR-19 | Pie/donut chart — category breakdown, interactive (hover shows name/amount/%) | P0 |
| FR-20 | Bar/line chart — spending over time | P0 |
| FR-21 | Budget progress with color status | P0 |
| FR-22 | Month-over-month comparison with % change | P1 |
| FR-23 | Top categories ranked, average daily/weekly spend | P2 |

### 7.7 Analytics
| ID | Requirement | Priority |
|---|---|---|
| FR-24 | Daily spending (bar chart) | P1 |
| FR-25 | Monthly spending trend | P0 |
| FR-26 | Yearly spending across months of a selected year | P1 |
| FR-27 | Category breakdown: total, % of spend, highest category | P0 |

### 7.8 Budget & Alerts
The user sets a monthly (and optionally per-category) limit. The app shows spent-so-far, remaining = goal − spent, and a color status.

| Usage | Status | Color |
|---|---|---|
| < 85% | On track | Green |
| 85%–99.99% | Near limit | Yellow |
| ≥ 100% | Over budget | Red |

| ID | Requirement | Priority |
|---|---|---|
| FR-28 | Set overall + per-category budget; live remaining-balance updates on every add | P0 |
| FR-29 | Alert: budget warning at ~80% usage | P1 |
| FR-30 | Alert: budget exceeded at ≥100% | P1 |
| FR-31 | Alert: category spend higher than previous month | P2 |
| FR-32 | Alerts calculated dynamically — no separate notification table/service needed | P0 |

### 7.9 Export
| ID | Requirement | Priority |
|---|---|---|
| FR-33 | Export filtered or full expense list as CSV or PDF (date, category, amount, payment method, description) | P2 |

### 7.10 Data Integrity Principle
| ID | Requirement | Priority |
|---|---|---|
| FR-34 | No hardcoded/demo data at any stage — all data dynamically created, stored, and fetched from the real data layer | P0 |

---

## 8. Key User Flows

| Flow | Steps |
|---|---|
| Add an expense | Expenses → Add New → pick/create category → Save → appears in list, dashboard updates live |
| Check spending | Dashboard → totals, charts, budget status, alerts |
| Find a past expense | Expenses → Search/Filter/Sort → Edit or Delete |
| Set a budget | Budget → set limit → Dashboard shows live remaining + color status + alerts as spend approaches limit |

---

## 9. Non-Functional Requirements

**Performance:** Pagination on all lists; dashboard avoids unnecessary API calls; charts render efficiently even at scale; no hardcoded/static values at any data volume.

**Reliability:** Database operations handled safely; API errors return proper HTTP status codes (200/201/400/404/422/500); frontend converts technical errors into user-facing messages; each phase fully functional (run → test → deploy) before the next begins.

**Security:** Even without auth in V1 — validate all API inputs; no hardcoded DB credentials (use env vars); CORS configured appropriately; sensitive DB details never exposed to frontend.

**Maintainability:** Backend modular (routers / services / schemas / models separated); SQLAlchemy models separate from Pydantic schemas; migrations via Alembic; frontend components reusable.

**Scalability:** Architecture supports later phases (Section 14) without major rework.

**Responsiveness:** Works across desktop, tablet, and mobile browsers; tables remain usable on small screens.

**Deployment (V1):** Local/private deployment — no public internet exposure, since there's no auth layer yet.

---

## 10. Technical Architecture

```
FRONTEND (Next.js + TS + Tailwind + shadcn/ui + Recharts)
        │  REST API / JSON
        ↓
BACKEND (FastAPI + Pydantic + SQLAlchemy + Alembic)
        │  SQL
        ↓
PostgreSQL
```

### Core API Surface
| Method | Endpoint | Description |
|---|---|---|
| POST/GET/PUT/DELETE | `/api/expenses`, `/api/expenses/{id}` | Expense CRUD |
| GET | `/api/dashboard` | Dashboard summary |
| GET | `/api/analytics/{daily\|monthly\|yearly\|categories}` | Analytics |
| POST/GET/PUT/DELETE | `/api/categories`, `/api/categories/{id}` | Category CRUD |
| GET/POST/PUT/DELETE | `/api/budget` | Budget CRUD |
| GET | `/api/expenses/export` | CSV and PDF export (`?format=csv` or `?format=pdf`) |

### Core Tables
`expenses` (id, amount, category_id, description, date, payment_method, timestamps) · `categories` (id, name, created_at) · `budgets` (id, month, year, amount, category_id nullable, timestamps). Analytics and alerts are calculated dynamically, not stored.

---

## 11. Assumptions & Risks

**Assumptions:** Single-user app, no login in V1; one fixed currency (INR); budget defaults to monthly; expense dates today-or-earlier only; local/private deployment.

**Risks:**
- **No data isolation** — without auth, this is single-user only; converting to a real multi-user product later requires adding auth and user ownership (flagged explicitly for that phase)
- Scope creep if later-phase features get pulled into V1
- Data accuracy risk if any hardcoded/test data survives into deployment

---

## 12. Definition of Done (V1)

- Full expense CRUD, dynamic categories (create/rename/delete), payment methods (tagging only)
- Dashboard with total spend, recent + highest expenses, ≥2 charts, budget status
- Daily/monthly/yearly analytics with category breakdown
- Search + filters (incl. quick filters) + sort, all usable together, paginated
- Budget goal (overall + per-category) with live balance, color status, and rule-based alerts
- CSV and PDF export
- Light/dark mode; responsive across devices
- Full validation + empty/loading/error/no-results/success states
- No hardcoded/demo data anywhere (frontend fetches categories and expenses dynamically from backend DB)
- Deployed and tested end-to-end before Phase 2

---

## 13. Stakeholders

- Product Owner · Development Team · QA/Testing Team · End Users (primary feedback source per phase)

---

## 14. Future Scope — Phase-wise Roadmap

| Phase | Theme | Key Features |
|---|---|---|
| **Phase 1 (V1)** | Core Loop | CRUD, dynamic categories, dashboard + analytics, search/filter/sort, budget + alerts, CSV & PDF export |
| **Phase 2** | Auth & Convenience | Login & multi-device sync, user-level data isolation, income tracking, recurring expenses, receipt upload, multiple wallets, Excel export |
| **Phase 3** | Social/Sharing | Split expenses, shared budgets, multi-user/family accounts, role-based access |
| **Phase 4** | Smart & Advanced | Savings goals, multi-currency, AI spend prediction, auto-categorization, bank/UPI/SMS auto-import, calendar heatmap, year-view trends |
| **Phase 5** | Security & Personalization | Biometric lock, cloud backup, custom themes, push/email notifications |
| **Phase 6** | Monetization | Free vs Premium plans, ads (free tier) |

*Each phase follows Run → Test → Deploy before the next begins.*

---

## 15. Dependencies

- PostgreSQL for persistent storage
- Recharts for dashboard/analytics visualizations
- Auth mechanism (introduced Phase 2 onward)
- Export libraries for CSV & PDF (V1); Excel export (Phase 2)
- Notification system (Phase 5)
