'use client';

import React, { useState } from 'react';
import {
  FlaskConical,
  Play,
  RotateCcw,
  ShieldCheck,
  AlertTriangle,
  Zap,
  Droplets,
  Layers,
  Gauge,
  Clock,
  Sparkles,
} from 'lucide-react';
import { simulationService } from '@/services/simulationService';
import { SimulationRequest, SimulationResult } from '@/types/simulation';
import { StatusBadge } from '@/components/common/StatusBadge';
import { ModelAuditBench } from '@/components/charts/ModelAuditBench';
import { formatFlow, formatTDS, formatPressure, formatTemperature, formatSEC, formatPower, formatPercent } from '@/utils/formatters';

export default function ScenariosPage() {
  const [params, setParams] = useState<SimulationRequest>({
    feed_flow_m3_h: 30.0,
    feed_tds_mg_l: 2041.0,
    temperature_c: 25.0,
    p1_bar: 16.06,
    p2_bar: 16.41,
    simulation_duration_hours: 48.0,
  });

  const [result, setResult] = useState<SimulationResult | null>(null);
  const [running, setRunning] = useState(false);

  const handleRunSimulation = async () => {
    setRunning(true);
    try {
      const res = await simulationService.runSimulation(params);
      setResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setRunning(false);
    }
  };

  const handleReset = () => {
    setParams({
      feed_flow_m3_h: 30.0,
      feed_tds_mg_l: 2041.0,
      temperature_c: 25.0,
      p1_bar: 16.06,
      p2_bar: 16.41,
      simulation_duration_hours: 48.0,
    });
    setResult(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Virtual Twin Scenario Simulator
            </h2>
            <StatusBadge status="Model V2.0 Sandbox" variant="virtual" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Evaluate feed disturbances and operating pressure scenarios against authoritative mechanistic equations.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg text-xs text-sky-900">
          <FlaskConical className="w-4 h-4 text-sky-600 shrink-0" />
          <span>Endpoint: POST /api/v1/simulate</span>
        </div>
      </div>

      {/* Dual Panel Grid (Left: Inputs, Right: Outputs) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Input Panel (5 Cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <FlaskConical className="w-4 h-4 text-sky-600" />
              Experiment Inputs
            </h3>
            <button
              onClick={handleReset}
              className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Defaults
            </button>
          </div>

          {/* Sliders and Inputs */}
          <div className="space-y-4 text-xs">
            {/* Feed Flow */}
            <div className="space-y-1.5">
              <div className="flex justify-between font-medium">
                <span className="text-slate-700">Feed Flow (Qf):</span>
                <span className="font-mono font-bold text-sky-700">{params.feed_flow_m3_h} m³/h</span>
              </div>
              <input
                type="range"
                min="15.0"
                max="45.0"
                step="0.5"
                value={params.feed_flow_m3_h}
                onChange={(e) => setParams({ ...params, feed_flow_m3_h: parseFloat(e.target.value) })}
                className="w-full accent-sky-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>15.0 m³/h</span>
                <span>Baseline: 30.0</span>
                <span>45.0 m³/h</span>
              </div>
            </div>

            {/* Feed TDS */}
            <div className="space-y-1.5">
              <div className="flex justify-between font-medium">
                <span className="text-slate-700">Feed Salinity (Cf):</span>
                <span className="font-mono font-bold text-sky-700">{params.feed_tds_mg_l} mg/L</span>
              </div>
              <input
                type="range"
                min="1000"
                max="4000"
                step="25"
                value={params.feed_tds_mg_l}
                onChange={(e) => setParams({ ...params, feed_tds_mg_l: parseFloat(e.target.value) })}
                className="w-full accent-sky-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>1000 mg/L</span>
                <span>Baseline: 2041</span>
                <span>4000 mg/L</span>
              </div>
            </div>

            {/* Temperature */}
            <div className="space-y-1.5">
              <div className="flex justify-between font-medium">
                <span className="text-slate-700">Temperature (T):</span>
                <span className="font-mono font-bold text-sky-700">{params.temperature_c} °C</span>
              </div>
              <input
                type="range"
                min="15.0"
                max="35.0"
                step="0.5"
                value={params.temperature_c}
                onChange={(e) => setParams({ ...params, temperature_c: parseFloat(e.target.value) })}
                className="w-full accent-sky-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>15.0 °C</span>
                <span>Standard: 25.0</span>
                <span>35.0 °C</span>
              </div>
            </div>

            {/* Stage 1 Pressure P1 */}
            <div className="space-y-1.5">
              <div className="flex justify-between font-medium">
                <span className="text-slate-700">Stage 1 Pressure (P₁):</span>
                <span className="font-mono font-bold text-emerald-700">{params.p1_bar} bar</span>
              </div>
              <input
                type="range"
                min="10.0"
                max="20.0"
                step="0.1"
                value={params.p1_bar}
                onChange={(e) => setParams({ ...params, p1_bar: parseFloat(e.target.value) })}
                className="w-full accent-emerald-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>10.0 bar</span>
                <span>Strategy D: 16.06</span>
                <span>20.0 bar</span>
              </div>
            </div>

            {/* Stage 2 Pressure P2 */}
            <div className="space-y-1.5">
              <div className="flex justify-between font-medium">
                <span className="text-slate-700">Stage 2 Pressure (P₂):</span>
                <span className="font-mono font-bold text-emerald-700">{params.p2_bar} bar</span>
              </div>
              <input
                type="range"
                min="14.0"
                max="28.0"
                step="0.1"
                value={params.p2_bar}
                onChange={(e) => setParams({ ...params, p2_bar: parseFloat(e.target.value) })}
                className="w-full accent-emerald-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>14.0 bar</span>
                <span>Strategy D: 16.41</span>
                <span>28.0 bar</span>
              </div>
            </div>

            {/* Duration */}
            <div className="space-y-1.5">
              <div className="flex justify-between font-medium">
                <span className="text-slate-700">Simulation Horizon:</span>
                <span className="font-mono font-bold text-slate-800">{params.simulation_duration_hours} hours</span>
              </div>
              <input
                type="range"
                min="12"
                max="168"
                step="6"
                value={params.simulation_duration_hours}
                onChange={(e) => setParams({ ...params, simulation_duration_hours: parseFloat(e.target.value) })}
                className="w-full accent-indigo-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>12 h</span>
                <span>48 h</span>
                <span>168 h (1 Week)</span>
              </div>
            </div>
          </div>

          {/* Action Run Button */}
          <button
            onClick={handleRunSimulation}
            disabled={running}
            className="w-full py-3 px-4 bg-gradient-to-r from-sky-600 to-emerald-600 hover:from-sky-700 hover:to-emerald-700 text-white font-bold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-50 cursor-pointer"
          >
            {running ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Solving Mechanistic Equations...
              </span>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                RUN VIRTUAL TWIN SIMULATION
              </>
            )}
          </button>
        </div>

        {/* Right Output Panel (7 Cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">
                  Predicted Virtual Twin Response
                </h3>
                <p className="text-xs text-slate-400">
                  {result ? result.model_version : 'Ready to execute experiment'}
                </p>
              </div>

              {result && (
                <StatusBadge status={`Solved in ${result.execution_time_ms} ms`} variant="healthy" size="sm" />
              )}
            </div>

            {/* Result Displays */}
            {result ? (
              <div className="space-y-4 my-4">
                {/* Warnings Banner if any */}
                {result.warnings.length > 0 && (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 space-y-1 text-xs text-amber-900">
                    {result.warnings.map((w, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                        <span>{w}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Key Outputs Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <span className="text-[11px] font-medium text-slate-500 block">Overall Recovery</span>
                    <span className="text-xl font-bold font-mono text-emerald-700">
                      {formatPercent(result.outputs.overall_recovery_pct)}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Product yield</span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <span className="text-[11px] font-medium text-slate-500 block">Permeate Flow</span>
                    <span className="text-xl font-bold font-mono text-sky-700">
                      {formatFlow(result.outputs.permeate_flow_m3_h)}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Total product</span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <span className="text-[11px] font-medium text-slate-500 block">Permeate TDS</span>
                    <span className="text-xl font-bold font-mono text-slate-800">
                      {formatTDS(result.outputs.permeate_tds_mg_l)}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Salinity</span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <span className="text-[11px] font-medium text-slate-500 block">Specific Energy (SEC)</span>
                    <span className="text-xl font-bold font-mono text-amber-700">
                      {formatSEC(result.outputs.sec_kwh_m3)}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Energy efficiency</span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <span className="text-[11px] font-medium text-slate-500 block">Total Power</span>
                    <span className="text-xl font-bold font-mono text-slate-800">
                      {formatPower(result.outputs.total_power_kw)}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Pump requirement</span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <span className="text-[11px] font-medium text-slate-500 block">Peak Element Recovery</span>
                    <span
                      className={`text-xl font-bold font-mono ${
                        result.outputs.max_element_recovery_pct > 30.0 ? 'text-rose-600' : 'text-slate-800'
                      }`}
                    >
                      {formatPercent(result.outputs.max_element_recovery_pct)}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">&le; 30% limit</span>
                  </div>
                </div>

                {/* Secondary Diagnostics */}
                <div className="bg-slate-50/70 p-3.5 rounded-xl border border-slate-200 text-xs text-slate-600 space-y-1.5">
                  <div className="flex justify-between">
                    <span>Salt Rejection:</span>
                    <strong className="text-emerald-700">{formatPercent(result.outputs.salt_rejection_pct)}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Stage 1 Recovery / Stage 2 Recovery:</span>
                    <strong>{formatPercent(result.outputs.stage1_recovery_pct)} / {formatPercent(result.outputs.stage2_recovery_pct)}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Predicted Dynamic Fouling Decline ({params.simulation_duration_hours}h):</span>
                    <strong className="text-amber-700">-{formatPercent(result.outputs.predicted_fouling_decline_pct)}</strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-slate-400 space-y-2">
                <Sparkles className="w-8 h-8 mx-auto text-slate-300" />
                <p className="text-xs">Adjust feed parameters and press &quot;Run Virtual Twin Simulation&quot;</p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span>Clean Architecture: API-ready contract</span>
            <span className="font-mono">POST /api/v1/simulate</span>
          </div>
        </div>
      </div>

      {/* Ground Truth Parity & Speed Audit Matrix */}
      <ModelAuditBench />
    </div>
  );
}
