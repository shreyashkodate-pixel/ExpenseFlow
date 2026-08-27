import { useState, useEffect, useCallback } from 'react';
import { Expense, ExpenseFilterParams, ExpenseCreate, ExpenseUpdate } from '../types';
import { getExpenses, createExpense, updateExpense, deleteExpense, exportExpenses } from '../lib/api/expenses';

export function useExpenses(initialFilters?: ExpenseFilterParams) {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<ExpenseFilterParams>({
    page: 1,
    page_size: 10,
    sort_by: 'date',
    sort_order: 'desc',
    ...initialFilters,
  });

  const fetchExpenses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getExpenses(filters);
      setExpenses(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch expenses');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  const updateFilters = (newFilters: Partial<ExpenseFilterParams>) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
      // reset to page 1 on filter changes unless page is explicitly updated
      page: newFilters.page !== undefined ? newFilters.page : 1,
    }));
  };

  const addExpense = async (data: ExpenseCreate) => {
    const created = await createExpense(data);
    await fetchExpenses();
    return created;
  };

  const editExpense = async (id: number, data: ExpenseUpdate) => {
    const updated = await updateExpense(id, data);
    await fetchExpenses();
    return updated;
  };

  const removeExpense = async (id: number) => {
    await deleteExpense(id);
    await fetchExpenses();
  };

  const handleExport = async (format: 'csv' | 'pdf') => {
    const { page, page_size, ...exportFilters } = filters;
    await exportExpenses(format, exportFilters);
  };

  return {
    expenses,
    total,
    totalPages,
    loading,
    error,
    filters,
    updateFilters,
    refreshExpenses: fetchExpenses,
    addExpense,
    editExpense,
    removeExpense,
    handleExport,
  };
}
