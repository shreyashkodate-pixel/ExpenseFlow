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

export interface AIRecommendationResponse {
  financial_health_score: number;
  health_status: 'Excellent' | 'Good' | 'Needs Attention' | 'Getting Started' | string;
  headline: string;
  spending_spikes: SpendingSpike[];
  saving_tips: SavingTip[];
  budget_warnings: BudgetWarning[];
  positive_habits: string[];
  provider_used: string;
  cached: boolean;
  generated_at: string;
}
