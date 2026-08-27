import { apiGet, apiPost, apiPut, apiDelete } from './client';
import { Category, CategoryWithCount, CategoryCreate } from '../../types';

export async function getCategories(): Promise<CategoryWithCount[]> {
  return apiGet<CategoryWithCount[]>('/categories');
}

export async function createCategory(data: CategoryCreate): Promise<Category> {
  return apiPost<Category, CategoryCreate>('/categories', data);
}

export async function updateCategory(
  id: number,
  data: CategoryCreate
): Promise<Category> {
  return apiPut<Category, CategoryCreate>(`/categories/${id}`, data);
}

export async function deleteCategory(
  id: number,
  reassignTo?: number
): Promise<void> {
  const params = reassignTo ? { reassign_to: reassignTo } : undefined;
  return apiDelete<void>(`/categories/${id}`, params);
}
