'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Download, Smartphone, X, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
}

interface PWAContextType {
  isInstallable: boolean;
  isInstalled: boolean;
  installApp: () => Promise<void>;
  isIOS: boolean;
}

const PWAContext = createContext<PWAContextType>({
  isInstallable: false,
  isInstalled: false,
  installApp: async () => {},
  isIOS: false,
});

export const usePWA = () => useContext(PWAContext);

export const PWAProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // 1. Register Service Worker
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => console.log('ExpenseFlow PWA Service Worker active:', reg.scope))
        .catch((err) => console.log('SW registration notice:', err));
    }

    // 2. Check if already installed
    if (typeof window !== 'undefined') {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      const isIOSStandalone = 'standalone' in window.navigator && Boolean((window.navigator as unknown as { standalone: boolean }).standalone);
      if (isStandalone || isIOSStandalone) {
        setIsInstalled(true);
      }

      // Check for iOS Safari
      const userAgent = window.navigator.userAgent.toLowerCase();
      const isIOSDevice = /iphone|ipad|ipod/.test(userAgent);
      setIsIOS(isIOSDevice);
    }

    // 3. Listen for BeforeInstallPrompt event (Android Chrome, Desktop Chrome, Edge)
    const handleBeforeInstallPrompt = (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
      // Show install banner if not dismissed before
      const hasDismissed = localStorage.getItem('pwa_dismissed');
      if (!hasDismissed) {
        setShowBanner(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
      setShowBanner(false);
    });

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const installApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const choiceResult = await deferredPrompt.userChoice;
      if (choiceResult.outcome === 'accepted') {
        setIsInstalled(true);
        setIsInstallable(false);
      }
      setDeferredPrompt(null);
      setShowBanner(false);
    }
  };

  const dismissBanner = () => {
    setShowBanner(false);
    localStorage.setItem('pwa_dismissed', 'true');
  };

  return (
    <PWAContext.Provider value={{ isInstallable, isInstalled, installApp, isIOS }}>
      {children}

      {/* Modern In-App PWA Install Banner */}
      <AnimatePresence>
        {showBanner && isInstallable && !isInstalled && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.95 }}
            className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:w-96 z-50 glass-panel p-4 rounded-2xl border border-indigo-500/40 shadow-2xl bg-slate-950/95 dark:bg-slate-950/95"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30 shrink-0">
                  <Smartphone className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">Install ExpenseFlow</h4>
                  <p className="text-xs text-slate-400 mt-0.5">Add to Home Screen for fast mobile access & offline mode</p>
                </div>
              </div>
              <button
                onClick={dismissBanner}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
                aria-label="Dismiss banner"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3.5 flex items-center gap-2">
              <button
                onClick={installApp}
                className="flex-1 inline-flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Install Mobile App</span>
              </button>
              <button
                onClick={dismissBanner}
                className="py-2 px-3 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Later
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </PWAContext.Provider>
  );
};

export const PWAInstallButton: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { isInstallable, isInstalled, installApp, isIOS } = usePWA();
  const [showIOSModal, setShowIOSModal] = useState(false);

  if (isInstalled) {
    return (
      <div className={`flex items-center space-x-2 text-xs text-emerald-400 font-semibold px-3 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 ${className}`}>
        <CheckCircle2 className="w-4 h-4" />
        <span>App Installed</span>
      </div>
    );
  }

  if (!isInstallable && !isIOS) {
    return null;
  }

  return (
    <>
      <button
        onClick={() => (isIOS ? setShowIOSModal(true) : installApp())}
        className={`w-full inline-flex items-center justify-between px-3.5 py-2.5 rounded-xl border border-indigo-500/30 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 hover:border-indigo-500/60 text-indigo-600 dark:text-indigo-300 transition-all group cursor-pointer ${className}`}
        title="Install ExpenseFlow as a native app on your phone"
      >
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
            <Smartphone className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-slate-900 dark:text-white">Install App</span>
        </div>
        <Download className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
      </button>

      {/* iOS Instructions Modal */}
      <AnimatePresence>
        {showIOSModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel max-w-sm w-full p-5 rounded-2xl border border-indigo-500/40 shadow-2xl space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Smartphone className="w-5 h-5 text-indigo-400" />
                  <span>Install on iPhone / iPad</span>
                </h3>
                <button onClick={() => setShowIOSModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="text-xs text-slate-300 space-y-2.5 leading-relaxed">
                <p>To install ExpenseFlow on iOS Safari:</p>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-[10px]">1</span>
                    <span>Tap the <strong>Share</strong> button at bottom of Safari.</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-[10px]">2</span>
                    <span>Scroll down and tap <strong>&quot;Add to Home Screen&quot;</strong>.</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-[10px]">3</span>
                    <span>Tap <strong>Add</strong> in the top right.</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setShowIOSModal(false)}
                className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold"
              >
                Got It
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
