import React from 'react';
import { MembraneZoneState } from '@/types/membrane';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatResistanceScientific, formatPercent } from '@/utils/formatters';
import { TrendingUp, Layers, Activity } from 'lucide-react';

interface MembraneZoneCardProps {
  zone: MembraneZoneState;
}

export function MembraneZoneCard({ zone }: MembraneZoneCardProps) {
  const statusBorders = {
    healthy: 'border-emerald-200 bg-white hover:border-emerald-400',
    normal: 'border-sky-200 bg-white hover:border-sky-400',
    approaching_threshold: 'border-amber-300 bg-amber-50/20 hover:border-amber-400',
    severe_warning: 'border-rose-300 bg-rose-50/20 hover:border-rose-400',
  };

  const trendLabels = {
    stable: 'Stable Kinetics',
    slow_growth: 'Gradual Cake Layer Growth',
    rapid_growth: 'Accelerated Tail Fouling',
    improving: 'Permeate Flux Recovery',
  };

  return (
    <div
      className={`rounded-2xl p-5 border shadow-xs transition-all ${statusBorders[zone.status]}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Stage {zone.stage_number} Axial Subdomain
          </span>
          <h4 className="text-base font-bold text-slate-900 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-sky-600" />
            {zone.zone_label}
          </h4>
        </div>
        <StatusBadge
          status={zone.status.replace('_', ' ')}
          variant={
            zone.status === 'healthy'
              ? 'healthy'
              : zone.status === 'approaching_threshold'
              ? 'warning'
              : zone.status === 'severe_warning'
              ? 'severe'
              : 'normal'
          }
        />
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 my-3">
        <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
          <span className="text-[11px] font-medium text-slate-500 block">Estimated Fouling (Rf)</span>
          <span className="text-sm font-bold font-mono text-slate-900">
            {formatResistanceScientific(zone.rf_m_inv)}
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Hydraulic resistance</span>
        </div>

        <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
          <span className="text-[11px] font-medium text-slate-500 block">Decline %</span>
          <span
            className={`text-sm font-bold font-mono ${
              zone.permeability_decline_pct >= 10.0
                ? 'text-amber-700'
                : zone.permeability_decline_pct >= 5.0
                ? 'text-sky-700'
                : 'text-emerald-700'
            }`}
          >
            {formatPercent(zone.permeability_decline_pct)}
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">vs clean baseline</span>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="space-y-1 text-xs text-slate-600 bg-slate-50/50 p-2.5 rounded-xl border border-slate-100">
        <div className="flex justify-between">
          <span>Normalized Permeability:</span>
          <strong className="text-slate-800">{zone.normalized_permeability_lmh_bar.toFixed(2)} LMH/bar</strong>
        </div>
        <div className="flex justify-between">
          <span>Virtual Sensor Confidence:</span>
          <strong className="text-emerald-700">{zone.state_confidence_pct.toFixed(1)}%</strong>
        </div>
        <div className="flex justify-between">
          <span>Elements Represented:</span>
          <span className="font-mono text-slate-700">{zone.vessels_represented}</span>
        </div>
      </div>

      {/* Trend Footer */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
        <span className="text-slate-500 flex items-center gap-1">
          <TrendingUp className="w-3.5 h-3.5 text-slate-400" />
          <span>{trendLabels[zone.trend]}</span>
        </span>
        <span className="text-[10px] font-mono text-slate-400">EKF Zone {zone.zone_id}</span>
      </div>
    </div>
  );
}
