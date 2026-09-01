'use client';

import React, { useEffect, useRef, useState } from 'react';
import Script from 'next/script';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../ui/toast';
import { ApiError } from '../../lib/api/client';

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
          }) => void;
          renderButton: (
            parent: HTMLElement,
            options: {
              type?: 'standard' | 'icon';
              theme?: 'outline' | 'filled_blue' | 'filled_black';
              size?: 'large' | 'medium' | 'small';
              text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
              shape?: 'rectangular' | 'pill' | 'circle' | 'square';
              width?: number | string;
              logo_alignment?: 'left' | 'center';
            }
          ) => void;
          prompt: () => void;
        };
      };
    };
  }
}

interface GoogleSignInButtonProps {
  text?: 'signin_with' | 'signup_with' | 'continue_with';
  onError?: (error: string) => void;
}

export const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({
  text = 'continue_with',
  onError,
}) => {
  const { googleLogin } = useAuth();
  const { showToast } = useToast();
  const buttonRef = useRef<HTMLDivElement>(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.trim();

  // Check if GIS script was already injected/cached
  useEffect(() => {
    if (typeof window !== 'undefined' && window.google?.accounts?.id) {
      setScriptLoaded(true);
    }
  }, []);

  const handleCredentialResponse = React.useCallback(async (response: { credential: string }) => {
    if (!response.credential) {
      if (onError) onError('No credential received from Google.');
      return;
    }

    setIsLoading(true);
    try {
      await googleLogin({ credential: response.credential });
      showToast('Google Sign-In Successful. Welcome to ExpenseFlow!', 'success');
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Google Sign-In failed. Please try again.';
      if (onError) onError(msg);
      showToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [googleLogin, showToast, onError]);

  useEffect(() => {
    if (!scriptLoaded || !clientId || !window.google?.accounts?.id || !buttonRef.current) {
      return;
    }

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse,
      });

      // Clear any previously rendered button
      buttonRef.current.innerHTML = '';

      window.google.accounts.id.renderButton(buttonRef.current, {
        type: 'standard',
        theme: 'outline',
        size: 'large',
        text: text,
        shape: 'pill',
        width: 380,
        logo_alignment: 'center',
      });
    } catch (err) {
      console.error('Failed to initialize Google Sign-In:', err);
    }
  }, [scriptLoaded, clientId, text, handleCredentialResponse]);

  const handleFallbackClick = () => {
    if (!clientId || clientId.includes('your_google_oauth_client_id')) {
      const msg = 'Google Client ID is not configured. Please set NEXT_PUBLIC_GOOGLE_CLIENT_ID in your environment.';
      if (onError) onError(msg);
      showToast(msg, 'error');
      return;
    }

    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt();
    }
  };

  return (
    <div className="w-full">
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setScriptLoaded(true)}
      />

      {/* Render container for official Google GIS Button */}
      {clientId && !clientId.includes('your_google_oauth_client_id') ? (
        <div className="w-full flex justify-center min-h-[44px]">
          <div ref={buttonRef} className="w-full flex justify-center [&>div]:!w-full [&>div>iframe]:!w-full" />
        </div>
      ) : (
        /* Fallback styled button with configuration hint */
        <button
          type="button"
          onClick={handleFallbackClick}
          disabled={isLoading}
          className="w-full py-3.5 px-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700/80 hover:border-slate-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-200 font-semibold text-sm flex items-center justify-center space-x-3 shadow-sm hover:shadow transition-all duration-200 disabled:opacity-50"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          <span>{isLoading ? 'Connecting...' : text === 'signup_with' ? 'Sign up with Google' : 'Continue with Google'}</span>
        </button>
      )}
    </div>
  );
};
