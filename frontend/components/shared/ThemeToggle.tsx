'use client';

import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon } from 'lucide-react';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className={`w-9 h-9 rounded-xl bg-slate-900/60 border border-slate-800 animate-pulse ${className}`} />
    );
  }

  const isDark = resolvedTheme === 'dark' || theme === 'dark';

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className={`relative p-2 rounded-xl border transition-all duration-300 group focus:outline-none focus:ring-2 focus:ring-indigo-500/50 ${
        isDark
          ? 'bg-slate-900/80 border-slate-800 text-amber-300 hover:bg-slate-800 hover:border-amber-500/40 hover:shadow-lg hover:shadow-amber-500/10'
          : 'bg-white/90 border-slate-200 text-indigo-600 hover:bg-slate-50 hover:border-indigo-500/40 hover:shadow-lg hover:shadow-indigo-500/10 shadow-sm'
      } ${className}`}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
      title={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      <div className="relative w-5 h-5 flex items-center justify-center">
        {isDark ? (
          <Sun className="w-4.5 h-4.5 text-amber-400 group-hover:rotate-90 transition-transform duration-500" />
        ) : (
          <Moon className="w-4.5 h-4.5 text-indigo-600 group-hover:-rotate-12 transition-transform duration-300" />
        )}
      </div>
    </button>
  );
};
