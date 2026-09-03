'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Sparkles, TrendingUp, RotateCw, Lightbulb, PiggyBank, CheckCircle2, AlertTriangle, Flame, ShieldCheck, Clock } from 'lucide-react';
import { AIRecommendationResponse } from '../../types/ai';
import { getAIRecommendations, refreshAIRecommendations } from '../../lib/api/ai';
import { useToast } from '../ui/toast';

export function AIInsightsCard() {
  const [data, setData] = useState<AIRecommendationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { showToast } = useToast();

  const fetchInsights = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getAIRecommendations();
      setData(res);
    } catch {
      // Gracefully handle unconfigured AI or server errors
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      const res = await refreshAIRecommendations();
      setData(res);
      showToast('AI recommendations refreshed!', 'success');
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Failed to refresh AI insights', 'error');
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-500/5 via-purple-500/5 to-emerald-500/5 p-6 backdrop-blur-md animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="h-6 w-48 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
          <div className="h-8 w-24 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
        </div>
        <div className="space-y-3">
          <div className="h-4 w-3/4 bg-gray-200 dark:bg-gray-800 rounded"></div>
          <div className="h-20 bg-gray-200 dark:bg-gray-800 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 60) return 'text-indigo-500 bg-indigo-500/10 border-indigo-500/30';
    return 'text-amber-500 bg-amber-500/10 border-amber-500/30';
  };

  const getPacingStyle = (status: string) => {
    switch (status) {
      case 'exceeded':
        return {
          border: 'border-rose-500/30 dark:border-rose-500/20',
          bg: 'bg-rose-500/5 dark:bg-rose-950/20',
          badge: 'bg-rose-500/20 text-rose-500 dark:text-rose-400 border-rose-500/30',
          bar: 'bg-rose-500',
          icon: <AlertTriangle className="h-4 w-4 text-rose-500" />,
          label: 'Budget Exceeded',
        };
      case 'critical':
        return {
          border: 'border-rose-500/30 dark:border-rose-500/20',
          bg: 'bg-rose-500/5 dark:bg-rose-950/20',
          badge: 'bg-rose-500/20 text-rose-500 dark:text-rose-400 border-rose-500/30',
          bar: 'bg-rose-500',
          icon: <Flame className="h-4 w-4 text-rose-500" />,
          label: 'Critical Burn Rate',
        };
      case 'caution':
        return {
          border: 'border-amber-500/30 dark:border-amber-500/20',
          bg: 'bg-amber-500/5 dark:bg-amber-950/20',
          badge: 'bg-amber-500/20 text-amber-500 dark:text-amber-400 border-amber-500/30',
          bar: 'bg-amber-500',
          icon: <Clock className="h-4 w-4 text-amber-500" />,
          label: 'Caution Pacing',
        };
      default:
        return {
          border: 'border-emerald-500/30 dark:border-emerald-500/20',
          bg: 'bg-emerald-500/5 dark:bg-emerald-950/20',
          badge: 'bg-emerald-500/20 text-emerald-500 dark:text-emerald-400 border-emerald-500/30',
          bar: 'bg-emerald-500',
          icon: <ShieldCheck className="h-4 w-4 text-emerald-500" />,
          label: 'Safe Pacing',
        };
    }
  };

  const predictiveAlerts = data.predictive_budget_alerts || [];

  return (
    <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950/20 via-purple-950/10 to-slate-900/40 p-6 shadow-xl backdrop-blur-xl transition-all duration-300 hover:border-indigo-500/30 dark:border-indigo-500/20">
      {/* Decorative Glow Background */}
      <div className="absolute -top-24 -right-24 h-48 w-48 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none"></div>
      <div className="absolute -bottom-24 -left-24 h-48 w-48 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none"></div>

      {/* Header Banner */}
      <div className="relative z-10 flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-200/10 dark:border-gray-800/60">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/25">
            <Sparkles className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 dark:text-white text-lg tracking-tight">
                Smart Spending Insights & Forecast
              </h3>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                AI Powered ({data.provider_used})
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              Personalized tips, category surge analysis, and predictive overspending forecasts
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Health Score Pill */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-sm font-semibold ${getScoreColor(data.financial_health_score)}`}>
            <span>Health Score:</span>
            <span className="font-mono text-base">{data.financial_health_score}/100</span>
            <span className="text-xs opacity-75 font-normal">({data.health_status})</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700/80 text-gray-700 dark:text-gray-300 text-xs font-medium transition-all shadow-sm disabled:opacity-50"
            title="Refresh AI Insights"
          >
            <RotateCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>{refreshing ? 'Analyzing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {/* Headline Overview */}
      <div className="relative z-10 mt-4 px-4 py-3 rounded-xl bg-indigo-500/5 dark:bg-indigo-950/30 border border-indigo-500/10 flex items-start gap-3">
        <Lightbulb className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />
        <p className="text-sm font-medium text-gray-800 dark:text-gray-200 leading-relaxed">
          {data.headline}
        </p>
      </div>

      {/* Predictive Budget Overspending Alerts (Step 2 Feature) */}
      {predictiveAlerts.length > 0 && (
        <div className="relative z-10 mt-5 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            <Flame className="h-4 w-4 text-rose-500" />
            <span>Predictive Budget Overspending Alerts & Pacing</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {predictiveAlerts.map((alert, idx) => {
              const style = getPacingStyle(alert.pacing_status);
              const progressPct = Math.min(100, Math.round((alert.current_spend / alert.budget_limit) * 100));

              return (
                <div
                  key={idx}
                  className={`rounded-xl border p-4 transition-all ${style.border} ${style.bg}`}
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      {style.icon}
                      <span className="font-semibold text-sm text-gray-900 dark:text-gray-100">
                        {alert.category} Budget
                      </span>
                    </div>
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold border ${style.badge}`}>
                      {alert.projected_exhaustion_date && alert.projected_exhaustion_date !== 'Exceeded'
                        ? `Exhausts by ${alert.projected_exhaustion_date}`
                        : style.label}
                    </span>
                  </div>

                  {/* Pacing Progress Bar */}
                  <div className="space-y-1 mb-3">
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>Spent: ₹{alert.current_spend.toLocaleString()}</span>
                      <span>Limit: ₹{alert.budget_limit.toLocaleString()}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${style.bar}`}
                        style={{ width: `${progressPct}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 pt-0.5">
                      <span>{progressPct}% consumed</span>
                      <span>Projected: ₹{alert.projected_total.toLocaleString()}</span>
                    </div>
                  </div>

                  {/* Proactive Pacing Metrics */}
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div className="rounded-lg bg-gray-100/80 dark:bg-gray-800/60 p-2 text-center border border-gray-200/40 dark:border-gray-700/40">
                      <span className="block text-2xs uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Current Burn Rate
                      </span>
                      <span className="font-mono text-xs font-bold text-gray-900 dark:text-gray-100">
                        ₹{alert.daily_burn_rate.toLocaleString()}/day
                      </span>
                    </div>

                    <div className="rounded-lg bg-gray-100/80 dark:bg-gray-800/60 p-2 text-center border border-gray-200/40 dark:border-gray-700/40">
                      <span className="block text-2xs uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Safe Daily Limit
                      </span>
                      <span className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        ₹{alert.safe_daily_ceiling.toLocaleString()}/day
                      </span>
                    </div>
                  </div>

                  {/* AI Advice Message */}
                  <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed font-normal">
                    {alert.alert_message}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Grid: Detected Spikes & Actionable Saving Tips */}
      <div className="relative z-10 mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Section 1: Detected Category Surges */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            <TrendingUp className="h-4 w-4 text-amber-500" />
            <span>Category Spending Surges</span>
          </div>

          {data.spending_spikes.length > 0 ? (
            <div className="space-y-2.5">
              {data.spending_spikes.map((spike, idx) => (
                <div
                  key={idx}
                  className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3.5 transition-all hover:border-amber-500/40"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-semibold text-gray-900 dark:text-gray-100">
                      {spike.category}
                    </span>
                    {spike.surge_percentage && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-500">
                        +{spike.surge_percentage}% surge
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                    {spike.insight}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-200 dark:border-gray-800 p-4 text-center">
              <CheckCircle2 className="h-6 w-6 text-emerald-500 mx-auto mb-1.5" />
              <p className="text-xs text-gray-600 dark:text-gray-400">
                No unusual category surges detected in the last 7 days. Your spending is steady!
              </p>
            </div>
          )}
        </div>

        {/* Section 2: Actionable Saving Opportunities */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            <PiggyBank className="h-4 w-4 text-emerald-500" />
            <span>Actionable Saving Tips</span>
          </div>

          <div className="space-y-2.5">
            {data.saving_tips.map((tip, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3.5 transition-all hover:border-emerald-500/40"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-semibold text-gray-900 dark:text-gray-100">
                    {tip.title}
                  </span>
                  {tip.estimated_monthly_savings && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-500">
                      Save ~₹{tip.estimated_monthly_savings.toLocaleString()}/mo
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                  {tip.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Positive Habits Banner */}
      {data.positive_habits && data.positive_habits.length > 0 && (
        <div className="relative z-10 mt-4 pt-3 border-t border-gray-200/10 dark:border-gray-800/60 flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{data.positive_habits[0]}</span>
        </div>
      )}
    </div>
  );
}
