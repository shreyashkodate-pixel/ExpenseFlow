import { z } from 'zod';

export const PaymentMethodEnum = z.enum([
  'Cash',
  'GPay',
  'Credit Card',
  'UPI',
  'Bank Transfer',
  'Others',
]);

export const expenseSchema = z.object({
  amount: z
    .number({ invalid_type_error: 'Amount must be a number' })
    .positive('Amount must be greater than 0'),
  category_id: z
    .number({ invalid_type_error: 'Please select a valid category' })
    .int()
    .positive('Category is required'),
  description: z
    .string()
    .min(1, 'Description is required')
    .max(255, 'Description cannot exceed 255 characters'),
  notes: z.string().max(1000, 'Notes cannot exceed 1000 characters').optional(),
  date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format'),
  payment_method: PaymentMethodEnum,
});

export const categorySchema = z.object({
  name: z
    .string()
    .min(2, 'Category name must be at least 2 characters')
    .max(50, 'Category name cannot exceed 50 characters'),
});

export const budgetSchema = z.object({
  amount: z
    .number({ invalid_type_error: 'Budget amount must be a number' })
    .positive('Budget amount must be greater than 0'),
  month: z
    .number()
    .int()
    .min(1, 'Month must be between 1 and 12')
    .max(12, 'Month must be between 1 and 12'),
  year: z
    .number()
    .int()
    .min(2000, 'Year must be valid'),
  category_id: z.number().int().positive().optional().nullable(),
});

export type ExpenseFormValues = z.infer<typeof expenseSchema>;
export type CategoryFormValues = z.infer<typeof categorySchema>;
export type BudgetFormValues = z.infer<typeof budgetSchema>;
