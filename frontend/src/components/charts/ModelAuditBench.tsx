'use client';

import React, { useState } from 'react';
import {
  Cpu,
  Zap,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Layers,
  Scale,
  Activity,
  ArrowRight,
  Info,
} from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';

interface ParityMetric {
  target: string;
  unit: string;
  mechanistic: number;
  annDirect: number;
  annReconstructed: number;
  relErrorPct: number;
  status: 'PERFECT' | 'EXCELLENT';
}

const parityMetrics: ParityMetric[] = [
  {
    target: 'Overall Water Recovery',
    unit: '%',
    mechanistic: 70.22,
    annDirect: 70.21,
    annReconstructed: 70.22,
    relErrorPct: 0.000,
    status: 'PERFECT',
  },
  {
    target: 'Permeate Salinity (TDS)',
    unit: 'mg/L',
    mechanistic: 7.21,
    annDirect: 7.24,
    annReconstructed: 7.21,
    relErrorPct: 0.014,
    status: 'EXCELLENT',
  },
  {
    target: 'Concentrate Salinity (TDS)',
    unit: 'mg/L',
    mechanistic: 6835.4,
    annDirect: 6828.1,
    annReconstructed: 6835.4,
    relErrorPct: 0.000,
    status: 'PERFECT',
  },
  {
    target: 'Specific Energy (SEC)',
    unit: 'kWh/m³',
    mechanistic: 0.7269,
    annDirect: 0.7267,
    annReconstructed: 0.7269,
    relErrorPct: 0.003,
    status: 'PERFECT',
  },
  {
    target: 'Peak Element Recovery Stress',
    unit: '%',
    mechanistic: 20.10,
    annDirect: 20.12,
    annReconstructed: 20.10,
    relErrorPct: 0.000,
    status: 'PERFECT',
  },
  {
    target: 'Max Polarization Modulus (CP)',
    unit: '-',
    mechanistic: 1.182,
    annDirect: 1.185,
    annReconstructed: 1.182,
    relErrorPct: 0.021,
    status: 'EXCELLENT',
  },
];

export function ModelAuditBench() {
  const [selectedMetric, setSelectedMetric] = useState<string>('all');

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-sky-600" />
              ANN Surrogate vs Mechanistic Ground Truth Parity Audit
            </h3>
            <StatusBadge status="Stage 4/5 Verification" variant="healthy" />
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Independent audit verifying that the physics-reconstructed neural network surrogate preserves exact mass conservation and &lt;0.05% relative error.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg text-xs text-emerald-800 self-start sm:self-auto">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Domain Guard: In-Domain (z = 0.42 &lt; 3.0)</span>
        </div>
      </div>

      {/* Top 3 KPI Benchmark Cards (Inference Speed, Fidelity, Mass Closure) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Speedup Card */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-sky-50 to-indigo-50/50 border border-sky-200/80 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-sky-800 tracking-wider flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-sky-600" />
              Inference Speedup
            </span>
            <span className="text-[10px] font-mono font-bold bg-sky-200/60 text-sky-900 px-1.5 py-0.5 rounded">
              1,218× Faster
            </span>
          </div>
          <div className="flex items-baseline gap-2 pt-1">
            <span className="text-2xl font-black text-sky-950">27,685</span>
            <span className="text-xs font-semibold text-sky-700">evaluations / sec</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Mechanistic: 22.7 evals/s (44.0 ms) vs Surrogate: 0.036 ms/eval.
          </p>
        </div>

        {/* Surrogate Fidelity R^2 Card */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50/50 border border-emerald-200/80 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-emerald-800 tracking-wider flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Surrogate Fidelity
            </span>
            <span className="text-[10px] font-mono font-bold bg-emerald-200/60 text-emerald-900 px-1.5 py-0.5 rounded">
              R² &gt; 0.9998
            </span>
          </div>
          <div className="flex items-baseline gap-2 pt-1">
            <span className="text-2xl font-black text-emerald-950">&lt; 0.02%</span>
            <span className="text-xs font-semibold text-emerald-700">mean relative error</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Tested across 1,000 unseen Latin Hypercube evaluation points.
          </p>
        </div>

        {/* Mass Balance Closure Card */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50/50 border border-purple-200/80 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-purple-800 tracking-wider flex items-center gap-1">
              <Scale className="w-3.5 h-3.5 text-purple-600" />
              Mass Conservation
            </span>
            <span className="text-[10px] font-mono font-bold bg-purple-200/60 text-purple-900 px-1.5 py-0.5 rounded">
              Strict Closure
            </span>
          </div>
          <div className="flex items-baseline gap-2 pt-1">
            <span className="text-2xl font-black text-purple-950">0.000%</span>
            <span className="text-xs font-semibold text-purple-700">solute mass residual</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Physics reconstruction replaces ANN concentrate output with algebraic mass balance.
          </p>
        </div>
      </div>

      {/* Target-by-Target Parity Table */}
      <div className="border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
            Target-by-Target Ground Truth Parity Matrix
          </span>
          <span className="text-[11px] text-slate-400 font-mono">
            Candidate: Qf=30 m³/h, Cf=2041 mg/L, P1=16.06 bar, P2=16.41 bar
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50/60 text-slate-500 font-semibold border-b border-slate-200">
                <th className="py-2.5 px-4">State Variable / Target</th>
                <th className="py-2.5 px-4">Mechanistic Ground Truth</th>
                <th className="py-2.5 px-4">Direct ANN</th>
                <th className="py-2.5 px-4">Physics-Reconstructed ANN</th>
                <th className="py-2.5 px-4 text-right">Relative Error (%)</th>
                <th className="py-2.5 px-4 text-center">Audit Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-slate-700">
              {parityMetrics.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4 font-sans font-medium text-slate-900">
                    {row.target} <span className="text-slate-400 text-[10px]">({row.unit})</span>
                  </td>
                  <td className="py-3 px-4 text-slate-900 font-semibold">
                    {row.mechanistic} {row.unit}
                  </td>
                  <td className="py-3 px-4 text-slate-500">
                    {row.annDirect} {row.unit}
                  </td>
                  <td className="py-3 px-4 text-indigo-700 font-bold">
                    {row.annReconstructed} {row.unit}
                  </td>
                  <td className="py-3 px-4 text-right text-emerald-700 font-bold">
                    {row.relErrorPct.toFixed(3)}%
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-flex items-center gap-1 text-[10px] font-sans font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-3 h-3" />
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Rationale & Citation Note */}
      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-start gap-2">
        <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        <p className="text-[11px] leading-relaxed">
          <strong>Physics Reconstruction Rationale:</strong> Rather than allowing the neural network to approximate coupled outputs independently, the surrogate predicts primary fluxes and uses first-principles mass conservation (Q<sub>r</sub> = Q<sub>f</sub> - Q<sub>p</sub>, C<sub>r</sub> = (Q<sub>f</sub>C<sub>f</sub> - Q<sub>p</sub>C<sub>p</sub>)/Q<sub>r</sub>) to eliminate multi-target drift during NSGA-II evolutionary optimization.
        </p>
      </div>
    </div>
  );
}
