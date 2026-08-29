import React from 'react';
import type { Metadata, Viewport } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import '../styles/globals.css';
import { ToastProvider } from '../components/ui/toast';
import { ThemeProvider } from '../components/shared/ThemeProvider';
import { AppShell } from '../components/shared/AppShell';

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['300', '400', '500', '600', '700', '800'],
});

export const metadata: Metadata = {
  title: 'ExpenseFlow — Smart Personal Finance & Expense Tracker',
  description: 'Track daily expenses, set budget goals, analyze spending trends, and export financial data.',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${jakarta.variable} font-sans ambient-bg text-slate-100 min-h-screen relative overflow-x-hidden transition-colors duration-300`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          {/* Ambient Glow Orbs */}
          <div className="fixed top-0 left-1/4 w-72 md:w-96 h-72 md:h-96 bg-indigo-600/10 dark:bg-indigo-600/10 rounded-full blur-3xl pointer-events-none -z-10" />
          <div className="fixed bottom-0 right-1/4 w-72 md:w-96 h-72 md:h-96 bg-purple-600/10 dark:bg-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10" />

          <ToastProvider>
            <AppShell>
              {children}
            </AppShell>
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
