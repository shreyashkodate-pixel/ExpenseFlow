'use client';

import React from 'react';
import { Edit2, Trash2, Tag, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { Expense } from '../../types';
import { Button } from '../ui/button';

interface ExpenseTableProps {
  expenses: Expense[];
  loading: boolean;
  page: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onEdit: (expense: Expense) => void;
  onDelete: (id: number) => void;
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
      return 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700';
  }
};

export const ExpenseTable: React.FC<ExpenseTableProps> = ({
  expenses,
  loading,
  page,
  totalPages,
  totalItems,
  onPageChange,
  onEdit,
  onDelete,
}) => {
  return (
    <div className="glass-panel rounded-2xl overflow-hidden shadow-xl flex flex-col border border-slate-200/80 dark:border-slate-800/80">
      {/* 1. Mobile Cards View (Rendered on < sm screens) */}
      <div className="block sm:hidden p-3 space-y-3">
        {loading ? (
          [1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 rounded-xl bg-slate-200/60 dark:bg-slate-800/30 animate-pulse" />
          ))
        ) : expenses.length === 0 ? (
          <div className="py-12 text-center text-slate-500">
            <Tag className="w-8 h-8 mx-auto mb-2 opacity-30 text-indigo-500" />
            <p className="text-sm font-bold text-slate-800 dark:text-slate-300">No expenses found</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Try changing filters or add a new expense.</p>
          </div>
        ) : (
          expenses.map((expense) => (
            <div
              key={expense.id}
              className="p-3.5 rounded-xl bg-white/80 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 shadow-sm dark:shadow-md space-y-2.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">{expense.description}</h4>
                  {expense.notes && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">{expense.notes}</p>
                  )}
                </div>
                <span className="text-base font-extrabold text-rose-600 dark:text-rose-400 font-mono shrink-0">
                  -₹{expense.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/80 dark:border-slate-800/60 text-xs">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/20">
                    <Tag className="w-2.5 h-2.5 mr-1 text-indigo-500 dark:text-indigo-400" />
                    {expense.category.name}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${getPaymentBadgeStyle(expense.payment_method)}`}>
                    {expense.payment_method}
                  </span>
                </div>

                <div className="flex items-center space-x-1.5">
                  <span className="font-mono text-[10px] text-slate-500 dark:text-slate-400 mr-1 flex items-center gap-1">
                    <Calendar className="w-2.5 h-2.5 text-slate-400 dark:text-slate-500" />
                    {new Date(expense.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
                  </span>
                  <button
                    onClick={() => onEdit(expense)}
                    className="p-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                    aria-label="Edit expense"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => onDelete(expense.id)}
                    className="p-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                    aria-label="Delete expense"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 2. Desktop/Tablet Data Table View (Rendered on >= sm screens) */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300 min-w-[640px]">
          <thead className="bg-slate-100/90 dark:bg-slate-950/90 text-xs uppercase font-extrabold tracking-wider text-slate-600 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
            <tr>
              <th className="py-4 px-4 sm:px-6">Description</th>
              <th className="py-4 px-4 sm:px-6">Category</th>
              <th className="py-4 px-4 sm:px-6">Date</th>
              <th className="py-4 px-4 sm:px-6">Payment Method</th>
              <th className="py-4 px-4 sm:px-6 text-right">Amount</th>
              <th className="py-4 px-4 sm:px-6 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800/60 bg-white/40 dark:bg-slate-950/30">
            {loading ? (
              [1, 2, 3, 4, 5].map((i) => (
                <tr key={i} className="animate-pulse">
                  <td colSpan={6} className="py-5 px-6">
                    <div className="h-7 rounded-xl bg-slate-200/60 dark:bg-slate-800/30" />
                  </td>
                </tr>
              ))
            ) : expenses.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-16 text-center text-slate-500">
                  <Tag className="w-10 h-10 mx-auto mb-3 opacity-30 text-indigo-500" />
                  <p className="text-base font-bold text-slate-800 dark:text-slate-300">No expenses match your search criteria</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Try clearing active search filters or add a new expense.</p>
                </td>
              </tr>
            ) : (
              expenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/80 transition-colors group">
                  <td className="py-3.5 px-4 sm:px-6">
                    <div className="font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">{expense.description}</div>
                    {expense.notes && (
                      <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 max-w-xs truncate font-normal">
                        {expense.notes}
                      </div>
                    )}
                  </td>
                  <td className="py-3.5 px-4 sm:px-6">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-lg text-xs font-bold bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/20 shadow-sm whitespace-nowrap">
                      <Tag className="w-3 h-3 mr-1.5 text-indigo-500 dark:text-indigo-400" />
                      {expense.category.name}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 sm:px-6 text-xs text-slate-600 dark:text-slate-300 font-mono whitespace-nowrap">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
                      {new Date(expense.date).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 sm:px-6 text-xs whitespace-nowrap">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold ${getPaymentBadgeStyle(expense.payment_method)}`}>
                      {expense.payment_method}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 sm:px-6 text-right font-extrabold text-rose-600 dark:text-rose-400 font-mono text-sm sm:text-base tracking-tight whitespace-nowrap">
                    -₹{expense.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-3.5 px-4 sm:px-6 text-center whitespace-nowrap">
                    <div className="flex items-center justify-center space-x-1.5">
                      <button
                        onClick={() => onEdit(expense)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Edit Expense"
                      >
                        <Edit2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      </button>
                      <button
                        onClick={() => onDelete(expense.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Delete Expense"
                      >
                        <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="p-3.5 sm:p-4 bg-slate-50 dark:bg-slate-950/80 border-t border-slate-200/80 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400">
        <div>
          Showing page <span className="font-bold text-slate-900 dark:text-white">{page}</span> of{' '}
          <span className="font-bold text-slate-900 dark:text-white">{totalPages || 1}</span> ({totalItems} total items)
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="px-3 py-1 text-xs"
          >
            <ChevronLeft className="w-3.5 h-3.5 mr-1" />
            <span>Prev</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages || totalPages === 0}
            onClick={() => onPageChange(page + 1)}
            className="px-3 py-1 text-xs"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5 ml-1" />
          </Button>
        </div>
      </div>
    </div>
  );
};
