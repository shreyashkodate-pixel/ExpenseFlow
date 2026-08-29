'use client';

import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  className = '',
  showLabel = false,
}) => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div
        className={`${
          showLabel
            ? 'w-full h-11 rounded-xl bg-slate-900/40 border border-slate-800'
            : 'w-9 h-9 rounded-xl bg-slate-900/60 border border-slate-800'
        } animate-pulse ${className}`}
      />
    );
  }

  const isDark = resolvedTheme === 'dark' || theme === 'dark';

  if (showLabel) {
    return (
      <button
        onClick={() => setTheme(isDark ? 'light' : 'dark')}
        className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl border transition-all duration-300 group cursor-pointer ${
          isDark
            ? 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-indigo-500/50 hover:bg-slate-800/80 hover:text-white'
            : 'bg-white/90 border-slate-200 text-slate-700 hover:border-indigo-500/50 hover:bg-slate-100 hover:text-indigo-600 shadow-sm'
        } ${className}`}
        aria-label="Toggle dark/light theme"
      >
        <div className="flex items-center space-x-3">
          <div
            className={`w-7 h-7 rounded-lg flex items-center justify-center transition-colors ${
              isDark ? 'bg-amber-500/10 text-amber-400' : 'bg-indigo-500/10 text-indigo-600'
            }`}
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </div>
          <span className="text-xs font-semibold">{isDark ? 'Dark Mode' : 'Light Mode'}</span>
        </div>

        {/* Pill switch indicator */}
        <div
          className={`w-10 h-5 rounded-full transition-colors p-0.5 relative ${
            isDark ? 'bg-indigo-600' : 'bg-slate-300'
          }`}
        >
          <div
            className={`w-4 h-4 rounded-full bg-white transition-transform shadow-md ${
              isDark ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </div>
      </button>
    );
  }

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className={`relative p-2 rounded-xl border transition-all duration-300 group focus:outline-none focus:ring-2 focus:ring-indigo-500/50 cursor-pointer ${
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
