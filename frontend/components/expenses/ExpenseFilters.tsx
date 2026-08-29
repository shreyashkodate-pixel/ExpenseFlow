'use client';

import React from 'react';
import { Search, RotateCcw, Filter } from 'lucide-react';
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
  const categoryOptions = [
    { value: '', label: 'All Categories' },
    ...categories.map((c) => ({ value: c.id, label: c.name })),
  ];

  const paymentOptions = [
    { value: '', label: 'All Payment Methods' },
    ...PAYMENT_METHODS.map((pm) => ({ value: pm, label: pm })),
  ];

  return (
    <div className="glass-panel p-5 rounded-2xl space-y-4 mb-6 shadow-2xl border border-slate-800/80">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="flex items-center space-x-2 text-xs font-extrabold uppercase tracking-wider text-indigo-400">
          <Filter className="w-4 h-4" />
          <span>Filters & Search</span>
        </div>
        <Button variant="ghost" size="sm" onClick={onReset} className="text-xs text-slate-400 hover:text-white gap-1 px-2.5 py-1">
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Search Input */}
        <div className="md:col-span-2">
          <Input
            placeholder="Search description, notes, or memo..."
            icon={<Search className="w-4 h-4 text-indigo-400" />}
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            className="glass-input"
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

      {/* Date & Range Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2 border-t border-slate-800/60">
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
