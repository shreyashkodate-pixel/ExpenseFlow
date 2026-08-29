'use client';

import React from 'react';
import { Plus, Download, FileText, Calendar } from 'lucide-react';
import { Button } from '../ui/button';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  title: string;
  subtitle?: string;
  onAddExpense?: () => void;
  onExportCsv?: () => void;
  onExportPdf?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  onAddExpense,
  onExportCsv,
  onExportPdf,
}) => {
  const currentDateFormatted = new Date().toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-5 border-b border-slate-800/80 mb-6 lg:mb-8 gap-4">
      <div>
        <div className="flex flex-wrap items-center gap-2.5 mb-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">{title}</h1>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-900/90 text-slate-300 border border-slate-800">
            <Calendar className="w-3 h-3 text-indigo-400" />
            <span>{currentDateFormatted}</span>
          </span>
        </div>
        {subtitle && <p className="text-xs sm:text-sm text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto">
        <ThemeToggle />

        {onExportCsv && (
          <Button
            variant="outline"
            size="sm"
            onClick={onExportCsv}
            className="flex-1 sm:flex-none gap-1.5 border-emerald-500/30 hover:border-emerald-500/60 hover:bg-emerald-500/10 text-emerald-300 text-xs"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>CSV</span>
          </Button>
        )}
        {onExportPdf && (
          <Button
            variant="outline"
            size="sm"
            onClick={onExportPdf}
            className="flex-1 sm:flex-none gap-1.5 border-rose-500/30 hover:border-rose-500/60 hover:bg-rose-500/10 text-rose-300 text-xs"
          >
            <FileText className="w-3.5 h-3.5 text-rose-400" />
            <span>PDF</span>
          </Button>
        )}
        {onAddExpense && (
          <Button
            variant="primary"
            size="md"
            onClick={onAddExpense}
            className="w-full sm:w-auto gap-2 shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 text-xs sm:text-sm py-2 sm:py-2.5"
          >
            <Plus className="w-4 h-4" />
            <span>Add Expense</span>
          </Button>
        )}
      </div>
    </header>
  );
};
