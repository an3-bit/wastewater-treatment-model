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
  Coins,
  BarChart3,
} from 'lucide-react';
import { optimizationService } from '@/services/optimizationService';
import { economicsApi } from '@/services/api/economics';
import { policiesApi } from '@/services/api/policies';
import { OptimizationSummary, OperatingStrategy } from '@/types/optimization';
import { ValueDecompositionResponse, PolicyComparisonResponse } from '@/types/api';
import { ParetoChart } from '@/components/charts/ParetoChart';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatSEC, formatPercent, formatPressure, formatPower } from '@/utils/formatters';

export default function OptimizationPage() {
  const [summary, setSummary] = useState<OptimizationSummary | null>(null);
  const [activeStrategyId, setActiveStrategyId] = useState<string>('strategy_d');
  const [valueDecomp, setValueDecomp] = useState<ValueDecompositionResponse | null>(null);
  const [policies, setPolicies] = useState<PolicyComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [optData, decompData, policyData] = await Promise.all([
          optimizationService.getOptimizationSummary(),
          economicsApi.getValueDecomposition().catch(() => null),
          policiesApi.getPolicies().catch(() => null),
        ]);
        setSummary(optData);
        setValueDecomp(decompData);
        setPolicies(policyData);
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
              Supervisory Optimization & Value Decomposition
            </h2>
            <StatusBadge status="Stage 8C Authoritative" variant="pareto" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Mathematical value attribution and multi-objective NSGA-II Pareto optimization for textile wastewater reuse.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs">
          <span className="text-slate-500">Framework: <strong>Stage 8C Frozen</strong></span>
          <span className="text-slate-300">|</span>
          <span className="text-emerald-700 font-semibold">Virtual Plant Validated</span>
        </div>
      </div>

      {/* Stage 8C Value Waterfall Section */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Coins className="w-5 h-5 text-emerald-600" />
              Stage 8C Mathematical Value Waterfall (KES / year)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Strict mathematical decomposition of the <strong>KES 4,391,948.14 / yr</strong> integrated digital twin value.
            </p>
          </div>
          <span className="text-xs font-mono bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-1 rounded-md">
            Total Integrated Value: KES 4.39M / yr
          </span>
        </div>

        {/* Value Waterfall Bar Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              1. Static Optimization (B - A)
            </span>
            <div className="text-xl font-bold text-slate-800">
              KES {valueDecomp ? valueDecomp.items.find(i => i.code === 'STATIC')?.value_kes_year.toLocaleString('en-US') : '62,203'}
            </div>
            <span className="text-[11px] text-slate-500 block">
              Share: <strong>1.42%</strong> (Fixed Setpoint Tuning)
            </span>
          </div>

          <div className="bg-emerald-50/70 p-4 rounded-xl border border-emerald-200 space-y-1">
            <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider block">
              2. Condition-Based CIP (C - B)
            </span>
            <div className="text-xl font-bold text-emerald-950">
              KES {valueDecomp ? (valueDecomp.items.find(i => i.code === 'CONDITION')?.value_kes_year || 3902797.57).toLocaleString('en-US') : '3,902,797'}
            </div>
            <span className="text-[11px] text-emerald-700 block">
              Share: <strong>88.86%</strong> (Fouling-Triggered Cleaning)
            </span>
          </div>

          <div className="bg-sky-50/70 p-4 rounded-xl border border-sky-200 space-y-1">
            <span className="text-[11px] font-bold text-sky-800 uppercase tracking-wider block">
              3. Pure Prediction (D - C)
            </span>
            <div className="text-xl font-bold text-sky-950">
              KES {valueDecomp ? (valueDecomp.items.find(i => i.code === 'PREDICTION')?.value_kes_year || 424164.72).toLocaleString('en-US') : '424,165'}
            </div>
            <span className="text-[11px] text-sky-700 block">
              Share: <strong>9.66%</strong> (Look-Ahead CIP Timing)
            </span>
          </div>

          <div className="bg-amber-50/70 p-4 rounded-xl border border-amber-200 space-y-1">
            <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider block">
              4. Pressure MPC (E - D)
            </span>
            <div className="text-xl font-bold text-amber-950">
              KES {valueDecomp ? (valueDecomp.items.find(i => i.code === 'MPC')?.value_kes_year || 2782.42).toLocaleString('en-US') : '2,782'}
            </div>
            <span className="text-[11px] text-amber-700 block">
              Share: <strong>0.06%</strong> (Marginal Continuous Trim)
            </span>
          </div>
        </div>

        {/* Caveat & Commercial Focus Note */}
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600 flex items-center justify-between">
          <span>
            💡 <strong>Commercial Finding:</strong> 98.5% of value is created by Membrane Health, Fouling Prediction, and Predictive CIP. Dynamic Pressure MPC contributes 0.06% marginal value.
          </span>
          <span className="text-[11px] font-mono text-slate-400 shrink-0">Stage 8C Audit Result</span>
        </div>
      </div>

      {/* Interactive Pareto Scatter Plot */}
      <ParetoChart data={summary.pareto_points} />

      {/* Policy Comparison Table */}
      {policies && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-indigo-600" />
              Stage 8C Supervisory Policy Comparison Matrix
            </h3>
            <span className="text-xs text-slate-400">Cases A through F (Oracle)</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <tr>
                  <th className="p-3">Policy Code</th>
                  <th className="p-3">Description</th>
                  <th className="p-3 text-right">Permeate (m³/yr)</th>
                  <th className="p-3 text-right">Recovery (%)</th>
                  <th className="p-3 text-right">Total Energy (kWh)</th>
                  <th className="p-3 text-right">SEC (kWh/m³)</th>
                  <th className="p-3 text-right">CIP Count</th>
                  <th className="p-3 text-right">Net Value vs Base</th>
                  <th className="p-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {policies.policies.map((p) => (
                  <tr key={p.policy_code} className="hover:bg-slate-50/60">
                    <td className="p-3 font-mono font-bold text-slate-900">{p.policy_code}</td>
                    <td className="p-3 text-slate-700">{p.policy_name}</td>
                    <td className="p-3 text-right font-mono">{p.permeate_m3.toLocaleString()}</td>
                    <td className="p-3 text-right font-mono">{p.effective_recovery_pct.toFixed(2)}%</td>
                    <td className="p-3 text-right font-mono">{p.total_energy_kwh.toLocaleString()}</td>
                    <td className="p-3 text-right font-mono font-bold text-amber-700">{p.sec_kwh_m3.toFixed(4)}</td>
                    <td className="p-3 text-right font-mono">{p.cip_count}</td>
                    <td className="p-3 text-right font-mono font-bold text-emerald-700">
                      {p.incremental_value_vs_baseline_kes > 0 ? `+KES ${p.incremental_value_vs_baseline_kes.toLocaleString()}` : 'Baseline'}
                    </td>
                    <td className="p-3 text-center">
                      {p.oracle ? (
                        <span className="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded">
                          ORACLE UPPER BOUND
                        </span>
                      ) : (
                        <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded">
                          DEPLOYABLE
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Strategy Cards Grid */}
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
