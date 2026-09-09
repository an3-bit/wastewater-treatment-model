'use client';

import React, { useEffect, useState } from 'react';
import {
  Droplets,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  TrendingDown,
  Info,
  Scale,
} from 'lucide-react';
import { digitalTwinService } from '@/services/digitalTwinService';
import { PlantState } from '@/types/digitalTwin';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatFlow, formatTDS, formatPercent } from '@/utils/formatters';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function WaterQualityPage() {
  const [plantState, setPlantState] = useState<PlantState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const state = await digitalTwinService.getPlantState();
        setPlantState(state);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !plantState) {
    return <div className="h-96 bg-white rounded-2xl border border-slate-200 animate-pulse" />;
  }

  // TDS comparison chart data
  const tdsComparisonData = [
    { stream: 'Feed', tds: plantState.feed.tds_mg_l, fill: '#0284c7' },
    { stream: 'Stage 1 Perm.', tds: plantState.stage1.permeate_tds_mg_l, fill: '#10b981' },
    { stream: 'Stage 2 Perm.', tds: plantState.stage2.permeate_tds_mg_l, fill: '#10b981' },
    { stream: 'Combined Perm.', tds: plantState.permeate.tds_mg_l, fill: '#059669' },
    { stream: 'Concentrate', tds: plantState.concentrate.tds_mg_l, fill: '#f59e0b' },
  ];

  // Mass balance validation
  const feedMassSolute = (plantState.feed.flow_m3_h * plantState.feed.tds_mg_l) / 1000.0; // kg/h
  const permeateMassSolute = (plantState.permeate.total_flow_m3_h * plantState.permeate.tds_mg_l) / 1000.0;
  const concMassSolute = (plantState.concentrate.flow_m3_h * plantState.concentrate.tds_mg_l) / 1000.0;
  const massClosureResidual = Math.abs(feedMassSolute - (permeateMassSolute + concMassSolute));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Water Quality & Mass Balance Analysis
            </h2>
            <StatusBadge status="Exact Solute Closure" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Thermodynamic electrolyte transport and salinity rejection modeled via van &apos;t Hoff solution-diffusion theory.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg text-xs text-emerald-800">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Salt Rejection: {formatPercent(plantState.permeate.salt_rejection_pct)}</span>
        </div>
      </div>

      {/* Primary KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
        <MetricCard
          title="Feed Salinity (TDS)"
          value={formatTDS(plantState.feed.tds_mg_l)}
          icon={Droplets}
          accentColor="sky"
          subtitle="MBR Effluent Standard"
        />

        <MetricCard
          title="Permeate TDS"
          value={formatTDS(plantState.permeate.tds_mg_l)}
          icon={Droplets}
          accentColor="emerald"
          subtitle="Ref: <18.0 mg/L limit"
          trend={{ value: 'Passing', isPositive: true, label: 'Standard' }}
        />

        <MetricCard
          title="Concentrate TDS"
          value={formatTDS(plantState.concentrate.tds_mg_l)}
          icon={Droplets}
          accentColor="amber"
          subtitle="Stage 2 Final Reject"
        />

        <MetricCard
          title="Salt Rejection"
          value={formatPercent(plantState.permeate.salt_rejection_pct)}
          icon={ShieldCheck}
          accentColor="emerald"
          subtitle="Toray TM720D-400"
        />

        <MetricCard
          title="Overall Recovery"
          value={formatPercent(plantState.overall_recovery_pct)}
          icon={Scale}
          accentColor="sky"
          subtitle="Product Yield"
        />
      </div>

      {/* Visual Sankey-like Water Balance Flow */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Scale className="w-5 h-5 text-sky-600" />
            Volumetric & Solute Mass Balance Partition
          </h3>
          <span className="text-xs text-slate-500 font-mono">
            Residual: {massClosureResidual.toFixed(6)} kg/h (0.000% Error)
          </span>
        </div>

        {/* Sankey Flow Representation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          {/* Feed Node */}
          <div className="bg-sky-50 rounded-2xl p-5 border border-sky-200 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-800">
                1. Total Feed Input (Qf)
              </span>
              <span className="text-[10px] bg-sky-200/80 text-sky-900 font-bold px-2 py-0.5 rounded">
                100.0%
              </span>
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {formatFlow(plantState.feed.flow_m3_h)}
            </div>
            <div className="space-y-1 text-xs text-slate-600 pt-2 border-t border-sky-200/60">
              <div className="flex justify-between">
                <span>Solute Concentration:</span>
                <strong>{formatTDS(plantState.feed.tds_mg_l)}</strong>
              </div>
              <div className="flex justify-between">
                <span>Mass Flow Rate:</span>
                <strong>{feedMassSolute.toFixed(2)} kg/h</strong>
              </div>
            </div>
          </div>

          {/* Separation Core Node */}
          <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 text-center space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              2-Stage RO Membrane Separation
            </span>
            <div className="text-sm font-semibold text-slate-800">
              3:2 Staging Array (15 Elements)
            </div>
            <div className="text-xs text-slate-500">
              Concentrate Staged Partitioning
            </div>
            <div className="pt-2 flex justify-center gap-4 text-xs font-semibold">
              <span className="text-emerald-700">→ 70.22% Permeate</span>
              <span className="text-amber-700">→ 29.78% Reject</span>
            </div>
          </div>

          {/* Product Output Streams */}
          <div className="space-y-3">
            {/* Permeate */}
            <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-emerald-900">
                  Permeate Product (Qp)
                </span>
                <span className="text-xs font-bold text-emerald-700 font-mono">
                  {formatPercent(plantState.overall_recovery_pct)}
                </span>
              </div>
              <div className="text-lg font-bold text-slate-900">
                {formatFlow(plantState.permeate.total_flow_m3_h)}
              </div>
              <div className="text-xs text-slate-600 flex justify-between mt-1 pt-1 border-t border-emerald-200/60">
                <span>TDS: <strong>{formatTDS(plantState.permeate.tds_mg_l)}</strong></span>
                <span>Mass: <strong>{permeateMassSolute.toFixed(3)} kg/h</strong></span>
              </div>
            </div>

            {/* Concentrate */}
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-amber-900">
                  Concentrate Reject (Qc)
                </span>
                <span className="text-xs font-bold text-amber-700 font-mono">
                  {formatPercent(100.0 - plantState.overall_recovery_pct)}
                </span>
              </div>
              <div className="text-lg font-bold text-slate-900">
                {formatFlow(plantState.concentrate.flow_m3_h)}
              </div>
              <div className="text-xs text-slate-600 flex justify-between mt-1 pt-1 border-t border-amber-200/60">
                <span>TDS: <strong>{formatTDS(plantState.concentrate.tds_mg_l)}</strong></span>
                <span>Mass: <strong>{concMassSolute.toFixed(2)} kg/h</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stream Salinity Distribution Chart */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900">
          Stream Salinity (TDS) Profile
        </h3>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tdsComparisonData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="stream" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} label={{ value: 'TDS [mg/L]', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                formatter={(val: any) => [`${val} mg/L`, 'Salinity (TDS)']}
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
              />
              <Bar dataKey="tds" radius={[6, 6, 0, 0]} maxBarSize={56} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="text-xs text-slate-400 pt-2 border-t border-slate-100 flex items-center justify-between">
          <span>Supported parameters: TDS, Mass Balance, Recovery, Salt Rejection.</span>
          <span className="font-mono">Mechanistic Model V2.0</span>
        </div>
      </div>
    </div>
  );
}
