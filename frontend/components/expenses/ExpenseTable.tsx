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
      return 'bg-slate-800 text-slate-300 border-slate-700';
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
    <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl flex flex-col border border-slate-800/80">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/90 text-xs uppercase font-extrabold tracking-wider text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-4.5 px-6">Description</th>
              <th className="py-4.5 px-6">Category</th>
              <th className="py-4.5 px-6">Date</th>
              <th className="py-4.5 px-6">Payment Method</th>
              <th className="py-4.5 px-6 text-right">Amount</th>
              <th className="py-4.5 px-6 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 bg-slate-950/30">
            {loading ? (
              [1, 2, 3, 4, 5].map((i) => (
                <tr key={i} className="animate-pulse">
                  <td colSpan={6} className="py-5 px-6">
                    <div className="h-7 rounded-xl bg-slate-800/30" />
                  </td>
                </tr>
              ))
            ) : expenses.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-16 text-center text-slate-500">
                  <Tag className="w-10 h-10 mx-auto mb-3 opacity-30 text-indigo-400" />
                  <p className="text-base font-bold text-slate-300">No expenses match your search criteria</p>
                  <p className="text-xs text-slate-400 mt-1">Try clearing active search filters or add a new expense.</p>
                </td>
              </tr>
            ) : (
              expenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-slate-900/80 transition-colors group">
                  <td className="py-4 px-6">
                    <div className="font-bold text-white group-hover:text-indigo-300 transition-colors">{expense.description}</div>
                    {expense.notes && (
                      <div className="text-xs text-slate-400 mt-0.5 max-w-xs truncate font-normal">
                        {expense.notes}
                      </div>
                    )}
                  </td>
                  <td className="py-4 px-6">
                    <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 shadow-sm">
                      <Tag className="w-3 h-3 mr-1.5 text-indigo-400" />
                      {expense.category.name}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-xs text-slate-300 font-mono">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      {new Date(expense.date).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-xs">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold ${getPaymentBadgeStyle(expense.payment_method)}`}>
                      {expense.payment_method}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right font-extrabold text-rose-400 font-mono text-base tracking-tight">
                    -₹{expense.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-6 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <button
                        onClick={() => onEdit(expense)}
                        className="p-2 rounded-lg text-slate-400 hover:text-indigo-300 hover:bg-slate-800 transition-colors"
                        title="Edit Expense"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onDelete(expense.id)}
                        className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                        title="Delete Expense"
                      >
                        <Trash2 className="w-4 h-4" />
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
      <div className="p-4 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
        <div>
          Showing page <span className="font-bold text-white">{page}</span> of{' '}
          <span className="font-bold text-white">{totalPages}</span> ({totalItems} total items)
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
