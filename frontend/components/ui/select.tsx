import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: Array<{ value: string | number; label: string }>;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, id, ...props }, ref) => {
    const generatedId = React.useId();
    const selectId = id || generatedId;

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={selectId} className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={twMerge(
              clsx(
                'w-full appearance-none rounded-lg bg-white/90 dark:bg-slate-900/80 border border-slate-300 dark:border-slate-800 text-slate-900 dark:text-slate-100 text-sm py-2 pl-3 pr-8 focus:outline-none focus:ring-2 focus:ring-indigo-500/80 focus:border-indigo-500 transition-all shadow-sm dark:shadow-inner cursor-pointer',
                error && 'border-rose-500/80 focus:ring-rose-500 focus:border-rose-500',
                className
              )
            )}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 py-1">
                {opt.label}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-2.5 pointer-events-none text-slate-400">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>
        {error && <p className="text-xs text-rose-500 dark:text-rose-400 font-medium">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';
