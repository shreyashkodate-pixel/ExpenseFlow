export type PaymentMethod =
  | 'Cash'
  | 'GPay'
  | 'Credit Card'
  | 'UPI'
  | 'Bank Transfer'
  | 'Others';

export interface Category {
  id: number;
  name: string;
  created_at: string;
}

export interface CategoryWithCount extends Category {
  expense_count: number;
}

export interface CategoryCreate {
  name: string;
}

export interface Expense {
  id: number;
  amount: number;
  category_id: number;
  description: string;
  notes?: string | null;
  date: string;
  payment_method: PaymentMethod;
  created_at: string;
  updated_at: string;
  category: Category;
}

export interface ExpenseCreate {
  amount: number;
  category_id: number;
  description: string;
  notes?: string;
  date: string;
  payment_method: PaymentMethod;
}

export interface ExpenseUpdate {
  amount?: number;
  category_id?: number;
  description?: string;
  notes?: string;
  date?: string;
  payment_method?: PaymentMethod;
}

export interface ExpenseFilterParams {
  search?: string;
  category_id?: number;
  payment_method?: PaymentMethod | '';
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
  page?: number;
  page_size?: number;
  sort_by?: 'date' | 'amount' | 'created_at';
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Budget {
  id: number;
  month: number;
  year: number;
  amount: number;
  category_id?: number | null;
  created_at: string;
  updated_at: string;
  category?: Category | null;
}

export interface BudgetCreate {
  month: number;
  year: number;
  amount: number;
  category_id?: number | null;
}

export type BudgetAlertStatus = 'ok' | 'warning' | 'exceeded';

export interface BudgetStatusItem {
  budget_id?: number | null;
  category_id?: number | null;
  category_name: string;
  budget_amount: number;
  spent_amount: number;
  remaining_amount: number;
  percentage_used: number;
  status_level: BudgetAlertStatus;
}

export interface OverallBudgetStatus {
  month: number;
  year: number;
  overall_budget: BudgetStatusItem | null;
  category_budgets: BudgetStatusItem[];
}

export interface DashboardSummary {
  current_month_spending: number;
  total_expense_count: number;
  highest_expense: Expense | null;
  recent_expenses: Expense[];
  budget_status: BudgetStatusItem | null;
  top_categories: CategorySpending[];
}

export interface DailySpendingItem {
  date: string;
  amount: number;
  expense_count: number;
}

export interface CategorySpending {
  category_id: number;
  category_name: string;
  amount: number;
  percentage: number;
  expense_count: number;
}

export interface MonthlyAnalyticsResponse {
  month: number;
  year: number;
  total_amount: number;
  expense_count: number;
  daily_breakdown: DailySpendingItem[];
  by_category: CategorySpending[];
}

export interface MonthlyAnalyticsItem {
  month: number;
  year: number;
  month_name: string;
  amount: number;
  expense_count: number;
}

export interface YearlyAnalyticsItem {
  year: number;
  total_amount: number;
  expense_count: number;
  monthly_breakdown: MonthlyAnalyticsItem[];
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
