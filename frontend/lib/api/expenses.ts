import { apiGet, apiPost, apiPut, apiDelete, downloadFile } from './client';
import {
  Expense,
  ExpenseCreate,
  ExpenseUpdate,
  ExpenseFilterParams,
  PaginatedResponse,
} from '../../types';

export async function getExpenses(
  params?: ExpenseFilterParams
): Promise<PaginatedResponse<Expense>> {
  return apiGet<PaginatedResponse<Expense>>('/expenses', params as Record<string, unknown>);
}

export async function getExpenseById(id: number): Promise<Expense> {
  return apiGet<Expense>(`/expenses/${id}`);
}

export async function createExpense(data: ExpenseCreate): Promise<Expense> {
  return apiPost<Expense, ExpenseCreate>('/expenses', data);
}

export async function updateExpense(
  id: number,
  data: ExpenseUpdate
): Promise<Expense> {
  return apiPut<Expense, ExpenseUpdate>(`/expenses/${id}`, data);
}

export async function deleteExpense(id: number): Promise<void> {
  return apiDelete<void>(`/expenses/${id}`);
}

export async function exportExpenses(
  format: 'csv' | 'pdf',
  params?: Omit<ExpenseFilterParams, 'page' | 'page_size'>
): Promise<void> {
  const queryParams = { ...params, format };
  const ext = format === 'csv' ? 'csv' : 'pdf';
  return downloadFile('/expenses/export', queryParams, `expenses_export.${ext}`);
}
