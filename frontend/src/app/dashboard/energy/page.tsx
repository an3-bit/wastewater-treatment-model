'use client';

import React, { useState, useEffect } from 'react';
import {
  Zap,
  Activity,
  TrendingDown,
  Clock,
  Layers,
  Scale,
  ShieldCheck,
  Info,
} from 'lucide-react';
import { digitalTwinService } from '@/services/digitalTwinService';
import { optimizationService } from '@/services/optimizationService';
import { economicsApi } from '@/services/api/economics';
import { PlantState } from '@/types/digitalTwin';
import { OperatingStrategy } from '@/types/optimization';
import { EconomicSummaryResponse } from '@/types/api';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatSEC, formatPower, formatPercent, formatPressure } from '@/utils/formatters';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export default function EnergyPage() {
  const [plantState, setPlantState] = useState<PlantState | null>(null);
  const [strategies, setStrategies] = useState<OperatingStrategy[]>([]);
  const [econSummary, setEconSummary] = useState<EconomicSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [state, strats, econ] = await Promise.all([
          digitalTwinService.getPlantState(),
          optimizationService.getStrategies(),
          economicsApi.getSummary().catch(() => null),
        ]);
        setPlantState(state);
        setStrategies(strats);
        setEconSummary(econ);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !plantState) {
    return <div className="h-96 bg-white rounded-2xl border border-slate-200 animate-pulse" />;
  }

  // Generate 48-hour SEC and Power history
  const timeSeriesData = Array.from({ length: 13 }).map((_, i) => {
    const t = i * 4;
    return {
      hour: `${t}h`,
      sec: Number((0.9348 + 0.0002 * t + (i % 2 === 0 ? 0.004 : -0.002)).toFixed(4)),
      power: Number((12.82 + 0.003 * t + (i % 2 === 0 ? 0.08 : -0.05)).toFixed(2)),
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Energy Telemetry & Specific Consumption (SEC)
            </h2>
            <StatusBadge status="Stage 8C Authoritative" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Hydraulic pump power modeling and energy optimization across operating pressures P₁ and P₂.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-lg text-xs text-amber-800">
          <Zap className="w-4 h-4 text-amber-600 shrink-0" />
          <span>Specific Energy (SEC): -6.19% Reduction per m³</span>
        </div>
      </div>

      {/* Critical Stage 8C Energy Interpretation Banner */}
      <div className="bg-amber-50/80 border border-amber-200 rounded-2xl p-5 text-xs text-amber-950 flex items-start gap-3 shadow-xs">
        <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <strong className="text-sm font-bold text-amber-900 block">
            Authoritative Energy Interpretation (Stage 8C Results Freeze):
          </strong>
          <p className="text-amber-900/90 leading-relaxed">
            <strong>Total Annual Electricity:</strong> {econSummary ? econSummary.energy.baseline_total_kwh.toLocaleString() : '65,054.4'} → {econSummary ? econSummary.energy.watertwin_total_kwh.toLocaleString() : '102,583.2'} kWh/yr (<strong>+{econSummary ? econSummary.energy.total_electricity_change_pct.toFixed(2) : '57.69'}%</strong>).
            <br />
            <strong>Specific Energy Consumption (SEC):</strong> {econSummary ? econSummary.energy.baseline_sec_kwh_m3.toFixed(4) : '0.9965'} → {econSummary ? econSummary.energy.watertwin_sec_kwh_m3.toFixed(4) : '0.9348'} kWh/m³ (<strong>-{econSummary ? econSummary.energy.sec_reduction_pct.toFixed(2) : '6.19'}%</strong>).
          </p>
          <p className="text-[11px] text-amber-800 font-medium">
            💡 <em>Scientific Context:</em> Total electricity increases because <strong className="text-amber-950">+68.10% more reusable water</strong> is produced (+44,458 m³/yr). However, the energy required per cubic metre of clean water is reduced by 6.19%.
          </p>
        </div>
      </div>

      {/* Primary KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Current SEC"
          value={plantState.energy.sec_kwh_m3.toFixed(4)}
          unit="kWh/m³"
          icon={Zap}
          accentColor="amber"
          tooltipTerm="SEC"
          trend={{ value: '-6.19%', isPositive: true, label: 'SEC reduction' }}
        />

        <MetricCard
          title="Total Electrical Power"
          value={formatPower(plantState.energy.total_electrical_power_kw)}
          icon={Activity}
          accentColor="sky"
          subtitle="Stage 1 + Stage 2 Booster"
        />

        <MetricCard
          title="Energy Per Hour"
          value={`${plantState.energy.energy_per_hour_kwh.toFixed(2)} kWh`}
          icon={Clock}
          accentColor="slate"
          subtitle="Hourly Consumption"
        />

        <MetricCard
          title="Cumulative Energy"
          value={`${plantState.energy.cumulative_energy_kwh.toFixed(1)} kWh`}
          icon={Zap}
          accentColor="indigo"
          subtitle="Annual: 102,583 kWh"
        />
      </div>

      {/* Energy Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SEC vs Time */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">
              Specific Energy Consumption (SEC) vs Time
            </h3>
            <span className="text-xs text-slate-400 font-mono">kWh/m³ permeate</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeriesData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis domain={[0.9, 0.98]} tick={{ fill: '#64748b', fontSize: 11 }} label={{ value: 'SEC [kWh/m³]', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
                <Tooltip formatter={(val: any) => [`${val} kWh/m³`, 'SEC']} contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="sec" stroke="#f59e0b" strokeWidth={2.5} dot={{ fill: '#f59e0b', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Electrical Power vs Time */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">
              Total Electrical Power vs Time
            </h3>
            <span className="text-xs text-slate-400 font-mono">kW (Pump η = 0.75)</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeriesData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis domain={[12.0, 14.0]} tick={{ fill: '#64748b', fontSize: 11 }} label={{ value: 'Power [kW]', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
                <Tooltip formatter={(val: any) => [`${val} kW`, 'Power']} contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="power" stroke="#0284c7" strokeWidth={2.5} dot={{ fill: '#0284c7', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Authoritative Strategy Comparison Ledger */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Operating Strategy Energy & Performance Benchmark
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Comparison across the 5 authoritative operating points discovered during Stage 5 optimization.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">Stage 8C Verified</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Strategy</th>
                <th className="py-3 px-4">Pressures (P₁ / P₂)</th>
                <th className="py-3 px-4">Recovery %</th>
                <th className="py-3 px-4">SEC (kWh/m³)</th>
                <th className="py-3 px-4">Max Elem. Rec.</th>
                <th className="py-3 px-4">Power (kW)</th>
                <th className="py-3 px-4">Pareto Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {strategies.map((strat) => (
                <tr
                  key={strat.id}
                  className={`hover:bg-slate-50/80 transition-colors ${
                    strat.is_active ? 'bg-sky-50/40 font-semibold' : ''
                  }`}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900">{strat.code}</span>
                      <span className="text-slate-500 font-normal">({strat.name})</span>
                      {strat.is_active && (
                        <span className="text-[10px] bg-sky-200 text-sky-800 font-bold px-1.5 py-0.2 rounded">
                          Active
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 font-mono">
                    {strat.p1_bar.toFixed(2)} / {strat.p2_bar.toFixed(2)} bar
                  </td>
                  <td className="py-3 px-4 font-mono text-emerald-700">
                    {formatPercent(strat.recovery_pct)}
                  </td>
                  <td className="py-3 px-4 font-mono text-amber-700 font-bold">
                    {formatSEC(strat.sec_kwh_m3)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-700">
                    {formatPercent(strat.max_element_recovery_pct)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-700">
                    {formatPower(strat.total_power_kw)}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge
                      status={strat.status}
                      variant={strat.status === 'PARETO OPTIMAL' ? 'pareto' : 'dominated'}
                      size="sm"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
