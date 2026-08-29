import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={twMerge(clsx('glass-card rounded-xl p-6 shadow-md', className))} {...props}>
    {children}
  </div>
);

export const CardHeader = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={twMerge(clsx('flex flex-col space-y-1.5 pb-4', className))} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={twMerge(clsx('text-lg font-semibold leading-none tracking-tight text-slate-900 dark:text-white', className))} {...props}>
    {children}
  </h3>
);

export const CardDescription = ({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p className={twMerge(clsx('text-sm text-slate-500 dark:text-slate-400', className))} {...props}>
    {children}
  </p>
);

export const CardContent = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={twMerge(clsx('pt-0', className))} {...props}>
    {children}
  </div>
);

export const CardFooter = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={twMerge(clsx('flex items-center pt-4 border-t border-slate-200/80 dark:border-slate-800/80', className))} {...props}>
    {children}
  </div>
);
