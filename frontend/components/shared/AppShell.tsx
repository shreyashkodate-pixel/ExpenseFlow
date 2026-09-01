'use client';

import React, { useState } from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';

interface AppShellProps {
  children: React.ReactNode;
}

const AUTH_PATHS = ['/login', '/register', '/forgot-password', '/reset-password'];

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const pathname = usePathname();

  const isAuthPage = AUTH_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));

  if (isAuthPage) {
    return (
      <div className="flex min-h-screen w-full relative items-center justify-center p-4 sm:p-6 lg:p-8">
        <main className="w-full max-w-md relative z-10">
          {children}
        </main>
      </div>
    );
  }

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
