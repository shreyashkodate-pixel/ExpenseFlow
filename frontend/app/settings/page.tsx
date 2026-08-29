'use client';

import React, { useState } from 'react';
import { Plus, Tag, Trash2, Edit2, AlertCircle } from 'lucide-react';
import { CategoryWithCount } from '../../types';
import { useCategories } from '../../hooks/useCategories';
import { Header } from '../../components/shared/Header';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Button } from '../../components/ui/button';
import { Modal } from '../../components/ui/modal';
import { useToast } from '../../components/ui/toast';

export default function SettingsPage() {
  const { categories, loading, addCategory, editCategory, removeCategory } = useCategories();
  const { showToast } = useToast();

  const [newCategoryName, setNewCategoryName] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  // Edit category modal state
  const [editingCategory, setEditingCategory] = useState<CategoryWithCount | null>(null);
  const [editName, setEditName] = useState('');

  // Delete category modal state
  const [deletingCategory, setDeletingCategory] = useState<CategoryWithCount | null>(null);
  const [reassignTargetId, setReassignTargetId] = useState<string>('');

  const handleAddCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategoryName.trim()) return;

    try {
      setIsAdding(true);
      await addCategory(newCategoryName.trim());
      setNewCategoryName('');
      showToast('Category added successfully', 'success');
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to add category', 'error');
    } finally {
      setIsAdding(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingCategory || !editName.trim()) return;

    try {
      await editCategory(editingCategory.id, editName.trim());
      setEditingCategory(null);
      showToast('Category updated successfully', 'success');
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to update category', 'error');
    }
  };

  const handleDeleteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!deletingCategory) return;

    try {
      const reassignId = reassignTargetId ? Number(reassignTargetId) : undefined;
      await removeCategory(deletingCategory.id, reassignId);
      setDeletingCategory(null);
      showToast('Category deleted successfully', 'success');
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to delete category', 'error');
    }
  };

  const otherCategories = categories.filter((c) => deletingCategory && c.id !== deletingCategory.id);

  return (
    <div className="space-y-6 sm:space-y-8 max-w-5xl mx-auto">
      <Header
        title="Settings & Categories"
        subtitle="Manage dynamic expense categories and reassignment rules."
      />

      {/* Add Category Form */}
      <Card className="p-4 sm:p-6">
        <CardHeader className="p-0 pb-3 sm:pb-4">
          <CardTitle className="text-sm sm:text-base flex items-center gap-2">
            <Tag className="w-4 h-4 text-indigo-400" />
            <span>Create New Category</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <form onSubmit={handleAddCategory} className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <div className="flex-1">
              <Input
                placeholder="Category name (e.g. Subscriptions, Travel)..."
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                required
                className="text-xs sm:text-sm"
              />
            </div>
            <Button type="submit" variant="primary" isLoading={isAdding} className="gap-2 shrink-0 text-xs sm:text-sm py-2 sm:py-2.5">
              <Plus className="w-4 h-4" />
              <span>Add Category</span>
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Existing Categories Grid */}
      <div>
        <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Active Categories ({categories.length})</h3>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 rounded-xl glass-card animate-pulse bg-slate-800/40" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            {categories.map((cat) => (
              <div
                key={cat.id}
                className="flex items-center justify-between p-3.5 sm:p-4 rounded-xl glass-card border border-slate-800"
              >
                <div className="flex items-center space-x-3 min-w-0 flex-1 mr-2">
                  <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold shrink-0">
                    {cat.name.charAt(0)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs sm:text-sm font-semibold text-white truncate">{cat.name}</h4>
                    <p className="text-[11px] sm:text-xs text-slate-400 mt-0.5 truncate">
                      {cat.expense_count} associated {cat.expense_count === 1 ? 'expense' : 'expenses'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-1 sm:space-x-2 shrink-0">
                  <button
                    onClick={() => {
                      setEditingCategory(cat);
                      setEditName(cat.name);
                    }}
                    className="p-1.5 sm:p-2 rounded-lg text-slate-400 hover:text-indigo-300 hover:bg-slate-800 transition-colors"
                    title="Rename Category"
                  >
                    <Edit2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </button>
                  <button
                    onClick={() => {
                      setDeletingCategory(cat);
                      setReassignTargetId(otherCategories[0]?.id ? String(otherCategories[0].id) : '');
                    }}
                    className="p-1.5 sm:p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                    title="Delete Category"
                  >
                    <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Category Modal */}
      <Modal
        isOpen={Boolean(editingCategory)}
        onClose={() => setEditingCategory(null)}
        title="Rename Category"
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <Input
            label="Category Name"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            required
          />
          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
            <Button type="button" variant="outline" onClick={() => setEditingCategory(null)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete / Reassign Category Modal */}
      <Modal
        isOpen={Boolean(deletingCategory)}
        onClose={() => setDeletingCategory(null)}
        title={`Delete "${deletingCategory?.name}"`}
      >
        <form onSubmit={handleDeleteSubmit} className="space-y-4">
          {deletingCategory && deletingCategory.expense_count > 0 ? (
            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div className="text-xs text-amber-200/90 leading-relaxed">
                  This category is currently linked to{' '}
                  <span className="font-bold text-amber-100">{deletingCategory.expense_count} expenses</span>.
                  Select a replacement category to reassign them to before deletion.
                </div>
              </div>

              <Select
                label="Reassign Existing Expenses To"
                value={reassignTargetId}
                onChange={(e) => setReassignTargetId(e.target.value)}
                options={otherCategories.map((c) => ({ value: c.id, label: c.name }))}
                required
              />
            </div>
          ) : (
            <p className="text-sm text-slate-300">
              Are you sure you want to delete <span className="font-bold text-white">&quot;{deletingCategory?.name}&quot;</span>? This action cannot be undone.
            </p>
          )}

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="outline" onClick={() => setDeletingCategory(null)}>
              Cancel
            </Button>
            <Button type="submit" variant="danger">
              Confirm Deletion
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
