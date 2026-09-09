'use client';

import React from 'react';
import { X, Layers, Activity, Gauge, Droplets } from 'lucide-react';
import { ROStageState } from '@/types/digitalTwin';
import { formatFlow, formatPressure, formatTDS, formatPercent } from '@/utils/formatters';

interface StageDetailModalProps {
  stage: ROStageState | null;
  onClose: () => void;
}

export function StageDetailModal({ stage, onClose }: StageDetailModalProps) {
  if (!stage) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-2xl w-full p-6 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-sky-50 text-sky-700">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Stage {stage.stage_number} Detailed Hydraulic & Membrane Profile
              </h3>
              <p className="text-xs text-slate-500">
                {stage.stage_number === 1
                  ? '3 Vessels in Parallel × 3 Elements in Series (9 elements total)'
                  : '2 Vessels in Parallel × 3 Elements in Series (6 elements total)'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
            aria-label="Close details"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Key Stage Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-5">
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span className="text-[11px] font-medium text-slate-500 block">Feed Pressure</span>
            <span className="text-base font-bold text-slate-800">{formatPressure(stage.inlet_pressure_bar)}</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span className="text-[11px] font-medium text-slate-500 block">Pressure Drop (ΔP)</span>
            <span className="text-base font-bold text-amber-700">{formatPressure(stage.pressure_drop_bar)}</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span className="text-[11px] font-medium text-slate-500 block">Stage Recovery</span>
            <span className="text-base font-bold text-emerald-700">{formatPercent(stage.stage_recovery_pct)}</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span className="text-[11px] font-medium text-slate-500 block">Average Flux</span>
            <span className="text-base font-bold text-sky-700">{stage.avg_flux_lmh.toFixed(1)} LMH</span>
          </div>
        </div>

        {/* Detailed Stream Breakdown */}
        <div className="space-y-3 bg-slate-50/70 p-4 rounded-xl border border-slate-200">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
            Mass Balance & Stream Composition
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
              <span className="font-semibold text-slate-700 block">Inlet Feed Stream</span>
              <div className="flex justify-between text-slate-600">
                <span>Flow:</span>
                <strong>{formatFlow(stage.feed_flow_m3_h)}</strong>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Inlet Press:</span>
                <strong>{formatPressure(stage.inlet_pressure_bar)}</strong>
              </div>
            </div>

            <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
              <span className="font-semibold text-emerald-700 block">Permeate Product</span>
              <div className="flex justify-between text-slate-600">
                <span>Flow:</span>
                <strong>{formatFlow(stage.permeate_flow_m3_h)}</strong>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Permeate TDS:</span>
                <strong>{formatTDS(stage.permeate_tds_mg_l)}</strong>
              </div>
            </div>

            <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
              <span className="font-semibold text-amber-700 block">Concentrate Stream</span>
              <div className="flex justify-between text-slate-600">
                <span>Flow:</span>
                <strong>{formatFlow(stage.concentrate_flow_m3_h)}</strong>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Conc TDS:</span>
                <strong>{formatTDS(stage.concentrate_tds_mg_l)}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Membrane Vessel Configuration Layout */}
        <div className="mt-4 p-3 bg-sky-50/50 rounded-xl border border-sky-200 text-xs text-sky-950 flex items-center justify-between">
          <div>
            <span className="font-semibold block">Toray TM720D-400 Membrane Array</span>
            <span className="text-[11px] text-sky-800">
              Total Stage Membrane Area: {stage.total_elements * 37.0} m²
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-medium rounded-lg text-xs transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
}
