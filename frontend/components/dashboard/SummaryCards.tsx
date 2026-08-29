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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-36 rounded-2xl glass-card animate-pulse bg-slate-800/30" />
        ))}
      </div>
    );
  }

  const monthSpend = summary?.current_month_spending || 0;
  const monthCount = summary?.total_expense_count || 0;
  const highestExpense = summary?.highest_expense;
  const overallBudget = summary?.budget_status;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Month Spend Card */}
      <Card className="relative overflow-hidden group border-indigo-500/20 hover:border-indigo-500/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-indigo-400">Total Month Spend</p>
            <h3 className="text-2xl md:text-3xl font-extrabold text-white mt-1.5 tracking-tight">
              ₹{monthSpend.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </h3>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600/30 to-purple-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform shadow-lg shadow-indigo-600/20">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>
        <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1 text-emerald-400 font-semibold">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>Active Period</span>
          </span>
          <span className="font-mono text-[11px] text-slate-400">INR (₹)</span>
        </div>
      </Card>

      {/* Transactions Count Card */}
      <Card className="relative overflow-hidden group border-purple-500/20 hover:border-purple-500/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-purple-400">Total Transactions</p>
            <h3 className="text-2xl md:text-3xl font-extrabold text-white mt-1.5 tracking-tight">{monthCount}</h3>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600/30 to-pink-600/30 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform shadow-lg shadow-purple-600/20">
            <Hash className="w-6 h-6" />
          </div>
        </div>
        <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>Total entries recorded</span>
          <span className="font-mono text-[11px] text-purple-300 font-semibold">{monthCount} Items</span>
        </div>
      </Card>

      {/* Highest Expense Card */}
      <Card className="relative overflow-hidden group border-pink-500/20 hover:border-pink-500/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-pink-400">Highest Transaction</p>
            <h3 className="text-2xl md:text-3xl font-extrabold text-white mt-1.5 tracking-tight">
              {highestExpense ? `₹${highestExpense.amount.toLocaleString('en-IN')}` : '₹0'}
            </h3>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-pink-600/30 to-rose-600/30 border border-pink-500/30 flex items-center justify-center text-pink-400 group-hover:scale-110 transition-transform shadow-lg shadow-pink-600/20">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>
        <div className="mt-5 pt-3 border-t border-slate-800/80 text-xs text-slate-400 truncate">
          {highestExpense ? `${highestExpense.description} (${highestExpense.category.name})` : 'No transactions'}
        </div>
      </Card>

      {/* Overall Budget Utilization Card */}
      <Card className="relative overflow-hidden group border-emerald-500/20 hover:border-emerald-500/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-emerald-400">Budget Goal Utilization</p>
            <h3 className="text-2xl md:text-3xl font-extrabold text-white mt-1.5 tracking-tight">
              {overallBudget ? `${overallBudget.percentage_used.toFixed(0)}%` : 'Not Set'}
            </h3>
          </div>
          <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg ${
            overallBudget?.status_level === 'exceeded'
              ? 'bg-rose-500/20 border-rose-500/30 text-rose-400 shadow-rose-600/20'
              : overallBudget?.status_level === 'warning'
              ? 'bg-amber-500/20 border-amber-500/30 text-amber-400 shadow-amber-600/20'
              : 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400 shadow-emerald-600/20'
          }`}>
            {overallBudget?.status_level === 'exceeded' || overallBudget?.status_level === 'warning' ? (
              <AlertTriangle className="w-6 h-6" />
            ) : (
              <CheckCircle2 className="w-6 h-6" />
            )}
          </div>
        </div>
        <div className="mt-5 pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex justify-between items-center">
          <span>{overallBudget ? `Remaining: ₹${overallBudget.remaining_amount.toLocaleString('en-IN')}` : 'Click Budget Goals to set limit'}</span>
        </div>
      </Card>
    </div>
  );
};
