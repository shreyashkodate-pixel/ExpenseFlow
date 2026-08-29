'use client';

import React from 'react';
import { Plus, Download, FileText, Calendar } from 'lucide-react';
import { Button } from '../ui/button';

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
    <header className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-slate-800/80 mb-8 gap-4">
      <div>
        <div className="flex items-center space-x-3 mb-1">
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">{title}</h1>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-900/90 text-slate-300 border border-slate-800">
            <Calendar className="w-3 h-3 text-indigo-400" />
            <span>{currentDateFormatted}</span>
          </span>
        </div>
        {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-3">
        {onExportCsv && (
          <Button variant="outline" size="sm" onClick={onExportCsv} className="gap-1.5 border-emerald-500/30 hover:border-emerald-500/60 hover:bg-emerald-500/10 text-emerald-300">
            <Download className="w-4 h-4 text-emerald-400" />
            <span>Export CSV</span>
          </Button>
        )}
        {onExportPdf && (
          <Button variant="outline" size="sm" onClick={onExportPdf} className="gap-1.5 border-rose-500/30 hover:border-rose-500/60 hover:bg-rose-500/10 text-rose-300">
            <FileText className="w-4 h-4 text-rose-400" />
            <span>Export PDF</span>
          </Button>
        )}
        {onAddExpense && (
          <Button variant="primary" size="md" onClick={onAddExpense} className="gap-2 shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50">
            <Plus className="w-4.5 h-4.5" />
            <span>Add Expense</span>
          </Button>
        )}
      </div>
    </header>
  );
};
