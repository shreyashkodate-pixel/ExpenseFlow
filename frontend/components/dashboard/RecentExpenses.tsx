'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Tag, Calendar, CreditCard } from 'lucide-react';
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
      <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-800/60">
        <CardTitle className="text-lg flex items-center gap-2">
          <span>Recent Activity</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 font-mono">
            {expenses.length} Latest
          </span>
        </CardTitle>
        <Link
          href="/expenses"
          className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 hover:bg-indigo-500/20"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto pt-4">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 rounded-xl bg-slate-800/30 animate-pulse" />
            ))}
          </div>
        ) : expenses.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-56 text-slate-500">
            <Tag className="w-10 h-10 mb-3 opacity-40 text-indigo-400" />
            <p className="text-sm font-semibold text-slate-400">No expenses recorded yet</p>
            <p className="text-xs text-slate-500 mt-1">Click &quot;Add Expense&quot; to log your first transaction.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {expenses.map((expense) => (
              <div
                key={expense.id}
                className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/40 hover:bg-slate-900/90 transition-all duration-200 group shadow-md"
              >
                <div className="flex items-center space-x-3.5">
                  <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-indigo-600/20 via-purple-600/20 to-pink-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-300 font-bold text-base shadow-inner group-hover:scale-105 transition-transform">
                    {expense.category.name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                      {expense.description}
                    </h4>
                    <div className="flex items-center space-x-2 text-xs text-slate-400 mt-1">
                      <span className="inline-flex items-center gap-1 font-semibold text-slate-300">
                        <Tag className="w-3 h-3 text-indigo-400" />
                        {expense.category.name}
                      </span>
                      <span>•</span>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${getPaymentBadgeStyle(expense.payment_method)}`}>
                        {expense.payment_method}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1 font-mono text-[11px] text-slate-400">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        {new Date(expense.date).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                        })}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-base font-extrabold text-rose-400 font-mono tracking-tight">
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
