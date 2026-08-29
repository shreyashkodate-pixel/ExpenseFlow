'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Tag, Calendar } from 'lucide-react';
import { Expense } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

interface RecentExpensesProps {
  expenses: Expense[];
  loading: boolean;
}

const getPaymentBadgeStyle = (pm: string) => {
  switch (pm) {
    case 'GPay':
      return 'badge-gpay';
    case 'UPI':
      return 'badge-upi';
    case 'Credit Card':
      return 'badge-card';
    case 'Cash':
      return 'badge-cash';
    case 'Bank Transfer':
      return 'badge-bank';
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700';
  }
};

export const RecentExpenses: React.FC<RecentExpensesProps> = ({ expenses, loading }) => {
  return (
    <Card className="h-full flex flex-col border-slate-800/80">
      <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-800/60 p-4 sm:p-6">
        <CardTitle className="text-base sm:text-lg flex items-center gap-2">
          <span>Recent Activity</span>
          <span className="text-[11px] sm:text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 font-mono">
            {expenses.length} Latest
          </span>
        </CardTitle>
        <Link
          href="/expenses"
          className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 hover:bg-indigo-500/20"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-3 sm:p-6 pt-3 sm:pt-4">
        {loading ? (
          <div className="space-y-2.5 sm:space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 rounded-xl bg-slate-800/30 animate-pulse" />
            ))}
          </div>
        ) : expenses.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 sm:h-56 text-slate-500 text-center p-4">
            <Tag className="w-8 h-8 sm:w-10 sm:h-10 mb-2 sm:mb-3 opacity-40 text-indigo-400" />
            <p className="text-xs sm:text-sm font-semibold text-slate-400">No expenses recorded yet</p>
            <p className="text-[11px] sm:text-xs text-slate-500 mt-1">Click &quot;Add Expense&quot; to log your first transaction.</p>
          </div>
        ) : (
          <div className="space-y-2.5 sm:space-y-3">
            {expenses.map((expense) => (
              <div
                key={expense.id}
                className="flex items-center justify-between p-3 sm:p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/40 hover:bg-slate-900/90 transition-all duration-200 group shadow-md gap-3"
              >
                <div className="flex items-center space-x-3 min-w-0 flex-1">
                  <div className="w-9 h-9 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-tr from-indigo-600/20 via-purple-600/20 to-pink-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-300 font-bold text-sm sm:text-base shadow-inner group-hover:scale-105 transition-transform shrink-0">
                    {expense.category.name.charAt(0)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs sm:text-sm font-bold text-white group-hover:text-indigo-300 transition-colors truncate">
                      {expense.description}
                    </h4>
                    <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 text-[11px] sm:text-xs text-slate-400 mt-0.5 sm:mt-1">
                      <span className="inline-flex items-center gap-1 font-semibold text-slate-300 truncate">
                        <Tag className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-indigo-400 shrink-0" />
                        <span className="truncate">{expense.category.name}</span>
                      </span>
                      <span className="hidden sm:inline">•</span>
                      <span className={`px-1.5 sm:px-2 py-0.5 rounded text-[10px] sm:text-[11px] font-semibold ${getPaymentBadgeStyle(expense.payment_method)}`}>
                        {expense.payment_method}
                      </span>
                      <span className="hidden sm:inline">•</span>
                      <span className="flex items-center gap-1 font-mono text-[10px] sm:text-[11px] text-slate-400">
                        <Calendar className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-slate-500 shrink-0" />
                        {new Date(expense.date).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                        })}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-sm sm:text-base font-extrabold text-rose-400 font-mono tracking-tight">
                    -₹{expense.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
