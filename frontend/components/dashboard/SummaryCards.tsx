'use client';

import React from 'react';
import { DollarSign, Hash, TrendingUp, AlertTriangle, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { DashboardSummary } from '../../types';
import { Card } from '../ui/card';

interface SummaryCardsProps {
  summary: DashboardSummary | null;
  loading: boolean;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 sm:h-36 rounded-2xl glass-card animate-pulse bg-slate-200/50 dark:bg-slate-800/30" />
        ))}
      </div>
    );
  }

  const monthSpend = summary?.current_month_spending || 0;
  const monthCount = summary?.total_expense_count || 0;
  const highestExpense = summary?.highest_expense;
  const overallBudget = summary?.budget_status;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {/* Month Spend Card */}
      <Card className="relative overflow-hidden group border-indigo-500/20 hover:border-indigo-500/50 p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">Total Month Spend</p>
            <h3 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white mt-1 tracking-tight">
              ₹{monthSpend.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </h3>
          </div>
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-indigo-500/10 dark:bg-gradient-to-tr dark:from-indigo-600/30 dark:to-purple-600/30 border border-indigo-500/20 dark:border-indigo-500/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform shadow-sm dark:shadow-lg dark:shadow-indigo-600/20 shrink-0">
            <DollarSign className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
        </div>
        <div className="mt-4 sm:mt-5 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold text-[11px] sm:text-xs">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>Active Period</span>
          </span>
          <span className="font-mono text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400">INR (₹)</span>
        </div>
      </Card>

      {/* Transactions Count Card */}
      <Card className="relative overflow-hidden group border-purple-500/20 hover:border-purple-500/50 p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400">Total Transactions</p>
            <h3 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white mt-1 tracking-tight">{monthCount}</h3>
          </div>
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-purple-500/10 dark:bg-gradient-to-tr dark:from-purple-600/30 dark:to-pink-600/30 border border-purple-500/20 dark:border-purple-500/30 flex items-center justify-center text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform shadow-sm dark:shadow-lg dark:shadow-purple-600/20 shrink-0">
            <Hash className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
        </div>
        <div className="mt-4 sm:mt-5 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span className="text-[11px] sm:text-xs truncate">Total entries</span>
          <span className="font-mono text-[10px] sm:text-[11px] text-purple-600 dark:text-purple-300 font-semibold">{monthCount} Items</span>
        </div>
      </Card>

      {/* Highest Expense Card */}
      <Card className="relative overflow-hidden group border-pink-500/20 hover:border-pink-500/50 p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-pink-600 dark:text-pink-400">Highest Transaction</p>
            <h3 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white mt-1 tracking-tight">
              {highestExpense ? `₹${highestExpense.amount.toLocaleString('en-IN')}` : '₹0'}
            </h3>
          </div>
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-pink-500/10 dark:bg-gradient-to-tr dark:from-pink-600/30 dark:to-rose-600/30 border border-pink-500/20 dark:border-pink-500/30 flex items-center justify-center text-pink-600 dark:text-pink-400 group-hover:scale-110 transition-transform shadow-sm dark:shadow-lg dark:shadow-pink-600/20 shrink-0">
            <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
        </div>
        <div className="mt-4 sm:mt-5 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 truncate">
          {highestExpense ? `${highestExpense.description} (${highestExpense.category.name})` : 'No transactions'}
        </div>
      </Card>

      {/* Overall Budget Utilization Card */}
      <Card className="relative overflow-hidden group border-emerald-500/20 hover:border-emerald-500/50 p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Budget Goal</p>
            <h3 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white mt-1 tracking-tight">
              {overallBudget ? `${overallBudget.percentage_used.toFixed(0)}%` : 'Not Set'}
            </h3>
          </div>
          <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl border flex items-center justify-center group-hover:scale-110 transition-transform shadow-sm dark:shadow-lg shrink-0 ${
            overallBudget?.status_level === 'exceeded'
              ? 'bg-rose-500/15 border-rose-500/30 text-rose-600 dark:text-rose-400 dark:shadow-rose-600/20'
              : overallBudget?.status_level === 'warning'
              ? 'bg-amber-500/15 border-amber-500/30 text-amber-600 dark:text-amber-400 dark:shadow-amber-600/20'
              : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-600 dark:text-emerald-400 dark:shadow-emerald-600/20'
          }`}>
            {overallBudget?.status_level === 'exceeded' || overallBudget?.status_level === 'warning' ? (
              <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6" />
            ) : (
              <CheckCircle2 className="w-5 h-5 sm:w-6 sm:h-6" />
            )}
          </div>
        </div>
        <div className="mt-4 sm:mt-5 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 flex justify-between items-center truncate">
          <span>{overallBudget ? `Remaining: ₹${overallBudget.remaining_amount.toLocaleString('en-IN')}` : 'Set in Budget Goals'}</span>
        </div>
      </Card>
    </div>
  );
};
