'use client';

import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  FlaskConical,
  Play,
  RotateCcw,
  CheckCircle2,
  TrendingDown,
  Clock,
  Zap,
  ShieldCheck,
  DollarSign,
  Info,
} from 'lucide-react';
import { CIPProtocol, CIPProtocolType, CleaningSimulationResult } from '@/types/cleaning';
import { cleaningService } from '@/services/cleaningService';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatPercent, formatSEC, formatHours } from '@/utils/formatters';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

export function CleaningAdvisor() {
  const [protocols, setProtocols] = useState<CIPProtocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<CIPProtocolType>('combined_two_step');
  const [efficiency, setEfficiency] = useState<number>(0.92);
  const [targetStages, setTargetStages] = useState<'both' | 'stage1_only' | 'stage2_only'>('both');
  const [result, setResult] = useState<CleaningSimulationResult | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  useEffect(() => {
    async function init() {
      const p = await cleaningService.getCIPProtocols();
      setProtocols(p);
      const initialRes = await cleaningService.runCleaningSimulation({
        cleaning_efficiency: 0.92,
        protocol_id: 'combined_two_step',
        target_stages: 'both',
      });
      setResult(initialRes);
    }
    init();
  }, []);

  const handleSimulateCIP = async () => {
    setSimulating(true);
    try {
      const res = await cleaningService.runCleaningSimulation({
        cleaning_efficiency: efficiency,
        protocol_id: selectedProtocol,
        target_stages: targetStages,
      });
      setResult(res);
    } finally {
      setSimulating(false);
    }
  };

  const currentProtocolObj = protocols.find((p) => p.id === selectedProtocol);

  if (!result || !currentProtocolObj) {
    return <div className="h-64 bg-slate-100 rounded-2xl animate-pulse" />;
  }

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-600" />
              Chemical Cleaning-In-Place (CIP) & Maintenance Advisor
            </h3>
            <StatusBadge status="Stage 8 CIP Physics" variant="virtual" />
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Optimize chemical wash timing and simulate hydraulic permeability restoration (ΔR<sub>f</sub> = (1 - η<sub>clean</sub>) R<sub>f</sub>).
          </p>
        </div>

        <button
          onClick={handleSimulateCIP}
          disabled={simulating}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm shadow-indigo-200 transition-all active:scale-95 disabled:opacity-50 self-start sm:self-auto"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{simulating ? 'Evaluating CIP Physics...' : 'Simulate CIP Event'}</span>
        </button>
      </div>

      {/* Control Grid: Protocol Selector & Sliders */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Protocol Selectors */}
        <div className="lg:col-span-6 space-y-4">
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2">
              Select CIP Chemical Protocol
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {protocols.map((p) => {
                const isSelected = p.id === selectedProtocol;
                return (
                  <button
                    key={p.id}
                    onClick={() => {
                      setSelectedProtocol(p.id);
                      setEfficiency(p.typical_efficiency_pct / 100.0);
                    }}
                    className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'border-indigo-600 bg-indigo-50/60 ring-1 ring-indigo-500/30'
                        : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
                    }`}
                  >
                    <div>
                      <span className="text-xs font-bold text-slate-900 block leading-snug">
                        {p.name}
                      </span>
                      <span className="text-[11px] text-indigo-700 font-medium block mt-1">
                        {p.target_foulant}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-200/60 text-[10px] text-slate-500">
                      <span>{p.ph_target}</span>
                      <span className="font-semibold text-emerald-700">{p.typical_efficiency_pct}% η</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Target Stage & Efficiency Slider */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700">Target Vessel Scope</span>
              <div className="flex bg-slate-200 p-0.5 rounded-lg text-[11px] font-medium">
                <button
                  onClick={() => setTargetStages('both')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    targetStages === 'both' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-600'
                  }`}
                >
                  All 15 Elements
                </button>
                <button
                  onClick={() => setTargetStages('stage1_only')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    targetStages === 'stage1_only' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Stage 1 Lead
                </button>
                <button
                  onClick={() => setTargetStages('stage2_only')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    targetStages === 'stage2_only' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Stage 2 Tail
                </button>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600">Chemical Cleaning Efficiency (η<sub>clean</sub>)</span>
                <span className="font-mono font-bold text-indigo-700">
                  {(efficiency * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.60"
                max="0.99"
                step="0.01"
                value={efficiency}
                onChange={(e) => setEfficiency(parseFloat(e.target.value))}
                className="w-full accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>60% (Mild Rinse)</span>
                <span>90% (Standard)</span>
                <span>99% (Aggressive Multi-Step)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Key Post-CIP Outcomes */}
        <div className="lg:col-span-6 flex flex-col justify-between space-y-3">
          <div className="grid grid-cols-2 gap-3">
            {/* Flux Recovery Card */}
            <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-emerald-800 tracking-wider flex items-center gap-1">
                <TrendingDown className="w-3.5 h-3.5 text-emerald-600" />
                Residual Flux Decline
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-extrabold text-emerald-950">
                  {result.restored_flux_decline_pct}%
                </span>
                <span className="text-xs text-slate-400 line-through">
                  {result.initial_flux_decline_pct}%
                </span>
              </div>
              <p className="text-[11px] text-emerald-800 font-medium">
                -{(result.initial_flux_decline_pct - result.restored_flux_decline_pct).toFixed(2)}% permeability regained
              </p>
            </div>

            {/* Life Extension Card */}
            <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-indigo-800 tracking-wider flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-indigo-600" />
                Extended Service Life
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-extrabold text-indigo-950">
                  +{result.extended_operating_life_hours} h
                </span>
              </div>
              <p className="text-[11px] text-indigo-800 font-medium">
                Postpones t₁₀ threshold crossing
              </p>
            </div>

            {/* Energy Savings */}
            <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-amber-800 tracking-wider flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-amber-600" />
                Restored Energy SEC
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-extrabold text-amber-950">
                  {result.restored_sec_kwh_m3}
                </span>
                <span className="text-xs text-slate-400">kWh/m³</span>
              </div>
              <p className="text-[11px] text-amber-800 font-medium">
                -{result.sec_reduction_pct}% pumping power penalty
              </p>
            </div>

            {/* Net Cost Savings */}
            <div className="p-4 bg-sky-50/70 border border-sky-200 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-sky-800 tracking-wider flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5 text-sky-600" />
                Net Power Savings
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-extrabold text-sky-950">
                  ${result.net_energy_savings_usd_month}
                </span>
                <span className="text-xs text-slate-500">/month</span>
              </div>
              <p className="text-[11px] text-sky-800 font-medium">
                Est. chemical cost: ${result.chemical_cost_usd_est}
              </p>
            </div>
          </div>

          {/* Operational Protocol Notes Banner */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-start gap-2">
            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-800 block font-semibold">Recommended CIP Execution:</strong>
              <p className="text-[11px] text-slate-600 mt-0.5 leading-relaxed">
                Flush with warm permeate (35°C) at low pressure (2 bar) for {currentProtocolObj.contact_time_min} mins. Recirculate {currentProtocolObj.chemical_agent} at {currentProtocolObj.ph_target}.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 6-Zone Axial Resistance Restoration Chart */}
      <div className="pt-2 border-t border-slate-100">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
          Zone-by-Zone Fouling Resistance Restoration (R<sub>f</sub> in 10¹² m⁻¹)
        </h4>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={result.zone_restorations}
              margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="zone_label" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748b' }}
                label={{
                  value: 'Rf [10¹² m⁻¹]',
                  angle: -90,
                  position: 'insideLeft',
                  fontSize: 11,
                  fill: '#64748b',
                }}
              />
              <Tooltip
                formatter={(value: any, name: string) => [
                  `${value} × 10¹² m⁻¹`,
                  name === 'initial_rf_e12' ? 'Initial Rf (Pre-CIP)' : 'Restored Rf (Post-CIP)',
                ]}
              />
              <Legend
                verticalAlign="top"
                align="right"
                wrapperStyle={{ fontSize: '11px', paddingBottom: '8px' }}
              />
              <Bar dataKey="initial_rf_e12" name="Pre-CIP Resistance" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="restored_rf_e12" name="Post-CIP Resistance" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
