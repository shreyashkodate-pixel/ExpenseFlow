import { apiGet, apiPost } from './client';
import { Budget, BudgetCreate, OverallBudgetStatus } from '../../types';

export async function getBudgets(month?: number, year?: number): Promise<Budget[]> {
  return apiGet<Budget[]>('/budgets', { month, year });
}

export async function setBudget(data: BudgetCreate): Promise<Budget> {
  return apiPost<Budget, BudgetCreate>('/budgets', data);
}

export async function getBudgetStatus(
  month?: number,
  year?: number
): Promise<OverallBudgetStatus> {
  return apiGet<OverallBudgetStatus>('/budgets/status', { month, year });
}
