'use client';

import React, { useState, useEffect } from 'react';
import { CategoryWithCount, Expense, ExpenseCreate, PaymentMethod } from '../../types';
import { Modal } from '../ui/modal';
import { Input } from '../ui/input';
import { Select } from '../ui/select';
import { Button } from '../ui/button';

interface ExpenseFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: Expense | null;
  categories: CategoryWithCount[];
  onSubmit: (data: ExpenseCreate) => Promise<void>;
}

const PAYMENT_METHODS: PaymentMethod[] = ['Cash', 'GPay', 'Credit Card', 'UPI', 'Bank Transfer', 'Others'];

export const ExpenseFormModal: React.FC<ExpenseFormModalProps> = ({
  isOpen,
  onClose,
  initialData,
  categories,
  onSubmit,
}) => {
  const [amount, setAmount] = useState<string>('');
  const [categoryId, setCategoryId] = useState<number>(categories[0]?.id || 1);
  const [description, setDescription] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('GPay');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setAmount(String(initialData.amount));
      setCategoryId(initialData.category_id);
      setDescription(initialData.description);
      setNotes(initialData.notes || '');
      setDate(initialData.date);
      setPaymentMethod(initialData.payment_method);
    } else {
      setAmount('');
      setCategoryId(categories[0]?.id || 1);
      setDescription('');
      setNotes('');
      setDate(new Date().toISOString().split('T')[0]);
      setPaymentMethod('GPay');
    }
  }, [initialData, isOpen, categories]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numAmount = parseFloat(amount);

    if (isNaN(numAmount) || numAmount <= 0) {
      setError('Amount must be a positive number');
      return;
    }
    if (!description.trim()) {
      setError('Description is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        amount: numAmount,
        category_id: categoryId,
        description: description.trim(),
        notes: notes.trim() || undefined,
        date,
        payment_method: paymentMethod,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save expense');
    } finally {
      setLoading(false);
    }
  };

  const categoryOptions = categories.map((c) => ({
    value: c.id,
    label: `${c.name} (${c.expense_count} items)`,
  }));

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialData ? 'Edit Expense Record' : 'Log New Expense'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Amount (₹)"
            type="number"
            step="0.01"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
            className="glass-input text-lg font-bold"
          />
          <Input
            label="Date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            className="glass-input"
          />
        </div>

        <Input
          label="Description"
          placeholder="e.g. Grocery shopping, Electricity bill..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          className="glass-input"
        />

        <Select
          label="Category"
          value={categoryId}
          onChange={(e) => setCategoryId(Number(e.target.value))}
          options={categoryOptions}
        />

        {/* Visual Payment Method Radio Buttons */}
        <div className="space-y-1.5">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
            Payment Tag
          </label>
          <div className="grid grid-cols-3 gap-2">
            {PAYMENT_METHODS.map((pm) => {
              const isSelected = paymentMethod === pm;
              return (
                <button
                  type="button"
                  key={pm}
                  onClick={() => setPaymentMethod(pm)}
                  className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? 'bg-indigo-600/30 border-indigo-500 text-white shadow-lg shadow-indigo-600/20'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  {pm}
                </button>
              );
            })}
          </div>
        </div>

        <div className="w-full space-y-1.5">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
            Notes / Memo (Optional)
          </label>
          <textarea
            rows={2}
            className="w-full rounded-xl bg-slate-900/80 border border-slate-800 text-slate-100 placeholder:text-slate-500 text-sm p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/80 shadow-inner"
            placeholder="Additional context or invoice memo..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={loading}>
            {initialData ? 'Save Changes' : 'Confirm Expense'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
