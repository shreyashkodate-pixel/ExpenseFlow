'use client';

import React from 'react';
import Link from 'next/link';
import { Wallet, ChevronRight, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { BudgetStatusItem } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

interface BudgetOverviewWidgetProps {
  overallBudget: BudgetStatusItem | null;
  loading: boolean;
}

export const BudgetOverviewWidget: React.FC<BudgetOverviewWidgetProps> = ({
  overallBudget,
  loading,
}) => {
  return (
    <Card className="h-full flex flex-col border-slate-800/80">
      <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-800/60">
        <CardTitle className="text-base flex items-center gap-2">
          <Wallet className="w-4.5 h-4.5 text-indigo-400" />
          <span>Monthly Target Utilization</span>
        </CardTitle>
        <Link
          href="/budget"
          className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20"
        >
          <span>Manage</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col justify-center pt-6">
        {loading ? (
          <div className="h-32 rounded-xl bg-slate-800/30 animate-pulse" />
        ) : !overallBudget ? (
          <div className="text-center py-8 space-y-3">
            <Wallet className="w-10 h-10 mx-auto text-slate-500 opacity-40" />
            <p className="text-sm font-bold text-slate-300">No overall budget set for this month</p>
            <Link
              href="/budget"
              className="inline-block px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 hover:opacity-90 transition-opacity"
            >
              Set Monthly Limit Goal
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Month Spend</p>
                <p className="text-2xl font-extrabold text-white mt-1 font-mono">
                  ₹{overallBudget.spent_amount.toLocaleString('en-IN')}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Target Cap</p>
                <p className="text-base font-semibold text-slate-300 mt-1 font-mono">
                  ₹{overallBudget.budget_amount.toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            {/* Visual Meter */}
            <div className="space-y-2">
              <div className="w-full h-4 rounded-full bg-slate-950 overflow-hidden p-0.5 border border-slate-800/80 shadow-inner">
                <div
                  className={`h-full rounded-full transition-all duration-700 shadow-glow ${
                    overallBudget.status_level === 'exceeded'
                      ? 'bg-gradient-to-r from-rose-600 to-rose-400 glow-rose'
                      : overallBudget.status_level === 'warning'
                      ? 'bg-gradient-to-r from-amber-500 to-amber-400 glow-amber'
                      : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 glow-emerald'
                  }`}
                  style={{ width: `${Math.min(overallBudget.percentage_used, 100)}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-xs font-mono pt-1">
                <span
                  className={`flex items-center gap-1 font-bold ${
                    overallBudget.status_level === 'exceeded'
                      ? 'text-rose-400'
                      : overallBudget.status_level === 'warning'
                      ? 'text-amber-400'
                      : 'text-emerald-400'
                  }`}
                >
                  {overallBudget.status_level === 'exceeded' || overallBudget.status_level === 'warning' ? (
                    <AlertTriangle className="w-3.5 h-3.5" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  )}
                  <span>{overallBudget.percentage_used.toFixed(1)}% Used</span>
                </span>
                <span className="text-slate-300 font-semibold">
                  Remaining: ₹{overallBudget.remaining_amount.toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
