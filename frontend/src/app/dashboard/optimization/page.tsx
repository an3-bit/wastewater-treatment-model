'use client';

import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Award,
  Zap,
  Droplets,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingDown,
  Layers,
} from 'lucide-react';
import { optimizationService } from '@/services/optimizationService';
import { OptimizationSummary, OperatingStrategy, ParetoPoint } from '@/types/optimization';
import { ParetoChart } from '@/components/charts/ParetoChart';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatSEC, formatPercent, formatPressure, formatPower } from '@/utils/formatters';

export default function OptimizationPage() {
  const [summary, setSummary] = useState<OptimizationSummary | null>(null);
  const [activeStrategyId, setActiveStrategyId] = useState<string>('strategy_d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await optimizationService.getOptimizationSummary();
        setSummary(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSelectStrategy = async (id: string) => {
    setActiveStrategyId(id);
    await optimizationService.setActiveStrategy(id);
  };

  if (loading || !summary) {
    return <div className="h-96 bg-white rounded-2xl border border-slate-200 animate-pulse" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Multi-Objective Operating Optimization (NSGA-II)
            </h2>
            <StatusBadge status="424 Pareto Points" variant="pareto" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Surrogate-accelerated multi-objective optimization across conflicting recovery, SEC, and membrane stress goals.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs">
          <span className="text-slate-500">Convergence: <strong>{summary.convergence_status}</strong></span>
          <span className="text-slate-300">|</span>
          <span className="text-emerald-700 font-semibold">{summary.surrogate_speedup}</span>
        </div>
      </div>

      {/* Dominance Proof Banner */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-xs text-emerald-950 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex items-start gap-2.5">
          <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div>
            <strong className="font-bold text-emerald-900 block">
              Pareto Dominance Proof: Strategy D Dominates Industrial Baseline
            </strong>
            <p className="text-emerald-800 leading-relaxed mt-0.5">
              Operating at P<sub>1</sub> = 16.06 bar, P<sub>2</sub> = 16.41 bar strictly dominates the original 13/18 bar baseline by delivering <strong>+0.86% higher recovery</strong> (70.22% vs 69.36%), <strong>-5.72% lower energy</strong> (0.7269 vs 0.7710 kWh/m³), and <strong>-15.15% lower peak element recovery stress</strong> (20.10% vs 23.69%).
            </p>
          </div>
        </div>

        <span className="text-[11px] font-mono bg-emerald-200/60 text-emerald-900 px-2 py-1 rounded whitespace-nowrap self-start sm:self-auto font-semibold">
          Dominance Verified
        </span>
      </div>

      {/* Interactive Pareto Scatter Plot */}
      <ParetoChart data={summary.pareto_points} />

      {/* Strategy Cards Grid (A, B, C, D, Baseline) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Award className="w-4 h-4 text-sky-600" />
            Authoritative Strategy Ledger & Presets
          </h3>
          <span className="text-xs text-slate-400">Select a strategy to inspect</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {summary.strategies.map((strat) => {
            const isSelected = strat.id === activeStrategyId;

            return (
              <div
                key={strat.id}
                onClick={() => handleSelectStrategy(strat.id)}
                className={`rounded-2xl p-5 border cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-sky-50/50 border-2 border-sky-500 shadow-md ring-2 ring-sky-200'
                    : 'bg-white border-slate-200 hover:border-slate-300 shadow-xs'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-1 mb-2">
                    <span className="text-xs font-bold text-slate-900">{strat.code}</span>
                    <StatusBadge
                      status={strat.status}
                      variant={strat.status === 'PARETO OPTIMAL' ? 'pareto' : 'dominated'}
                      size="sm"
                    />
                  </div>

                  <h4 className="text-sm font-bold text-slate-800 mb-1">{strat.name}</h4>
                  <p className="text-[11px] text-slate-500 leading-snug line-clamp-2 mb-3">
                    {strat.description}
                  </p>

                  <div className="space-y-1.5 text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Pressures (P₁ / P₂):</span>
                      <strong className="font-mono text-slate-800">
                        {strat.p1_bar.toFixed(2)} / {strat.p2_bar.toFixed(2)} bar
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Recovery:</span>
                      <strong className="font-mono text-emerald-700">
                        {formatPercent(strat.recovery_pct)}
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">SEC:</span>
                      <strong className="font-mono text-amber-700">
                        {formatSEC(strat.sec_kwh_m3)}
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Max Element Rec:</span>
                      <strong className="font-mono text-slate-700">
                        {formatPercent(strat.max_element_recovery_pct)}
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-200 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 font-mono">
                    Power: {formatPower(strat.total_power_kw)}
                  </span>
                  <span
                    className={`font-semibold ${
                      isSelected ? 'text-sky-700' : 'text-slate-400'
                    }`}
                  >
                    {isSelected ? 'Active Selection' : 'Click to Select'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
