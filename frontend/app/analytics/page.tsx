'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { MonthlyAnalyticsResponse } from '../../types';
import { getMonthlyAnalytics } from '../../lib/api/analytics';
import { Header } from '../../components/shared/Header';
import { Select } from '../../components/ui/select';
import { SpendingCharts } from '../../components/analytics/SpendingCharts';
import { useToast } from '../../components/ui/toast';

const MONTH_OPTIONS = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' },
];

export default function AnalyticsPage() {
  const currentDate = new Date();
  const [selectedMonth, setSelectedMonth] = useState<number>(currentDate.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState<number>(currentDate.getFullYear());

  const [analyticsData, setAnalyticsData] = useState<MonthlyAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getMonthlyAnalytics(selectedMonth, selectedYear);
      setAnalyticsData(data);
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to load analytics', 'error');
    } finally {
      setLoading(false);
    }
  }, [selectedMonth, selectedYear, showToast]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const yearOptions = [
    { value: selectedYear - 1, label: String(selectedYear - 1) },
    { value: selectedYear, label: String(selectedYear) },
    { value: selectedYear + 1, label: String(selectedYear + 1) },
  ];

  const totalMonthSpend = analyticsData?.total_amount || 0;
  const dailyBreakdown = analyticsData?.daily_breakdown || [];
  const categoryBreakdown = analyticsData?.by_category || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Header
        title="Spending Analytics"
        subtitle="Visualize daily financial trends and category breakdown for any month."
      />

      {/* Date Selectors Row */}
      <div className="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-slate-800/80 shadow-2xl">
        <div className="grid grid-cols-2 sm:flex sm:items-center gap-3 sm:space-x-4">
          <div className="w-full sm:w-44 lg:w-48">
            <Select
              label="Select Month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(Number(e.target.value))}
              options={MONTH_OPTIONS}
            />
          </div>
          <div className="w-full sm:w-28 lg:w-32">
            <Select
              label="Select Year"
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              options={yearOptions}
            />
          </div>
        </div>

        <div className="text-left sm:text-right pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-800/60">
          <p className="text-[10px] sm:text-xs font-extrabold uppercase tracking-wider text-slate-400">Total Spend in Selected Period</p>
          <p className="text-xl sm:text-2xl font-extrabold text-white gradient-text font-mono mt-0.5">
            ₹{totalMonthSpend.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {/* Recharts Analytics Charts */}
      <SpendingCharts
        dailyData={dailyBreakdown}
        categoryData={categoryBreakdown}
        loading={loading}
      />
    </div>
  );
}
