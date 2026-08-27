import { apiGet } from './client';
import {
  DashboardSummary,
  MonthlyAnalyticsResponse,
  YearlyAnalyticsItem,
  DailySpendingItem,
  CategorySpending,
} from '../../types';

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>('/dashboard/summary');
}

export async function getMonthlyAnalytics(
  month?: number,
  year?: number
): Promise<MonthlyAnalyticsResponse> {
  return apiGet<MonthlyAnalyticsResponse>('/analytics/monthly', { month, year });
}

export async function getDailyAnalytics(
  date?: string
): Promise<DailySpendingItem[]> {
  return apiGet<DailySpendingItem[]>('/analytics/daily', { date });
}

export async function getCategoryAnalytics(
  month?: number,
  year?: number
): Promise<CategorySpending[]> {
  return apiGet<CategorySpending[]>('/analytics/categories', { month, year });
}

export async function getYearlyAnalytics(
  year?: number
): Promise<YearlyAnalyticsItem> {
  return apiGet<YearlyAnalyticsItem>('/analytics/yearly', { year });
}
