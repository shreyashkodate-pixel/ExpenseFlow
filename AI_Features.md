# ExpenseFlow — AI Features Overview

ExpenseFlow includes a full-stack, personal financial intelligence suite designed to analyze user spending, forecast budget run-outs, audit recurring subscriptions, optimize wealth distribution, and provide a conversational financial assistant grounded in live database records.

---

## 🚀 The 5 Core AI Features

### 1. Smart Spending Insights & Actionable Saving Tips
* **Summary**: Automatically analyzes your spending behavior and alerts you when any category surges unusually in the last 7 days compared to past habits. It generates a 0–100 Financial Health Score and provides concrete tips with exact monthly rupee amounts (₹) you can save.
* **Key Highlights**:
  * 7-day category surge detection (e.g., *"+42% spike in Dining Out this week"*).
  * Quantified monthly saving potential (e.g., *"Trim weekend deliveries to save ~₹2,500/month"*).
  * Dynamic Financial Health Score (*Excellent*, *Good*, or *Needs Attention*).

---

### 2. Predictive Budget Overspending Alerts & Burn-Rate Pacing
* **Summary**: Acts as an early-warning radar that calculates your real-time daily burn rate (₹/day) and projects your month-end spend for every active budget. It forecasts the exact calendar date your budget will be exhausted (e.g., *"Exhausts by Sep 19"*) and computes the safe daily spending limit needed to finish the month safely.
* **Key Highlights**:
  * Velocity-based run-rate calculation (`daily_burn_rate = current_spend / days_elapsed`).
  * Exact exhaustion calendar date prediction.
  * Safe daily spending ceiling (`remaining_budget / days_remaining`) to avoid overspending.
  * Visual pacing badges: *Safe*, *Caution*, *Critical*, or *Exceeded*.

---

### 3. Subscription & Recurring Expense Audit
* **Summary**: Scans your past 90 days of transactions to automatically identify recurring charges (Netflix, Spotify, Gym, Wi-Fi, Rent, SIPs) and repeating intervals. It displays your total monthly recurring overhead in ₹ and provides actionable tips on switching to annual discount plans or eliminating duplicate/unused subscriptions.
* **Key Highlights**:
  * Automated merchant and pattern detection across 90 days of transaction history.
  * Total recurring monthly overhead metric (e.g., *"₹4,260/month across 4 active subscriptions"*).
  * Cost-cutting recommendations (annual plan savings, bundle optimization, cancellation of idle services).

---

### 4. 50/30/20 Budget Optimization Rule
* **Summary**: Automatically categorizes all logged expenses into Needs (50%), Wants (30%), and Savings (20%) using an interactive 3-color segmented progress meter. It compares your real-time percentages against the target rule and gives precise rebalancing advice on how much to trim from discretionary spending to hit your 20% savings goal.
* **Key Highlights**:
  * Automated expense classification:
    * **Needs (50%)**: Rent, Groceries, Utilities, Healthcare, Commute.
    * **Wants (30%)**: Dining Out, Food Delivery, Shopping, Entertainment, Travel.
    * **Savings (20%)**: Mutual Funds, SIPs, Emergency Deposits.
  * Segmented 3-color progress meter comparing actual vs target distribution.
  * Tailored rebalancing advice with exact ₹ amount needed to redirect to savings.

---

### 5. "Ask ExpenseFlow AI" Conversational Assistant (Structured RAG)
* **Summary**: A floating, slide-out chatbot that answers questions strictly using your live database facts (monthly totals, category breakdowns, budgets, and subscriptions) with zero mathematical hallucinations. It features strict scope guardrails to filter out non-finance questions, 1-click prompt chips, and dynamic question-specific answers.
* **Key Highlights**:
  * **Structured RAG**: Real database totals, pacing metrics, and recent expenses injected into the LLM context as ground-truth facts.
  * **Scope Guardrails**: Politely declines off-topic questions (trivia, coding, politics, weather) and stays strictly focused on personal finance.
  * **Multi-Model Auto-Rotation**: Automatically rotates across available models (`gemini-3.5-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`) if a provider hits quota limits (429) or temporary spikes (503).
  * **Intelligent Local Fallback**: If external AI APIs are offline, a question-aware rule engine computes answers directly from the database instead of giving a generic static message.

---

## 🛠️ Multi-Provider Support

ExpenseFlow supports multiple AI providers via a single environment variable (`AI_PROVIDER`):

| Provider | Supported Models | Primary Use Case |
| :--- | :--- | :--- |
| **Google Gemini** *(Active)* | `gemini-3.5-flash`, `gemini-3.7-flash`, `gemini-3.6-flash` | High-speed structured analysis with automated multi-model rotation on rate limits |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | Structured JSON generation and reasoning |
| **Anthropic Claude** | `claude-3-5-haiku`, `claude-3-5-sonnet` | Analytical spending reports and budget evaluation |
| **Local Rule Engine** | Built-in Python statistical engine | Zero-dependency offline fallback ensuring 100% platform uptime |

---

## 🔒 Privacy & Ground-Truth Guarantees
* **Zero PII Leakage**: User personal details (names, emails, passwords) are never transmitted to external AI providers. Only aggregated category sums and expense labels are analyzed.
* **Zero Mathematical Hallucinations**: All sums, percentages, burn rates, and pacing metrics are calculated in SQL/Python before prompting the LLM, ensuring 100% numerical accuracy.
