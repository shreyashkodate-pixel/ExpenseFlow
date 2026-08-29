'use client';

import React, { useState } from 'react';
import { Expense } from '../../types';
import { useExpenses } from '../../hooks/useExpenses';
import { useCategories } from '../../hooks/useCategories';
import { Header } from '../../components/shared/Header';
import { ExpenseFilters } from '../../components/expenses/ExpenseFilters';
import { ExpenseTable } from '../../components/expenses/ExpenseTable';
import { ExpenseFormModal } from '../../components/expenses/ExpenseFormModal';
import { useToast } from '../../components/ui/toast';

export default function ExpensesPage() {
  const {
    expenses,
    total,
    totalPages,
    loading,
    filters,
    updateFilters,
    addExpense,
    editExpense,
    removeExpense,
    handleExport,
  } = useExpenses();

  const { categories } = useCategories();
  const { showToast } = useToast();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);

  const handleOpenAddModal = () => {
    setEditingExpense(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (expense: Expense) => {
    setEditingExpense(expense);
    setIsModalOpen(true);
  };

  const handleDeleteExpense = async (id: number) => {
    if (confirm('Are you sure you want to delete this expense record?')) {
      try {
        await removeExpense(id);
        showToast('Expense deleted successfully', 'success');
      } catch {
        showToast('Failed to delete expense', 'error');
      }
    }
  };

  const handleExportCsv = async () => {
    try {
      await handleExport('csv');
      showToast('CSV export downloaded', 'success');
    } catch {
      showToast('Failed to download CSV', 'error');
    }
  };

  const handleExportPdf = async () => {
    try {
      await handleExport('pdf');
      showToast('PDF export downloaded', 'success');
    } catch {
      showToast('Failed to download PDF', 'error');
    }
  };

  const handleResetFilters = () => {
    updateFilters({
      search: '',
      category_id: undefined,
      payment_method: undefined,
      start_date: undefined,
      end_date: undefined,
      min_amount: undefined,
      max_amount: undefined,
      page: 1,
    });
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Header
        title="Expense Tracker"
        subtitle="Filter, search, export, and manage your transaction records."
        onAddExpense={handleOpenAddModal}
        onExportCsv={handleExportCsv}
        onExportPdf={handleExportPdf}
      />

      {/* Filter Controls */}
      <ExpenseFilters
        filters={filters}
        categories={categories}
        onFilterChange={updateFilters}
        onReset={handleResetFilters}
      />

      {/* Paginated Expenses Data Table */}
      <ExpenseTable
        expenses={expenses}
        loading={loading}
        page={filters.page || 1}
        totalPages={totalPages}
        totalItems={total}
        onPageChange={(page) => updateFilters({ page })}
        onEdit={handleOpenEditModal}
        onDelete={handleDeleteExpense}
      />

      {/* Add / Edit Expense Modal */}
      <ExpenseFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        initialData={editingExpense}
        categories={categories}
        onSubmit={async (data) => {
          if (editingExpense) {
            await editExpense(editingExpense.id, data);
            showToast('Expense updated successfully', 'success');
          } else {
            await addExpense(data);
            showToast('Expense created successfully', 'success');
          }
        }}
      />
    </div>
  );
}
