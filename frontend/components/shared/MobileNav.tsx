'use client';

import React from 'react';
import { Menu, Sparkles } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface MobileNavProps {
  onOpenSidebar: () => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ onOpenSidebar }) => {
  return (
    <header className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-slate-950/85 backdrop-blur-xl border-b border-slate-800/80 z-30 px-4 flex items-center justify-between">
      {/* Brand Logo */}
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg blur opacity-75 animate-pulse" />
          <div className="relative w-8 h-8 rounded-lg bg-slate-950 border border-slate-700/60 flex items-center justify-center text-indigo-400">
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
        </div>
        <div>
          <span className="text-lg font-extrabold text-white gradient-text tracking-tight">ExpenseFlow</span>
        </div>
      </div>

      {/* Right Action: Theme Toggle & Hamburger */}
      <div className="flex items-center space-x-2">
        <ThemeToggle />
        <button
          onClick={onOpenSidebar}
          className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 hover:text-white hover:border-indigo-500/50 transition-colors active:scale-95"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};
