'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Receipt, PieChart, Wallet, Settings, Sparkles } from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Expenses', href: '/expenses', icon: Receipt },
  { name: 'Analytics', href: '/analytics', icon: PieChart },
  { name: 'Budget Goals', href: '/budget', icon: Wallet },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 flex flex-col h-screen sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl">
      {/* Brand Logo Header */}
      <div className="p-6 border-b border-slate-800/80 flex items-center space-x-3.5">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300 animate-pulse" />
          <div className="relative w-11 h-11 rounded-xl bg-slate-950 border border-slate-700/60 flex items-center justify-center text-indigo-400">
            <Sparkles className="w-6 h-6 text-indigo-400" />
          </div>
        </div>
        <div>
          <h1 className="text-xl font-extrabold tracking-tight text-white gradient-text">ExpenseFlow</h1>
          <p className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">Smart Finance Platform</p>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`relative flex items-center px-4 py-3.5 text-sm font-semibold rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600/30 via-indigo-600/15 to-transparent text-white border border-indigo-500/40 shadow-lg shadow-indigo-900/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40 border border-transparent'
              }`}
            >
              {isActive && (
                <span className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-gradient-to-b from-indigo-400 via-purple-400 to-pink-400 shadow-glow" />
              )}
              <Icon
                className={`w-5 h-5 mr-3.5 transition-all duration-200 ${
                  isActive ? 'text-indigo-400 scale-110' : 'text-slate-400 group-hover:text-indigo-300 group-hover:scale-105'
                }`}
              />
              <span className="tracking-wide">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* App Footer & Connection Badge */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-center justify-between text-xs shadow-inner">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-glow" />
            <span className="text-slate-300 font-medium">PostgreSQL Engine</span>
          </div>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            ONLINE
          </span>
        </div>
      </div>
    </aside>
  );
};
