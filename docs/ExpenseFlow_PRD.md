# Product Requirements Document (PRD)
## ExpenseFlow — Personal Expense & Budget Tracker

**Document Version:** 2.0  
**Status:** Approved & Active  
**Platform:** Responsive Web App & Progressive Web App (PWA)

---

## 1. Overview

**Summary:** ExpenseFlow is a smart, privacy-focused personal finance web application that allows users to create personal accounts, log daily expenses into dynamic categories, track real-time budgets with proactive visual alerts, analyze spending habits over time, and export financial reports. Each user has their own private space with complete data privacy and security.

**Core Capabilities:**
- Personal user accounts (Email/Password registration and fast Google Sign-In).
- Private and secure expense logging, editing, and categorizing.
- Real-time budget progress with color-coded spending alerts.
- Interactive daily, monthly, and yearly analytics trends.
- Automated CSV and PDF expense report exports.
- Mobile-friendly Progressive Web App (PWA) with light and dark themes.

---

## 2. Problem Statement

Most individuals struggle to manage their personal finances because manual note-taking or spreadsheets are tedious, hard to search, lack visual insight, and offer no proactive budget guidance. Furthermore, shared or unauthenticated apps risk exposing private financial records.

Users need answers to essential financial questions:
- *"How much did I spend this month, this week, or today?"*
- *"Which categories are consuming the largest share of my budget?"*
- *"Am I on track with my monthly budget, or approaching my spending limit?"*
- *"Can I securely access my private records across all my personal devices?"*

ExpenseFlow solves this with a fast, private, and intuitive experience designed to make expense tracking effortless.

---

## 3. Product Vision

> **Sign In → Record → Organize → Budget → Analyze → Improve**

The product is built around a frictionless daily logging loop backed by strong account privacy, ensuring users can access their financial records securely from anywhere without complicated setup.

---

## 4. Goals & Success Metrics

| Goal | Why It Matters |
|---|---|
| **Fast Logging (<30 seconds)** | Low friction ensures users stay consistent with expense logging. |
| **Instant Account Access** | Sign in easily with Email/Password or 1-click Google Sign-In. |
| **Strict Privacy & Isolation** | Every user’s financial records remain completely private and confidential. |
| **Clear Visual Budgeting** | Live progress bars and status indicators prevent month-end overspending. |
| **Effortless Search & Export** | Quick filters, sorting, and one-click PDF/CSV reports make reviewing painless. |

**Key Success Metrics:**
- Weekly active users and expenses logged per user.
- Account retention and multi-device sign-in rate.
- % of users who configure a monthly budget target.
- Search, filter, and report download frequency.

---

## 5. Target Users & Persona

* **Primary Persona:** College students, freelancers, working professionals, and budget-conscious individuals who want a clean, distraction-free tool to track personal spending and stay within budget.
* **Core Needs:** Fast mobile and desktop logging, private personal account, clear visual summaries, custom categories, and painless report generation.
* **Privacy Requirement:** Multiple users can use the platform independently; no user can ever see or modify another user's financial entries.

---

## 6. Product Scope

### ✅ Included in Product
* **User Accounts & Security:**
  * User registration (Sign Up) and login (Sign In) with email and password.
  * One-click **Sign in with Google** (Google OAuth).
  * Password recovery lifecycle (Forgot Password request & Reset Password).
  * In-app password change and account profile management.
  * Secure sign-out and "Sign out from all devices" option.
  * Automatic session continuation without unexpected logouts.
* **Expense Management:**
  * Add, view, search, filter, edit, and delete private expenses.
  * Dynamic categories (built-in starter categories + user's own custom categories).
  * Payment method tags (*Cash, GPay, Credit Card, UPI, Bank Transfer, Others*).
  * Date selection, amount, notes, and receipt descriptions.
* **Budgeting & Visual Alerts:**
  * Monthly overall spending targets and category-specific budget limits.
  * Live remaining balance updates on every entry.
  * Color-coded status indicators (*On Track, Near Limit, Over Budget*).
* **Analytics & Reports:**
  * Interactive summary dashboard with cards and breakdown charts.
  * Daily, Monthly, and Yearly spending trend views.
  * Category distribution breakdowns.
  * Instant **CSV and PDF export** for any filtered date range or category.
* **Experience & Multi-Device Support:**
  * Light and dark theme toggle.
  * Full mobile responsiveness with slide-over drawer and mobile card layouts.
  * Progressive Web App (PWA) installation for Android, iOS, and desktop.

### ❌ Out of Scope
* Payment processing or merchant gateways (the app records payments; it does not process financial transactions).
* Multi-user shared joint accounts / shared household ledgers (each account is private).
* Bank account direct syncing or automated SMS scrapers.

---

## 7. Functional Requirements

### 7.1 User Account & Security Management
| ID | Requirement | Description |
|---|---|---|
| **FR-A1** | **Sign Up / Register** | Users can create an account using their email address, password, and optional full name. |
| **FR-A2** | **Sign In / Login** | Users can log into their account securely with their registered credentials. |
| **FR-A3** | **Sign in with Google** | Users can instantly create or sign in to their account using their Google account. |
| **FR-A4** | **Forgot Password** | Users who forget their password can request a secure reset link/token sent to their email. |
| **FR-A5** | **Reset Password** | Users can safely set a new password using their verified reset link. |
| **FR-A6** | **Change Password** | Authenticated users can update their account password from the Settings page. |
| **FR-A7** | **Secure Sign Out** | Users can sign out of their current session with one click. |
| **FR-A8** | **Sign Out All Devices** | Users can terminate all active sessions across all devices for security. |
| **FR-A9** | **User Data Isolation** | Each user only sees and manages their own expenses, budgets, and custom categories. |

### 7.2 Navigation & Layout
| ID | Requirement | Description |
|---|---|---|
| **FR-1** | **Primary Navigation** | Accessible navigation across Dashboard, Expenses, Analytics, Budget Goals, and Settings, plus user profile avatar and quick Sign Out. |
| **FR-2** | **Protected Access** | Unauthenticated visitors attempting to access app features are automatically guided to the Sign In page. |

### 7.3 Expense Logging & Management
| ID | Requirement | Description |
|---|---|---|
| **FR-3** | **Add Expense** | Quick form with Amount (>0), Category selection, Title (≤50 chars), Date (up to today), Payment Method, and Notes. |
| **FR-4** | **View Expenses** | Paginated list with desktop table and mobile cards displaying all user-logged transactions. |
| **FR-5** | **Edit Expense** | Modal to edit any previous transaction, updating charts and totals instantly. |
| **FR-6** | **Delete Expense** | Safe deletion with confirmation dialog. |

### 7.4 Category Organization
| ID | Requirement | Description |
|---|---|---|
| **FR-7** | **Starter Categories** | Built-in starter categories (*Food, Transport, Rent, Shopping, Bills, Entertainment, Health, Education, Other*). |
| **FR-8** | **Custom Categories** | Users can create their own custom categories matching their personal spending habits. |
| **FR-9** | **Category Management** | Users can rename or delete their custom categories, with reassignment options if expenses exist. |

### 7.5 Search, Filters & Sorting
| ID | Requirement | Description |
|---|---|---|
| **FR-10** | **Multi-Field Search** | Search expenses by title, category, or payment method. |
| **FR-11** | **Dynamic Filters** | Filter by category, payment method, amount range, and date range (*Today, This Week, This Month, Custom*). |
| **FR-12** | **Sorting** | Sort by newest, oldest, highest amount, or lowest amount. |

### 7.6 Dashboard & Spending Insights
| ID | Requirement | Description |
|---|---|---|
| **FR-13** | **Summary Cards** | Total spent this month, today's spending, remaining budget, and highest transaction. |
| **FR-14** | **Interactive Charts** | Visual category donut chart and monthly spending comparison graph. |
| **FR-15** | **Recent Transactions** | Snapshot list of recent 5 expenses for quick review. |

### 7.7 Budget Goals & Spending Alerts
| ID | Requirement | Description |
|---|---|---|
| **FR-16** | **Monthly Budget Target** | Set an overall monthly spending ceiling and optional category-specific targets. |
| **FR-17** | **Visual Status Alerts** | Color-coded feedback: Green (*On Track <80%*), Yellow (*Near Limit 80–99%*), Red (*Over Budget ≥100%*). |

### 7.8 Export & Reports
| ID | Requirement | Description |
|---|---|---|
| **FR-18** | **CSV Export** | Download spreadsheet-compatible CSV file containing all filtered expenses. |
| **FR-19** | **PDF Report Export** | Generate formatted PDF financial summary document with transaction records. |

---

## 8. Key User Journeys

```
Journey 1: Getting Started
[Visit App] ──> [Sign Up or Sign in with Google] ──> [Land on Dashboard] ──> [Set Monthly Budget]

Journey 2: Daily Expense Logging
[Open App / PWA] ──> [Tap 'Add Expense'] ──> [Select Category & Amount] ──> [Save] ──> [Charts & Budget Update Instantly]

Journey 3: Reviewing & Exporting
[Go to Expenses] ──> [Filter 'This Month' & 'Food'] ──> [Click 'Export PDF'] ──> [Download Statement]

Journey 4: Account Security
[Go to Settings] ──> [Change Password or 'Sign Out All Devices'] ──> [Sessions Invalidated Safely]
```

---

## 9. Non-Functional & Quality Standards

* **Privacy & Isolation:** Strict separation of user records. No user can view or alter data belonging to another account.
* **Speed & Performance:** Pages load quickly; adding an expense updates summaries in real time.
* **Security Standards:** Industry-standard password encryption, secure session tokens, and protected API endpoints.
* **Device Responsiveness:** Works smoothly on mobile phones, tablets, and widescreen desktop monitors.
* **Theme Preference:** Supports both high-contrast Dark Mode and clean Light Mode.

---

## 10. Release & Future Vision

| Phase | Focus | Highlights |
|---|---|---|
| **Current (V2)** | **Complete Personal Platform** | Full expense & budget tracking, analytics, CSV/PDF reports, dark/light theme, PWA, and secure user authentication with Google Sign-In & data isolation. |
| **Future (V3)** | **Smart Finance** | Multi-currency conversions, scheduled recurring expenses, receipt photo scanning (OCR), and budget push notifications. |
