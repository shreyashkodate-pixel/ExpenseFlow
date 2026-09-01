'use client';

import React, { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { Sparkles } from 'lucide-react';

const PUBLIC_PATHS = ['/login', '/register', '/forgot-password', '/reset-password'];

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isPublicPath = PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated && !isPublicPath) {
        router.push('/login');
      } else if (isAuthenticated && isPublicPath) {
        router.push('/');
      }
    }
  }, [isAuthenticated, isLoading, isPublicPath, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-100">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur opacity-75 animate-pulse" />
            <div className="relative w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-7 h-7 text-indigo-400 animate-spin" />
            </div>
          </div>
          <div className="text-sm font-semibold tracking-wide text-slate-400 font-mono animate-pulse">
            AUTHENTICATING SESSION...
          </div>
        </div>
      </div>
    );
  }

  // If on a public path or authenticated, render children
  if (!isAuthenticated && !isPublicPath) {
    return null; // Will redirect in useEffect
  }

  return <>{children}</>;
};
