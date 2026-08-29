import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon, type = 'text', id, ...props }, ref) => {
    const generatedId = React.useId();
    const inputId = id || generatedId;

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {icon && <div className="absolute left-3 text-slate-400 pointer-events-none">{icon}</div>}
          <input
            ref={ref}
            id={inputId}
            type={type}
            className={twMerge(
              clsx(
                'w-full rounded-lg bg-white/90 dark:bg-slate-900/80 border border-slate-300 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 text-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/80 focus:border-indigo-500 transition-all shadow-sm dark:shadow-inner',
                icon && 'pl-9',
                error && 'border-rose-500/80 focus:ring-rose-500 focus:border-rose-500',
                className
              )
            )}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-rose-500 dark:text-rose-400 font-medium">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
