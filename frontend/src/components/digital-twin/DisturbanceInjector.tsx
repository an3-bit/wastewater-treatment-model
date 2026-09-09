'use client';

import React, { useState } from 'react';
import {
  Zap,
  Activity,
  Droplets,
  AlertTriangle,
  Radio,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  ShieldAlert,
  Sliders,
  CheckCircle2,
} from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatFlow, formatTDS, formatTemperature, formatPressure, formatSEC, formatPercent } from '@/utils/formatters';

export interface DisturbancePreset {
  id: string;
  name: string;
  badge: string;
  badgeVariant: 'healthy' | 'normal' | 'warning' | 'virtual';
  feed_flow: number;
  feed_tds: number;
  temperature: number;
  p1: number;
  p2: number;
  description: string;
  expected_impact: string;
}

export const disturbancePresets: DisturbancePreset[] = [
  {
    id: 'baseline',
    name: 'Standard Operational Baseline',
    badge: 'Nominal Case',
    badgeVariant: 'healthy',
    feed_flow: 30.0,
    feed_tds: 2041.0,
    temperature: 25.0,
    p1: 16.06,
    p2: 16.41,
    description: 'Steady-state operation at Strategy D balanced knee condition.',
    expected_impact: 'Recovery: 70.22%, SEC: 0.7269 kWh/m³, EKF NIS: Normal',
  },
  {
    id: 'salinity_shock',
    name: 'Textile Reactive Dye Salinity Shock (+60%)',
    badge: 'Salinity Surge',
    badgeVariant: 'warning',
    feed_flow: 30.0,
    feed_tds: 3260.0,
    temperature: 25.0,
    p1: 16.06,
    p2: 16.41,
    description: 'Sudden discharge of high-salt reactive dyeing wastewater into MBR effluent.',
    expected_impact: 'Osmotic pressure increases from 1.73 to 2.76 bar. Net driving pressure drops, SEC rises to 0.795 kWh/m³.',
  },
  {
    id: 'hydraulic_surge',
    name: 'Peak Hydraulic Load Surge (+20%)',
    badge: 'High Flow',
    badgeVariant: 'normal',
    feed_flow: 36.0,
    feed_tds: 2041.0,
    temperature: 25.0,
    p1: 17.2,
    p2: 17.5,
    description: 'Industrial production batch ramp-up increasing feed flow to 36 m³/h.',
    expected_impact: 'Crossflow velocity increases, mass transfer k improves, but pump power jumps to 19.4 kW.',
  },
  {
    id: 'winter_cold',
    name: 'Winter Low-Temperature Shock (16°C)',
    badge: 'High Viscosity',
    badgeVariant: 'warning',
    feed_flow: 30.0,
    feed_tds: 2041.0,
    temperature: 16.0,
    p1: 16.06,
    p2: 16.41,
    description: 'Cold weather drops water temperature, elevating dynamic viscosity from 0.89 to 1.11 mPa·s.',
    expected_impact: 'Water permeability Aw drops ~21%. Permeate flow declines from 21.07 to 17.2 m³/h unless pressure is elevated.',
  },
];

interface DisturbanceInjectorProps {
  onDisturbanceChange?: (preset: DisturbancePreset) => void;
}

export function DisturbanceInjector({ onDisturbanceChange }: DisturbanceInjectorProps) {
  const [activePresetId, setActivePresetId] = useState<string>('baseline');
  const [isLiveStreaming, setIsLiveStreaming] = useState<boolean>(true);
  const [customFlow, setCustomFlow] = useState<number>(30.0);
  const [customTds, setCustomTds] = useState<number>(2041.0);
  const [customTemp, setCustomTemp] = useState<number>(25.0);

  const activePreset = disturbancePresets.find((p) => p.id === activePresetId) || disturbancePresets[0];

  const handleSelectPreset = (preset: DisturbancePreset) => {
    setActivePresetId(preset.id);
    setCustomFlow(preset.feed_flow);
    setCustomTds(preset.feed_tds);
    setCustomTemp(preset.temperature);
    if (onDisturbanceChange) {
      onDisturbanceChange(preset);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Radio className="w-4 h-4 text-sky-600" />
              Live Disturbance Injection & Telemetry Controller
            </h3>
            <StatusBadge status={isLiveStreaming ? 'Streaming Live (1.0 Hz)' : 'Paused'} variant={isLiveStreaming ? 'healthy' : 'warning'} />
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Inject hydraulic, thermal, or salinity disturbances to test real-time EKF virtual sensor convergence and stream balances.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsLiveStreaming(!isLiveStreaming)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all shadow-xs ${
              isLiveStreaming
                ? 'bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100'
                : 'bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100'
            }`}
          >
            {isLiveStreaming ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Pause Stream</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Resume Stream</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Preset Disturbance Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {disturbancePresets.map((preset) => {
          const isSelected = preset.id === activePresetId;
          return (
            <button
              key={preset.id}
              onClick={() => handleSelectPreset(preset)}
              className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'border-sky-600 bg-sky-50/70 ring-1 ring-sky-500/30'
                  : 'border-slate-200 hover:border-slate-300 bg-slate-50/40'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <span className="text-xs font-bold text-slate-900 leading-tight">
                    {preset.name}
                  </span>
                  <StatusBadge status={preset.badge} variant={preset.badgeVariant} size="sm" />
                </div>
                <p className="text-[11px] text-slate-500 leading-snug line-clamp-2">
                  {preset.description}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[10px] font-mono text-slate-600">
                <span>{preset.feed_flow} m³/h</span>
                <span>{preset.feed_tds} mg/L</span>
                <span>{preset.temperature}°C</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Real-time Dynamic Response Readout */}
      <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Active Stream Conditions
            </span>
            <span className="text-[11px] font-bold text-sky-800 bg-sky-100 px-2 py-0.5 rounded">
              {activePreset.name}
            </span>
          </div>
          <p className="text-xs text-slate-600">
            {activePreset.expected_impact}
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono bg-white p-2.5 rounded-lg border border-slate-200 shrink-0">
          <div>
            <span className="text-[10px] text-slate-400 block font-sans">Feed Flow</span>
            <span className="font-bold text-slate-800">{customFlow.toFixed(1)} m³/h</span>
          </div>
          <div className="border-l border-slate-100 pl-3">
            <span className="text-[10px] text-slate-400 block font-sans">Salinity</span>
            <span className="font-bold text-slate-800">{customTds.toFixed(0)} mg/L</span>
          </div>
          <div className="border-l border-slate-100 pl-3">
            <span className="text-[10px] text-slate-400 block font-sans">Temperature</span>
            <span className="font-bold text-slate-800">{customTemp.toFixed(1)} °C</span>
          </div>
        </div>
      </div>
    </div>
  );
}
