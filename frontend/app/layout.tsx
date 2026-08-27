import React from 'react';
import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import '../styles/globals.css';
import { ToastProvider } from '../components/ui/toast';
import { Sidebar } from '../components/shared/Sidebar';

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['300', '400', '500', '600', '700', '800'],
});

export const metadata: Metadata = {
  title: 'ExpenseFlow — Smart Personal Finance & Expense Tracker',
  description: 'Track daily expenses, set budget goals, analyze spending trends, and export financial data.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${jakarta.variable} font-sans ambient-bg text-slate-100 flex min-h-screen relative`}>
        {/* Ambient Glow Orbs */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none -z-10" />
        <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10" />

        <ToastProvider>
          <Sidebar />
          <main className="flex-1 p-6 md:p-10 overflow-y-auto min-h-screen relative z-10 max-w-7xl mx-auto">
            {children}
          </main>
        </ToastProvider>
      </body>
    </html>
  );
}
