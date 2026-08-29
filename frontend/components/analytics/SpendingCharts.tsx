'use client';

import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Sector,
} from 'recharts';
import { DailySpendingItem, CategorySpending } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { AreaChart as AreaIcon, BarChart3, PieChart as PieIcon, Tag, Calendar, TrendingUp, Sparkles } from 'lucide-react';

interface SpendingChartsProps {
  dailyData?: DailySpendingItem[];
  categoryData?: CategorySpending[];
  loading: boolean;
}

const CATEGORY_COLORS: Record<string, string> = {
  Food: '#6366f1',
  Transport: '#a855f7',
  Rent: '#ec4899',
  Shopping: '#3b82f6',
  Bills: '#10b981',
  Entertainment: '#f59e0b',
  Health: '#ef4444',
  Education: '#14b8a6',
  Other: '#64748b',
};

const FALLBACK_COLORS = ['#6366f1', '#a855f7', '#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#14b8a6', '#64748b'];

interface ActiveSectorProps {
  cx: number;
  cy: number;
  innerRadius: number;
  outerRadius: number;
  startAngle: number;
  endAngle: number;
  fill: string;
  payload: { category_name: string };
  percent: number;
  value: number;
}

// Active shape renderer for category distribution pie
const renderActivePieSector = (props: ActiveSectorProps) => {
  const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent, value } = props;

  return (
    <g className="animate-scale-in">
      <text x={cx} y={cy - 10} dy={6} textAnchor="middle" fill="#fff" className="text-xs sm:text-sm font-extrabold tracking-tight">
        {payload.category_name}
      </text>
      <text x={cx} y={cy + 12} dy={6} textAnchor="middle" fill="#818cf8" className="text-[10px] sm:text-xs font-mono font-bold">
        ₹{Number(value).toLocaleString('en-IN')} ({(percent * 100).toFixed(1)}%)
      </text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 8}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
        style={{
          filter: 'drop-shadow(0px 0px 10px rgba(99, 102, 241, 0.7))',
          transition: 'all 0.3s ease-out',
        }}
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 10}
        outerRadius={outerRadius + 14}
        fill={fill}
      />
    </g>
  );
};

export const SpendingCharts: React.FC<SpendingChartsProps> = ({
  dailyData = [],
  categoryData = [],
  loading,
}) => {
  const [dailyChartType, setDailyChartType] = useState<'area' | 'bar'>('area');
  const [activePieIndex, setActivePieIndex] = useState<number>(0);

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
        <div className="h-80 sm:h-96 rounded-2xl glass-card animate-pulse bg-slate-800/30" />
        <div className="h-80 sm:h-96 rounded-2xl glass-card animate-pulse bg-slate-800/30" />
      </div>
    );
  }

  const safeDaily = Array.isArray(dailyData) ? dailyData : [];
  const safeCategory = Array.isArray(categoryData) ? categoryData : [];

  const formattedDaily = safeDaily.map((d) => ({
    ...d,
    amountNum: typeof d.amount === 'string' ? parseFloat(d.amount) : Number(d.amount),
    dayNum: String(new Date(d.date).getDate()),
  }));

  const formattedCategory = safeCategory.map((c, i) => ({
    ...c,
    amountNum: typeof c.amount === 'string' ? parseFloat(c.amount) : Number(c.amount),
    color: CATEGORY_COLORS[c.category_name] || FALLBACK_COLORS[i % FALLBACK_COLORS.length],
  }));

  const totalCategorySpend = formattedCategory.reduce((acc, c) => acc + c.amountNum, 0);
  const maxDaySpend = formattedDaily.length > 0 ? Math.max(...formattedDaily.map((d) => d.amountNum)) : 0;
  const activeDaysCount = formattedDaily.filter((d) => d.amountNum > 0).length;

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Top Quick Metric Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
        <div className="glass-panel p-4 sm:p-5 rounded-2xl border border-slate-800/80 flex items-center justify-between hover:border-indigo-500/40 transition-all duration-300 group">
          <div>
            <p className="text-[11px] sm:text-xs font-extrabold uppercase tracking-wider text-slate-400">Peak Single Day Spend</p>
            <h4 className="text-lg sm:text-xl font-extrabold text-white mt-1 group-hover:text-indigo-300 transition-colors">
              ₹{maxDaySpend.toLocaleString('en-IN')}
            </h4>
            <p className="text-[11px] text-indigo-400 font-mono mt-0.5 flex items-center gap-1 font-semibold">
              <Sparkles className="w-3 h-3" />
              <span>Highest trajectory peak</span>
            </p>
          </div>
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-gradient-to-tr from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform shadow-lg shadow-indigo-600/20 shrink-0">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel p-4 sm:p-5 rounded-2xl border border-slate-800/80 flex items-center justify-between hover:border-purple-500/40 transition-all duration-300 group">
          <div>
            <p className="text-[11px] sm:text-xs font-extrabold uppercase tracking-wider text-slate-400">Active Days Rate</p>
            <h4 className="text-lg sm:text-xl font-extrabold text-white mt-1 group-hover:text-purple-300 transition-colors">
              {activeDaysCount} / {formattedDaily.length} Days
            </h4>
            <p className="text-[11px] text-purple-400 font-mono mt-0.5 font-semibold">
              {((activeDaysCount / (formattedDaily.length || 1)) * 100).toFixed(0)}% month active rate
            </p>
          </div>
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-gradient-to-tr from-purple-600/20 to-pink-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform shadow-lg shadow-purple-600/20 shrink-0">
            <Calendar className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel p-4 sm:p-5 rounded-2xl border border-slate-800/80 flex items-center justify-between hover:border-emerald-500/40 transition-all duration-300 group">
          <div>
            <p className="text-[11px] sm:text-xs font-extrabold uppercase tracking-wider text-slate-400">Active Categories</p>
            <h4 className="text-lg sm:text-xl font-extrabold text-white mt-1 group-hover:text-emerald-300 transition-colors">
              {formattedCategory.length} Categories
            </h4>
            <p className="text-[11px] text-emerald-400 font-mono mt-0.5 font-semibold truncate max-w-[140px]">
              Top: {formattedCategory[0]?.category_name || 'None'}
            </p>
          </div>
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-gradient-to-tr from-emerald-600/20 to-teal-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform shadow-lg shadow-emerald-600/20 shrink-0">
            <Tag className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
        {/* Daily Spending Trajectory Chart */}
        <Card className="flex flex-col border-slate-800/80 shadow-2xl overflow-hidden group">
          <CardHeader className="pb-3 border-b border-slate-800/60 flex flex-row items-center justify-between p-4 sm:p-6">
            <CardTitle className="text-sm sm:text-base font-bold flex items-center gap-2">
              <AreaIcon className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-indigo-400" />
              <span>Daily Spending Trajectory</span>
            </CardTitle>
            <div className="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setDailyChartType('area')}
                className={`p-1.5 rounded-lg text-xs font-semibold transition-all ${
                  dailyChartType === 'area'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="Area Curve View"
              >
                <AreaIcon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </button>
              <button
                onClick={() => setDailyChartType('bar')}
                className={`p-1.5 rounded-lg text-xs font-semibold transition-all ${
                  dailyChartType === 'bar'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="Bar Chart View"
              >
                <BarChart3 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </button>
            </div>
          </CardHeader>
          <CardContent className="h-72 sm:h-80 lg:h-96 w-full p-2 sm:p-6 pt-4 sm:pt-6">
            {formattedDaily.length === 0 ? (
              <div className="flex items-center justify-center h-full text-slate-500 text-sm">
                No daily data recorded for selected period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                {dailyChartType === 'area' ? (
                  <AreaChart data={formattedDaily} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorSpendGlow" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.6} />
                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                    <XAxis dataKey="dayNum" stroke="#94a3b8" fontSize={10} tickLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        borderColor: '#475569',
                        borderRadius: '12px',
                        color: '#fff',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
                        fontSize: '12px',
                      }}
                      formatter={(value: number) => [`₹${value.toLocaleString('en-IN')}`, 'Spent']}
                      labelFormatter={(label) => `Day ${label}`}
                    />
                    <Area
                      type="monotone"
                      dataKey="amountNum"
                      stroke="#818cf8"
                      strokeWidth={3}
                      fillOpacity={1}
                      fill="url(#colorSpendGlow)"
                      isAnimationActive={true}
                      animationDuration={1400}
                      animationEasing="ease-out"
                      activeDot={{ r: 6, stroke: '#818cf8', strokeWidth: 2, fill: '#0b0f19' }}
                    />
                  </AreaChart>
                ) : (
                  <BarChart data={formattedDaily} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                    <XAxis dataKey="dayNum" stroke="#94a3b8" fontSize={10} tickLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        borderColor: '#475569',
                        borderRadius: '12px',
                        color: '#fff',
                        fontSize: '12px',
                      }}
                      formatter={(value: number) => [`₹${value.toLocaleString('en-IN')}`, 'Spent']}
                      labelFormatter={(label) => `Day ${label}`}
                    />
                    <Bar
                      dataKey="amountNum"
                      fill="#6366f1"
                      radius={[4, 4, 0, 0]}
                      isAnimationActive={true}
                      animationDuration={1200}
                      animationEasing="ease-in-out"
                    />
                  </BarChart>
                )}
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Category Breakdown Pie Chart Card */}
        <Card className="flex flex-col border-slate-800/80 shadow-2xl overflow-hidden">
          <CardHeader className="pb-3 border-b border-slate-800/60 flex flex-row items-center justify-between p-4 sm:p-6">
            <CardTitle className="text-sm sm:text-base font-bold flex items-center gap-2">
              <PieIcon className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-purple-400" />
              <span>Category Share</span>
            </CardTitle>
            <span className="text-[11px] sm:text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 font-mono font-semibold">
              ₹{totalCategorySpend.toLocaleString('en-IN')} Total
            </span>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-4 sm:p-6 pt-3 sm:pt-4">
            {formattedCategory.length === 0 ? (
              <div className="flex items-center justify-center h-64 sm:h-80 text-slate-500 text-sm">
                No category transactions recorded for selected month
              </div>
            ) : (
              <div className="flex flex-col h-full">
                {/* Recharts Animated Pie */}
                <div className="h-56 sm:h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        activeIndex={activePieIndex}
                        activeShape={renderActivePieSector}
                        data={formattedCategory}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={75}
                        dataKey="amountNum"
                        nameKey="category_name"
                        isAnimationActive={true}
                        animationDuration={1500}
                        animationBegin={200}
                        animationEasing="ease-out"
                        onMouseEnter={(_, index) => setActivePieIndex(index)}
                      >
                        {formattedCategory.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} stroke="#0b0f19" strokeWidth={2} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Custom Category Badges Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-2.5 mt-3 pt-3 border-t border-slate-800/60 max-h-40 overflow-y-auto">
                  {formattedCategory.map((cat, idx) => (
                    <div
                      key={cat.category_id}
                      onClick={() => setActivePieIndex(idx)}
                      onMouseEnter={() => setActivePieIndex(idx)}
                      className={`flex items-center justify-between p-2 sm:p-2.5 rounded-xl border transition-all duration-200 cursor-pointer ${
                        activePieIndex === idx
                          ? 'bg-slate-800/90 border-indigo-500/60 shadow-lg shadow-indigo-600/20 translate-x-1'
                          : 'bg-slate-900/40 border-slate-800/60 hover:bg-slate-800/50 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center space-x-2 min-w-0 truncate">
                        <span
                          className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full shrink-0 shadow-sm transition-transform"
                          style={{ backgroundColor: cat.color }}
                        />
                        <span className="text-xs font-bold text-white truncate">{cat.category_name}</span>
                      </div>
                      <div className="text-right shrink-0 font-mono text-[10px] sm:text-[11px] ml-2">
                        <span className="font-bold text-slate-200">
                          ₹{cat.amountNum.toLocaleString('en-IN')}
                        </span>
                        <span className="text-slate-400 ml-1 font-semibold">({cat.percentage.toFixed(0)}%)</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
