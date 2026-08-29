'use client';

import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full relative">
      {/* Top Mobile Navbar (Hidden on lg+ screens) */}
      <MobileNav onOpenSidebar={() => setIsSidebarOpen(true)} />

      {/* Sidebar (Fixed on Desktop, Slide-over on Mobile) */}
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      {/* Main Content Area with Adaptive Responsive Padding */}
      <main className="flex-1 w-full min-w-0 p-4 sm:p-6 lg:p-10 pt-20 lg:pt-8 overflow-y-auto min-h-screen relative z-10 max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  );
};
