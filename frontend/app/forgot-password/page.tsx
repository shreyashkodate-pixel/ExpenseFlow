'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Sparkles, Mail, ArrowLeft, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import { forgotPassword } from '../../lib/api/auth';
import { ApiError } from '../../lib/api/client';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setErrorMsg('Please enter your email address.');
      return;
    }

    setErrorMsg(null);
    setIsLoading(true);

    try {
      await forgotPassword(email);
      setIsSuccess(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Failed to process request. Please try again.');
      }
    } finally {
      setIsLoading(false);
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
          Recover Password
        </h1>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          We&apos;ll help you securely reset your password
        </p>
      </div>

      {/* Card Container */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 shadow-2xl backdrop-blur-xl">
        {errorMsg && (
          <div className="mb-5 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3 text-rose-600 dark:text-rose-400 text-sm animate-shake">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">{errorMsg}</div>
          </div>
        )}

        {isSuccess ? (
          <div className="text-center py-4 space-y-4">
            <div className="w-14 h-14 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-500">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
              Check Your Email
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              If an account with <span className="font-semibold text-slate-900 dark:text-slate-100">{email}</span> exists in ExpenseFlow, we have sent a secure password reset link to your email inbox.
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Please check your inbox (and spam/junk folder) and click the link to reset your password. The link is valid for 60 minutes.
            </p>

            <div className="pt-6">
              <Link
                href="/login"
                className="w-full inline-flex items-center justify-center space-x-2 py-3 px-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-md transition-all"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Return to Sign In</span>
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                Registered Email Address
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-11 pr-4 py-3 rounded-2xl bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all duration-200 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{isLoading ? 'Processing...' : 'Send Recovery Link'}</span>
            </button>

            <div className="pt-4 text-center">
              <Link
                href="/login"
                className="inline-flex items-center space-x-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Sign In</span>
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
