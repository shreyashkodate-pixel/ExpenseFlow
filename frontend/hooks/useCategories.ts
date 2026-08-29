import { useState, useEffect, useCallback } from 'react';
import { CategoryWithCount } from '../types';
import { getCategories, createCategory, updateCategory, deleteCategory } from '../lib/api/categories';

export function useCategories() {
  const [categories, setCategories] = useState<CategoryWithCount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCategories();
      setCategories(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const addCategory = async (name: string) => {
    const newCat = await createCategory({ name });
    await fetchCategories();
    return newCat;
  };

  const editCategory = async (id: number, name: string) => {
    const updated = await updateCategory(id, { name });
    await fetchCategories();
    return updated;
  };

  const removeCategory = async (id: number, reassignTo?: number) => {
    await deleteCategory(id, reassignTo);
    await fetchCategories();
  };

  return {
    categories,
    loading,
    error,
    refreshCategories: fetchCategories,
    addCategory,
    editCategory,
    removeCategory,
  };
}
