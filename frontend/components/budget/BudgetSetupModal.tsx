'use client';

import React, { useState } from 'react';
import { CategoryWithCount, BudgetCreate } from '../../types';
import { Modal } from '../ui/modal';
import { Input } from '../ui/input';
import { Select } from '../ui/select';
import { Button } from '../ui/button';

interface BudgetSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: CategoryWithCount[];
  currentMonth: number;
  currentYear: number;
  onSubmit: (data: BudgetCreate) => Promise<void>;
}

export const BudgetSetupModal: React.FC<BudgetSetupModalProps> = ({
  isOpen,
  onClose,
  categories,
  currentMonth,
  currentYear,
  onSubmit,
}) => {
  const [amount, setAmount] = useState<string>('');
  const [categoryId, setCategoryId] = useState<string>(''); // empty string means Overall Budget
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numAmount = parseFloat(amount);

    if (isNaN(numAmount) || numAmount <= 0) {
      setError('Amount must be a positive number');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        month: currentMonth,
        year: currentYear,
        amount: numAmount,
        category_id: categoryId ? Number(categoryId) : null,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to set budget goal');
    } finally {
      setLoading(false);
    }
  };

  const categoryOptions = [
    { value: '', label: 'Overall Monthly Budget' },
    ...categories.map((c) => ({ value: c.id, label: `${c.name} Category` })),
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Set Budget Goal">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-medium">
            {error}
          </div>
        )}

        <Select
          label="Budget Scope"
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          options={categoryOptions}
        />

        <Input
          label="Target Budget Limit (₹)"
          type="number"
          step="0.01"
          placeholder="e.g. 25000"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />

        <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs">
          Target set for Month {currentMonth}, {currentYear}. If a budget already exists for this scope, it will be updated.
        </div>

        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={loading}>
            Save Target
          </Button>
        </div>
      </form>
    </Modal>
  );
};
