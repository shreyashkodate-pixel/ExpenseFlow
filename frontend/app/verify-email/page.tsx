'use client';

import React, { useEffect, useState, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Sparkles, CheckCircle2, AlertCircle, ArrowRight, Loader2, RotateCw, Mail } from 'lucide-react';
import { verifyEmail, resendVerification } from '../../lib/api/auth';
import { ApiError } from '../../lib/api/client';
import { useToast } from '../../components/ui/toast';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const { showToast } = useToast();

  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>(token ? 'verifying' : 'error');
  const [errorMessage, setErrorMessage] = useState<string>(
    token ? '' : 'No verification token provided in the link.'
  );

  // Resend link state
  const [resendEmail, setResendEmail] = useState('');
  const [isResending, setIsResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);

  useEffect(() => {
    if (!token) return;

    let isMounted = true;

    async function executeVerification() {
      try {
        await verifyEmail(token as string);
        if (isMounted) {
          setStatus('success');
          showToast('Email verified successfully! Welcome to ExpenseFlow.', 'success');
        }
      } catch (err) {
        if (isMounted) {
          setStatus('error');
          if (err instanceof ApiError) {
            setErrorMessage(err.message);
          } else {
            setErrorMessage('Invalid or expired verification link. Please request a new one.');
          }
        }
      }
    }

    executeVerification();

    return () => {
      isMounted = false;
    };
  }, [token, showToast]);

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resendEmail) return;

    setIsResending(true);
    try {
      await resendVerification(resendEmail);
      setResendSuccess(true);
      showToast('A new verification email has been sent!', 'success');
    } catch (err) {
      if (err instanceof ApiError) {
        showToast(err.message, 'error');
      } else {
        showToast('Failed to resend verification email.', 'error');
      }
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto animate-fade-in-up">
      {/* Brand Header */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center mb-3 relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur opacity-75 group-hover:opacity-100 transition duration-300 animate-pulse" />
          <div className="relative w-12 h-12 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <Sparkles className="w-6 h-6" />
          </div>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight gradient-text mb-1">
          Email Verification
        </h1>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Account activation & security validation
        </p>
      </div>

      {/* Card Container */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 shadow-2xl backdrop-blur-xl">
        {status === 'verifying' && (
          <div className="text-center py-8 space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
              Verifying Your Email...
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Please wait a moment while we validate your activation token.
            </p>
          </div>
        )}

        {status === 'success' && (
          <div className="text-center py-6 space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-500">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              Email Verified! 🎉
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Your ExpenseFlow account has been activated successfully. A welcome email has been sent to your inbox.
            </p>

            <div className="pt-6">
              <Link
                href="/"
                className="w-full inline-flex items-center justify-center space-x-2 py-3.5 px-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition-all"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="text-center py-4 space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-500">
              <AlertCircle className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
              Verification Failed
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {errorMessage || 'The verification link is invalid or has expired.'}
            </p>

            {resendSuccess ? (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-medium">
                A new verification email has been dispatched. Please check your inbox.
              </div>
            ) : (
              <form onSubmit={handleResend} className="pt-3 text-left space-y-3">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
                  Resend Verification Email
                </label>
                <div className="relative">
                  <Mail className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={resendEmail}
                    onChange={(e) => setResendEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-11 pr-4 py-2.5 rounded-2xl bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-all"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isResending}
                  className="w-full inline-flex items-center justify-center space-x-2 py-3 px-4 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold text-sm transition-all disabled:opacity-50"
                >
                  <RotateCw className={`w-4 h-4 ${isResending ? 'animate-spin' : ''}`} />
                  <span>{isResending ? 'Sending Link...' : 'Send New Verification Link'}</span>
                </button>
              </form>
            )}

            <div className="pt-4">
              <Link
                href="/login"
                className="inline-flex items-center space-x-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
              >
                <span>Return to Sign In</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full max-w-md mx-auto py-16 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-indigo-600" />
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
