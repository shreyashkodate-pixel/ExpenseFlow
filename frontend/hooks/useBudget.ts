import { useState, useEffect, useCallback } from 'react';
import { OverallBudgetStatus, BudgetCreate } from '../types';
import { getBudgetStatus, setBudget } from '../lib/api/budgets';

export function useBudget(month?: number, year?: number) {
  const [status, setStatus] = useState<OverallBudgetStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getBudgetStatus(month, year);
      setStatus(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch budget status');
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const updateBudgetGoal = async (data: BudgetCreate) => {
    const res = await setBudget(data);
    await fetchStatus();
    return res;
  };

  return {
    status,
    loading,
    error,
    refreshBudget: fetchStatus,
    updateBudgetGoal,
  };
}
