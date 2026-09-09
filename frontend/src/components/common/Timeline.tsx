import React from 'react';
import { Activity, Cpu, TrendingUp } from 'lucide-react';

interface TimelineProps {
  currentSimHour?: number;
  measuredWindowHours?: number;
  forecastHorizonHours?: number;
  className?: string;
}

export function Timeline({
  currentSimHour = 48.0,
  measuredWindowHours = 48.0,
  forecastHorizonHours = 72.0,
  className = '',
}: TimelineProps) {
  return (
    <div className={`bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-sm ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Digital Twin Temporal Framework
          </span>
          <span className="text-[10px] bg-sky-50 text-sky-700 font-mono px-2 py-0.5 rounded border border-sky-200">
            t = {currentSimHour.toFixed(1)} h
          </span>
        </div>
        <span className="text-xs text-slate-400">Continuous 1-hour supervisory cycle</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 relative">
        {/* Step 1: Measured */}
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-sky-600" />
                1. Measured Plant Telemetry
              </span>
              <span className="text-[10px] font-mono text-slate-500">PAST (0 → {measuredWindowHours}h)</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Standard 10-sensor skid telemetry (Q<sub>f</sub>, C<sub>f</sub>, P<sub>1</sub>, P<sub>2</sub>, Q<sub>p,total</sub>, C<sub>p,total</sub>, W<sub>elec</sub>) sampled at 1.0 s intervals.
            </p>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-500">
            <span>Status: <strong className="text-emerald-600">Online</strong></span>
            <span>Noise: <strong>Industrial σ</strong></span>
          </div>
        </div>

        {/* Step 2: Estimated (NOW) */}
        <div className="bg-emerald-50/70 rounded-lg p-3 border border-emerald-300 ring-2 ring-emerald-400/30 flex flex-col justify-between relative">
          <div className="absolute -top-2.5 right-3 bg-emerald-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow-sm">
            NOW (t = {currentSimHour}h)
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-emerald-600" />
                2. EKF State Estimator
              </span>
            </div>
            <p className="text-xs text-emerald-950 leading-relaxed">
              Physics-informed virtual sensor reconstructs unmeasured 6-zone axial fouling resistance (R<sub>f</sub>) &amp; permeability decline.
            </p>
          </div>
          <div className="mt-2 pt-2 border-t border-emerald-200 flex items-center justify-between text-[11px] text-emerald-800">
            <span>Latency: <strong>~105 ms</strong></span>
            <span>State Dim: <strong>n = 6 zones</strong></span>
          </div>
        </div>

        {/* Step 3: Forecast */}
        <div className="bg-amber-50/60 rounded-lg p-3 border border-amber-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-amber-600" />
                3. Predictive Forecasting
              </span>
              <span className="text-[10px] font-mono text-amber-700">FUTURE (+{forecastHorizonHours}h)</span>
            </div>
            <p className="text-xs text-amber-900 leading-relaxed">
              Forward projection of dynamic fouling kinetics to estimate arrival at t₅, t₁₀, t₁₅ Analysis Thresholds.
            </p>
          </div>
          <div className="mt-2 pt-2 border-t border-amber-200 flex items-center justify-between text-[11px] text-amber-800">
            <span>Next: <strong className="text-amber-700">t₁₀ in 34.5 h</strong></span>
            <span>Horizon: <strong>72.0 h</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
