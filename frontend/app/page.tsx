'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { DashboardSummary } from '../types';
import { getDashboardSummary } from '../lib/api/analytics';
import { exportExpenses } from '../lib/api/expenses';
import { Header } from '../components/shared/Header';
import { SummaryCards } from '../components/dashboard/SummaryCards';
import { RecentExpenses } from '../components/dashboard/RecentExpenses';
import { BudgetOverviewWidget } from '../components/dashboard/BudgetOverviewWidget';
import { AIInsightsCard } from '../components/dashboard/AIInsightsCard';
import { ExpenseFormModal } from '../components/expenses/ExpenseFormModal';
import { useToast } from '../components/ui/toast';
import { useCategories } from '../hooks/useCategories';
import { createExpense } from '../lib/api/expenses';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const { categories } = useCategories();
  const { showToast } = useToast();

  const fetchSummary = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to load dashboard summary', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const handleExportCsv = async () => {
    try {
      await exportExpenses('csv');
      showToast('CSV export downloaded successfully', 'success');
    } catch {
      showToast('Failed to export CSV', 'error');
    }
  };

  const handleExportPdf = async () => {
    try {
      await exportExpenses('pdf');
      showToast('PDF export downloaded successfully', 'success');
    } catch {
      showToast('Failed to export PDF', 'error');
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <Header
        title="Dashboard"
        subtitle="Overview of your financial performance, recent transactions, and budget goals."
        onAddExpense={() => setIsAddModalOpen(true)}
        onExportCsv={handleExportCsv}
        onExportPdf={handleExportPdf}
      />

      {/* Top Metric Cards */}
      <SummaryCards summary={summary} loading={loading} />

      {/* AI Smart Spending Insights & Recommendations */}
      <AIInsightsCard />

      {/* Grid: Recent Activity & Budget Widget */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <RecentExpenses expenses={summary?.recent_expenses || []} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <BudgetOverviewWidget overallBudget={summary?.budget_status || null} loading={loading} />
        </div>
      </div>

      {/* Add Expense Form Modal */}
      <ExpenseFormModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        categories={categories}
        onSubmit={async (data) => {
          await createExpense(data);
          showToast('Expense added successfully', 'success');
          fetchSummary();
        }}
      />
    </div>
  );
}
