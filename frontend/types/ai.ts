export interface SpendingSpike {
  category: string;
  surge_percentage?: number | null;
  insight: string;
}

export interface SavingTip {
  title: string;
  description: string;
  estimated_monthly_savings?: number | null;
  category?: string | null;
}

export interface BudgetWarning {
  category: string;
  status: string;
  message: string;
}

export interface PredictiveBudgetAlert {
  category: string;
  current_spend: number;
  budget_limit: number;
  daily_burn_rate: number;
  projected_total: number;
  projected_exhaustion_date?: string | null;
  days_until_exhaustion?: number | null;
  safe_daily_ceiling: number;
  pacing_status: 'safe' | 'caution' | 'critical' | 'exceeded' | string;
  alert_message: string;
}

export interface SubscriptionAuditItem {
  merchant_or_service: string;
  amount: number;
  frequency: string;
  category: string;
  last_charged_date?: string | null;
  optimization_tip?: string | null;
}

export interface SubscriptionAuditResponse {
  detected_subscriptions: SubscriptionAuditItem[];
  total_monthly_recurring: number;
  subscription_count: number;
  summary_tip: string;
}

export interface Budget50_30_20 {
  needs_spend: number;
  needs_pct: number;
  wants_spend: number;
  wants_pct: number;
  savings_spend: number;
  savings_pct: number;
  total_evaluated: number;
  status: 'balanced' | 'wants_heavy' | 'needs_heavy' | 'savings_low' | string;
  rebalancing_advice: string;
}

export interface AIChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface AIChatRequest {
  message: string;
  conversation_history?: AIChatMessage[];
}

export interface AIChatResponse {
  reply: string;
  suggested_followups: string[];
  data_points_referenced: string[];
  provider_used: string;
}

export interface AIRecommendationResponse {
  financial_health_score: number;
  health_status: 'Excellent' | 'Good' | 'Needs Attention' | 'Getting Started' | string;
  headline: string;
  spending_spikes: SpendingSpike[];
  saving_tips: SavingTip[];
  budget_warnings: BudgetWarning[];
  predictive_budget_alerts?: PredictiveBudgetAlert[];
  subscription_audit?: SubscriptionAuditResponse | null;
  budget_50_30_20?: Budget50_30_20 | null;
  positive_habits: string[];
  provider_used: string;
  cached: boolean;
  generated_at: string;
}
