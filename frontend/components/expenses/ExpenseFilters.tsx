'use client';

import React, { useState } from 'react';
import { Search, RotateCcw, Filter, SlidersHorizontal, ChevronDown, ChevronUp } from 'lucide-react';
import { CategoryWithCount, ExpenseFilterParams, PaymentMethod } from '../../types';
import { Input } from '../ui/input';
import { Select } from '../ui/select';
import { Button } from '../ui/button';

interface ExpenseFiltersProps {
  filters: ExpenseFilterParams;
  categories: CategoryWithCount[];
  onFilterChange: (filters: Partial<ExpenseFilterParams>) => void;
  onReset: () => void;
}

const PAYMENT_METHODS: PaymentMethod[] = ['Cash', 'GPay', 'Credit Card', 'UPI', 'Bank Transfer', 'Others'];

export const ExpenseFilters: React.FC<ExpenseFiltersProps> = ({
  filters,
  categories,
  onFilterChange,
  onReset,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    ...categories.map((c) => ({ value: c.id, label: c.name })),
  ];

  const paymentOptions = [
    { value: '', label: 'All Payment Methods' },
    ...PAYMENT_METHODS.map((pm) => ({ value: pm, label: pm })),
  ];

  const hasAdvancedFilters = Boolean(
    filters.start_date || filters.end_date || filters.min_amount || filters.max_amount
  );

  return (
    <div className="glass-panel p-4 sm:p-5 rounded-2xl space-y-4 mb-6 shadow-2xl border border-slate-800/80">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="flex items-center space-x-2 text-xs font-extrabold uppercase tracking-wider text-indigo-400">
          <Filter className="w-4 h-4" />
          <span>Filters & Search</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`sm:hidden inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg border transition-colors ${
              hasAdvancedFilters
                ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                : 'bg-slate-900 border-slate-800 text-slate-400'
            }`}
          >
            <SlidersHorizontal className="w-3 h-3" />
            <span>Dates & Range</span>
            {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          <Button variant="ghost" size="sm" onClick={onReset} className="text-xs text-slate-400 hover:text-white gap-1 px-2.5 py-1">
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Search Input */}
        <div className="sm:col-span-2">
          <Input
            placeholder="Search description, notes..."
            icon={<Search className="w-4 h-4 text-indigo-400" />}
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            className="glass-input text-xs sm:text-sm"
          />
        </div>

        {/* Category Dropdown */}
        <div>
          <Select
            value={filters.category_id || ''}
            onChange={(e) =>
              onFilterChange({ category_id: e.target.value ? Number(e.target.value) : undefined })
            }
            options={categoryOptions}
          />
        </div>

        {/* Payment Method Selector */}
        <div>
          <Select
            value={filters.payment_method || ''}
            onChange={(e) =>
              onFilterChange({
                payment_method: (e.target.value as PaymentMethod) || undefined,
              })
            }
            options={paymentOptions}
          />
        </div>
      </div>

      {/* Date & Range Row (Always visible on sm+, toggleable on xs) */}
      <div className={`${showAdvanced ? 'grid' : 'hidden sm:grid'} grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 pt-3 border-t border-slate-800/60`}>
        <Input
          type="date"
          label="Start Date"
          value={filters.start_date || ''}
          onChange={(e) => onFilterChange({ start_date: e.target.value || undefined })}
        />
        <Input
          type="date"
          label="End Date"
          value={filters.end_date || ''}
          onChange={(e) => onFilterChange({ end_date: e.target.value || undefined })}
        />
        <Input
          type="number"
          label="Min Amount (₹)"
          placeholder="0"
          value={filters.min_amount || ''}
          onChange={(e) =>
            onFilterChange({ min_amount: e.target.value ? Number(e.target.value) : undefined })
          }
        />
        <Input
          type="number"
          label="Max Amount (₹)"
          placeholder="Max"
          value={filters.max_amount || ''}
          onChange={(e) =>
            onFilterChange({ max_amount: e.target.value ? Number(e.target.value) : undefined })
          }
        />
      </div>
    </div>
  );
};
