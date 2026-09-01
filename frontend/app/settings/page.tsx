'use client';

import React, { useState } from 'react';
import { Plus, Tag, Trash2, Edit2, AlertCircle, Shield, Key, LogOut, User as UserIcon, CheckCircle2 } from 'lucide-react';
import { CategoryWithCount } from '../../types';
import { useCategories } from '../../hooks/useCategories';
import { useAuth } from '../../context/AuthContext';
import { changePassword } from '../../lib/api/auth';
import { Header } from '../../components/shared/Header';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Button } from '../../components/ui/button';
import { Modal } from '../../components/ui/modal';
import { useToast } from '../../components/ui/toast';
import { ApiError } from '../../lib/api/client';

export default function SettingsPage() {
  const { user, logoutAll } = useAuth();
  const { categories, loading, addCategory, editCategory, removeCategory } = useCategories();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState<'categories' | 'security'>('categories');

  // Category state
  const [newCategoryName, setNewCategoryName] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CategoryWithCount | null>(null);
  const [editName, setEditName] = useState('');
  const [deletingCategory, setDeletingCategory] = useState<CategoryWithCount | null>(null);
  const [reassignTargetId, setReassignTargetId] = useState<string>('');

  // Password state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Logout all state
  const [isLoggingOutAll, setIsLoggingOutAll] = useState(false);

  const handleAddCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategoryName.trim()) return;

    try {
      setIsAdding(true);
      await addCategory(newCategoryName.trim());
      setNewCategoryName('');
      showToast('New category created successfully.', 'success');
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
      showToast('Category name updated successfully.', 'success');
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
      showToast('Category has been deleted.', 'success');
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to delete category', 'error');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(false);

    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setIsChangingPassword(true);
    try {
      await changePassword({ old_password: oldPassword, new_password: newPassword });
      setPasswordSuccess(true);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
      showToast('Your password has been updated and other sessions revoked.', 'success');
    } catch (err) {
      if (err instanceof ApiError) {
        setPasswordError(err.message);
      } else {
        setPasswordError('Failed to change password. Please verify current password.');
      }
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleLogoutAll = async () => {
    if (!window.confirm('Are you sure you want to sign out from all devices? You will be returned to the login screen.')) {
      return;
    }

    setIsLoggingOutAll(true);
    try {
      await logoutAll();
    } catch {
      setIsLoggingOutAll(false);
    }
  };

  const otherCategories = categories.filter((c) => deletingCategory && c.id !== deletingCategory.id);

  return (
    <div className="space-y-6 sm:space-y-8 max-w-5xl mx-auto animate-fade-in-up">
      <Header
        title="Settings & Preferences"
        subtitle="Manage dynamic categories, account security, and active sessions."
      />

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 dark:border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab('categories')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-bold transition-all ${
            activeTab === 'categories'
              ? 'bg-indigo-600/10 dark:bg-indigo-600/20 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-900'
          }`}
        >
          <Tag className="w-4 h-4" />
          <span>Expense Categories</span>
        </button>

        <button
          onClick={() => setActiveTab('security')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-bold transition-all ${
            activeTab === 'security'
              ? 'bg-indigo-600/10 dark:bg-indigo-600/20 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-900'
          }`}
        >
          <Shield className="w-4 h-4" />
          <span>Account & Security</span>
        </button>
      </div>

      {activeTab === 'categories' ? (
        <div className="space-y-6">
          {/* Add Category Form */}
          <Card className="p-4 sm:p-6">
            <CardHeader className="p-0 pb-3 sm:pb-4">
              <CardTitle className="text-sm sm:text-base flex items-center gap-2">
                <Tag className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                <span>Create New Custom Category</span>
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
            <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-3 sm:mb-4">
              Available Categories ({categories.length})
            </h3>
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-16 rounded-xl glass-card animate-pulse bg-slate-100 dark:bg-slate-800/40" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {categories.map((cat) => (
                  <div
                    key={cat.id}
                    className="flex items-center justify-between p-3.5 sm:p-4 rounded-xl glass-card border border-slate-200 dark:border-slate-800 shadow-sm"
                  >
                    <div className="flex items-center space-x-3 min-w-0 flex-1 mr-2">
                      <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold shrink-0">
                        {cat.name.charAt(0)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h4 className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate">{cat.name}</h4>
                        <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate">
                          {cat.expense_count} your {cat.expense_count === 1 ? 'expense' : 'expenses'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1 sm:space-x-2 shrink-0">
                      <button
                        onClick={() => {
                          setEditingCategory(cat);
                          setEditName(cat.name);
                        }}
                        className="p-1.5 sm:p-2 rounded-lg text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Rename Category"
                      >
                        <Edit2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      </button>
                      <button
                        onClick={() => {
                          setDeletingCategory(cat);
                          setReassignTargetId(otherCategories[0]?.id ? String(otherCategories[0].id) : '');
                        }}
                        className="p-1.5 sm:p-2 rounded-lg text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-slate-800 transition-colors"
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
        </div>
      ) : (
        /* Account & Security Tab */
        <div className="space-y-6">
          {/* User Profile Card */}
          {user && (
            <Card className="p-6">
              <CardHeader className="p-0 pb-4">
                <CardTitle className="text-base flex items-center space-x-2">
                  <UserIcon className="w-5 h-5 text-indigo-500" />
                  <span>Account Profile</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="flex items-center space-x-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white text-xl font-bold">
                    {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">
                      {user.full_name || 'ExpenseFlow User'}
                    </h3>
                    <p className="text-xs text-slate-500 font-mono">{user.email}</p>
                    <div className="mt-1 flex items-center space-x-2">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                        {user.is_verified ? 'Verified Account' : 'Active Account'}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Change Password Form */}
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-base flex items-center space-x-2">
                <Key className="w-5 h-5 text-indigo-500" />
                <span>Change Account Password</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {passwordError && (
                <div className="mb-4 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-2.5 text-rose-600 dark:text-rose-400 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{passwordError}</span>
                </div>
              )}
              {passwordSuccess && (
                <div className="mb-4 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start space-x-2.5 text-emerald-600 dark:text-emerald-400 text-xs">
                  <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>Password updated successfully!</span>
                </div>
              )}

              <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
                <div>
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">
                    Current Password
                  </label>
                  <input
                    type="password"
                    required
                    value={oldPassword}
                    onChange={(e) => setOldPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">
                    New Password (min. 8 characters)
                  </label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <Button type="submit" variant="primary" isLoading={isChangingPassword} className="text-xs font-bold py-2.5">
                  Update Password
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Active Sessions & Logout All Devices */}
          <Card className="p-6 border-rose-500/20 bg-rose-500/5">
            <CardHeader className="p-0 pb-3">
              <CardTitle className="text-base flex items-center space-x-2 text-rose-600 dark:text-rose-400">
                <LogOut className="w-5 h-5" />
                <span>Session Management</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 space-y-3">
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Sign out of all other browsers, mobile apps, and active sessions across all devices.
              </p>
              <Button
                type="button"
                variant="danger"
                isLoading={isLoggingOutAll}
                onClick={handleLogoutAll}
                className="text-xs font-bold py-2.5"
              >
                Sign Out from All Devices
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

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
          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-200 dark:border-slate-800">
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
                <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                <div className="text-xs text-amber-700 dark:text-amber-200/90 leading-relaxed">
                  This category is currently linked to{' '}
                  <span className="font-bold text-amber-900 dark:text-amber-100">{deletingCategory.expense_count} of your expenses</span>.
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
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Are you sure you want to delete <span className="font-bold text-slate-900 dark:text-white">&quot;{deletingCategory?.name}&quot;</span>? This action cannot be undone.
            </p>
          )}

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-200 dark:border-slate-800">
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
