'use client';

import React, { useState } from 'react';
import { Plus, Wallet, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useBudget } from '../../hooks/useBudget';
import { useCategories } from '../../hooks/useCategories';
import { Header } from '../../components/shared/Header';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { BudgetSetupModal } from '../../components/budget/BudgetSetupModal';
import { useToast } from '../../components/ui/toast';

export default function BudgetPage() {
  const currentDate = new Date();
  const currentMonth = currentDate.getMonth() + 1;
  const currentYear = currentDate.getFullYear();

  const { status, loading, refreshBudget, updateBudgetGoal } = useBudget(currentMonth, currentYear);
  const { categories } = useCategories();
  const { showToast } = useToast();

  const [isModalOpen, setIsModalOpen] = useState(false);

  const overall = status?.overall_budget;
  const categoryBudgets = status?.category_budgets || [];

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto">
      <Header
        title="Budget Goals & Limits"
        subtitle={`Track spending caps and status alerts for ${currentDate.toLocaleString('en-IN', { month: 'long' })} ${currentYear}.`}
      />

      {/* Main Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between glass-panel p-4 rounded-xl gap-3 sm:gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
            <Wallet className="w-4.5 h-4.5 sm:w-5 sm:h-5" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-white">Monthly Target Rules</h3>
            <p className="text-xs text-slate-400">Set overall cap or assign category-specific budget limits</p>
          </div>
        </div>
        <Button variant="primary" size="md" onClick={() => setIsModalOpen(true)} className="w-full sm:w-auto gap-2 text-xs sm:text-sm py-2">
          <Plus className="w-4 h-4" />
          <span>Set Budget Goal</span>
        </Button>
      </div>

      {/* Overall Budget Focus Card */}
      <Card className="p-4 sm:p-8 relative overflow-hidden">
        {loading ? (
          <div className="h-32 sm:h-36 rounded-lg bg-slate-800/40 animate-pulse" />
        ) : !overall ? (
          <div className="text-center py-6 sm:py-8 space-y-3">
            <Wallet className="w-8 h-8 sm:w-10 sm:h-10 mx-auto text-slate-500 opacity-50" />
            <h3 className="text-base sm:text-lg font-bold text-slate-200">No Overall Budget Goal Set</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Setting an overall monthly budget allows ExpenseFlow to alert you when your spending reaches 80% or exceeds your goal.
            </p>
            <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)}>
              Define Overall Cap
            </Button>
          </div>
        ) : (
          <div className="space-y-4 sm:space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4">
              <div>
                <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider text-slate-400">Overall Target</span>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-0.5 sm:mt-1">
                  ₹{overall.budget_amount.toLocaleString('en-IN')}
                </h2>
              </div>
              <div className="flex items-center space-x-4 sm:space-x-6 text-sm pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-800/60">
                <div>
                  <p className="text-[10px] sm:text-xs text-slate-400">Total Spent</p>
                  <p className="text-base sm:text-lg font-bold text-rose-400 mt-0.5">
                    ₹{overall.spent_amount.toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="h-7 sm:h-8 w-px bg-slate-800" />
                <div>
                  <p className="text-[10px] sm:text-xs text-slate-400">Remaining</p>
                  <p className="text-base sm:text-lg font-bold text-emerald-400 mt-0.5">
                    ₹{overall.remaining_amount.toLocaleString('en-IN')}
                  </p>
                </div>
              </div>
            </div>

            {/* Utilization Bar */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-[11px] sm:text-xs font-medium">
                <span className="flex items-center gap-1.5 truncate">
                  {overall.status_level === 'exceeded' ? (
                    <AlertTriangle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-rose-400 shrink-0" />
                  ) : overall.status_level === 'warning' ? (
                    <AlertTriangle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-400 shrink-0" />
                  )}
                  <span
                    className={`truncate ${
                      overall.status_level === 'exceeded'
                        ? 'text-rose-400 font-bold'
                        : overall.status_level === 'warning'
                        ? 'text-amber-400 font-bold'
                        : 'text-emerald-400 font-bold'
                    }`}
                  >
                    {overall.status_level === 'exceeded'
                      ? 'Limit Exceeded!'
                      : overall.status_level === 'warning'
                      ? '>80% Used'
                      : 'On Track'}
                  </span>
                </span>
                <span className="font-mono text-slate-300 shrink-0">
                  {overall.percentage_used.toFixed(1)}% Used
                </span>
              </div>

              <div className="w-full h-3.5 sm:h-4 rounded-full bg-slate-900 overflow-hidden p-0.5 border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    overall.status_level === 'exceeded'
                      ? 'bg-gradient-to-r from-rose-600 to-rose-400'
                      : overall.status_level === 'warning'
                      ? 'bg-gradient-to-r from-amber-500 to-amber-400'
                      : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400'
                  }`}
                  style={{ width: `${Math.min(overall.percentage_used, 100)}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Category Specific Budget Caps */}
      <div>
        <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Category Budgets</h3>
        {categoryBudgets.length === 0 ? (
          <div className="glass-card p-5 sm:p-6 rounded-xl text-center text-slate-400 text-xs sm:text-sm">
            No category-specific budget limits defined for this month.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {categoryBudgets.map((item, idx) => (
              <Card key={item.budget_id || idx} className="space-y-3.5 p-4 sm:p-6">
                <CardHeader className="flex flex-row items-center justify-between pb-2 p-0">
                  <CardTitle className="text-sm sm:text-base truncate mr-2">{item.category_name}</CardTitle>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] sm:text-[11px] font-bold font-mono uppercase shrink-0 ${
                      item.status_level === 'exceeded'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : item.status_level === 'warning'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {item.status_level}
                  </span>
                </CardHeader>
                <CardContent className="space-y-2.5 sm:space-y-3 p-0">
                  <div className="flex items-end justify-between text-[11px] sm:text-xs">
                    <span className="text-slate-400">Spent: ₹{item.spent_amount.toLocaleString('en-IN')}</span>
                    <span className="text-slate-300 font-semibold">Limit: ₹{item.budget_amount.toLocaleString('en-IN')}</span>
                  </div>

                  <div className="w-full h-2 sm:h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                    <div
                      className={`h-full rounded-full transition-all ${
                        item.status_level === 'exceeded'
                          ? 'bg-rose-500'
                          : item.status_level === 'warning'
                          ? 'bg-amber-500'
                          : 'bg-indigo-500'
                      }`}
                      style={{ width: `${Math.min(item.percentage_used, 100)}%` }}
                    />
                  </div>

                  <p className="text-[10px] sm:text-[11px] text-right text-slate-400 font-mono">
                    Remaining: ₹{item.remaining_amount.toLocaleString('en-IN')}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Setup Modal */}
      <BudgetSetupModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        categories={categories}
        currentMonth={currentMonth}
        currentYear={currentYear}
        onSubmit={async (data) => {
          await updateBudgetGoal(data);
          showToast('Budget goal saved successfully', 'success');
          refreshBudget();
        }}
      />
    </div>
  );
}
