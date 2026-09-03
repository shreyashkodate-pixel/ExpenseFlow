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

export interface AIRecommendationResponse {
  financial_health_score: number;
  health_status: 'Excellent' | 'Good' | 'Needs Attention' | 'Getting Started' | string;
  headline: string;
  spending_spikes: SpendingSpike[];
  saving_tips: SavingTip[];
  budget_warnings: BudgetWarning[];
  predictive_budget_alerts?: PredictiveBudgetAlert[];
  positive_habits: string[];
  provider_used: string;
  cached: boolean;
  generated_at: string;
}
