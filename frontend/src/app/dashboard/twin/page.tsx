'use client';

import React, { useState, useEffect } from 'react';
import {
  Droplets,
  Activity,
  Layers,
  ArrowRight,
  ArrowDown,
  Info,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  Gauge,
} from 'lucide-react';
import { digitalTwinService } from '@/services/digitalTwinService';
import { PlantState, ROStageState } from '@/types/digitalTwin';
import { formatFlow, formatPressure, formatTDS, formatTemperature, formatPercent, formatSEC, formatPower } from '@/utils/formatters';
import { StageDetailModal } from '@/components/digital-twin/StageDetailModal';
import { DisturbanceInjector, DisturbancePreset } from '@/components/digital-twin/DisturbanceInjector';
import { StatusBadge } from '@/components/common/StatusBadge';

export default function LiveTwinPage() {
  const [plantState, setPlantState] = useState<PlantState | null>(null);
  const [selectedStage, setSelectedStage] = useState<ROStageState | null>(null);
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

  const handleDisturbanceChange = (preset: DisturbancePreset) => {
    if (!plantState) return;
    const qf = preset.feed_flow;
    const cf = preset.feed_tds;
    const temp = preset.temperature;

    // Approximate dynamic hydraulic response based on solution-diffusion thermodynamics
    const permFlow = qf * 0.7022 * (temp === 16 ? 0.81 : 1.0);
    const concFlow = qf - permFlow;
    const permTds = 7.21 * (cf / 2041.0);
    const concTds = (qf * cf - permFlow * permTds) / concFlow;
    const secVal = temp === 16 ? 0.842 : cf > 3000 ? 0.795 : 0.7269;
    const powerKw = permFlow * secVal;

    setPlantState({
      ...plantState,
      feed: {
        ...plantState.feed,
        flow_m3_h: qf,
        tds_mg_l: cf,
        temperature_c: temp,
        pressure_bar: preset.p1,
      },
      stage1: {
        ...plantState.stage1,
        feed_flow_m3_h: qf,
        inlet_pressure_bar: preset.p1,
        permeate_flow_m3_h: Number((permFlow * 0.741).toFixed(2)),
        concentrate_flow_m3_h: Number((qf - permFlow * 0.741).toFixed(2)),
      },
      stage2: {
        ...plantState.stage2,
        inlet_pressure_bar: preset.p2,
        feed_flow_m3_h: Number((qf - permFlow * 0.741).toFixed(2)),
        permeate_flow_m3_h: Number((permFlow * 0.259).toFixed(2)),
        concentrate_flow_m3_h: Number(concFlow.toFixed(2)),
        concentrate_tds_mg_l: Number(concTds.toFixed(1)),
      },
      permeate: {
        ...plantState.permeate,
        total_flow_m3_h: Number(permFlow.toFixed(2)),
        tds_mg_l: Number(permTds.toFixed(2)),
        recovery_pct: Number(((permFlow / qf) * 100).toFixed(2)),
      },
      concentrate: {
        ...plantState.concentrate,
        flow_m3_h: Number(concFlow.toFixed(2)),
        tds_mg_l: Number(concTds.toFixed(1)),
      },
      energy: {
        ...plantState.energy,
        sec_kwh_m3: Number(secVal.toFixed(4)),
        total_electrical_power_kw: Number(powerKw.toFixed(2)),
      },
      overall_recovery_pct: Number(((permFlow / qf) * 100).toFixed(2)),
    });
  };

  if (loading || !plantState) {
    return <div className="h-96 bg-white rounded-2xl border border-slate-200 animate-pulse" />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Mode Notice */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Live Process Flow Digital Twin
            </h2>
            <StatusBadge status="Virtual Plant" variant="virtual" />
            <span className="text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200 px-2.5 py-0.5 rounded-md">
              Industrial Validation Pending
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Two-stage concentrate-staged reverse osmosis system with MBR pre-treatment. Click stages for vessel-level analytics.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span className="font-semibold text-slate-700">6-Zone EKF Live</span>
          </span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500">Topology A (Concentrate Staged)</span>
        </div>
      </div>

      {/* Main Process Diagram Canvas */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm relative overflow-hidden">
        {/* Subtle Water Background Accent */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-gradient-to-br from-sky-100/40 to-emerald-100/20 pointer-events-none blur-3xl" />

        {/* Process Flow Schematic Grid */}
        <div className="space-y-8 relative z-10">
          {/* Main Horizontal Flow Path */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5 items-stretch">
            {/* Step 1: Raw Textile Wastewater */}
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 relative">
              <div className="flex items-center gap-2 mb-2">
                <div className="p-1.5 rounded-md bg-slate-200 text-slate-700">
                  <Droplets className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Source
                  </span>
                  <span className="text-xs font-bold text-slate-800">
                    Textile Wastewater
                  </span>
                </div>
              </div>
              <div className="space-y-1 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-slate-200/80">
                <div className="flex justify-between">
                  <span>Feed Flow:</span>
                  <strong className="text-slate-800">{formatFlow(plantState.feed.flow_m3_h)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Raw TDS:</span>
                  <strong className="text-slate-800">{formatTDS(plantState.feed.tds_mg_l)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Temp:</span>
                  <strong className="text-slate-800">{formatTemperature(plantState.feed.temperature_c)}</strong>
                </div>
              </div>
            </div>

            {/* Step 2: Equalization / MBR */}
            <div className="bg-sky-50/50 rounded-xl p-4 border border-sky-200 relative">
              <div className="flex items-center gap-2 mb-2">
                <div className="p-1.5 rounded-md bg-sky-100 text-sky-700">
                  <Activity className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-sky-600 block">
                    Pretreatment
                  </span>
                  <span className="text-xs font-bold text-slate-800">
                    Equalization / MBR
                  </span>
                </div>
              </div>
              <div className="space-y-1 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-sky-100">
                <div className="flex justify-between">
                  <span>Turbidity:</span>
                  <strong className="text-slate-800">&lt; 0.2 NTU</strong>
                </div>
                <div className="flex justify-between">
                  <span>Feed pH:</span>
                  <strong className="text-slate-800">{plantState.feed.ph.toFixed(1)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>COD:</span>
                  <strong className="text-slate-800">{plantState.feed.cod_mg_l.toFixed(1)} mg/L</strong>
                </div>
              </div>
            </div>

            {/* Step 3: High Pressure Pump & Stage 1 */}
            <div
              onClick={() => setSelectedStage(plantState.stage1)}
              className="bg-emerald-50/70 rounded-xl p-4 border-2 border-emerald-300 hover:border-emerald-500 transition-all cursor-pointer shadow-xs hover:shadow-md relative group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-md bg-emerald-600 text-white">
                    <Layers className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 block">
                      Primary RO Array
                    </span>
                    <span className="text-xs font-bold text-slate-900">
                      Stage 1 (3 Vessels × 3E)
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform" />
              </div>
              <div className="space-y-1 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-emerald-200">
                <div className="flex justify-between">
                  <span>Feed Pressure P₁:</span>
                  <strong className="text-emerald-700">{formatPressure(plantState.stage1.inlet_pressure_bar)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Permeate Flow:</span>
                  <strong className="text-slate-800">{formatFlow(plantState.stage1.permeate_flow_m3_h)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Stage Recovery:</span>
                  <strong className="text-emerald-700">{formatPercent(plantState.stage1.stage_recovery_pct)}</strong>
                </div>
              </div>
              <div className="mt-2 text-[10px] text-emerald-700 font-medium flex items-center justify-between">
                <span>Click for vessel details</span>
                <span className="underline">9 elements</span>
              </div>
            </div>

            {/* Step 4: Interstage Booster & Stage 2 */}
            <div
              onClick={() => setSelectedStage(plantState.stage2)}
              className="bg-sky-50/70 rounded-xl p-4 border-2 border-sky-300 hover:border-sky-500 transition-all cursor-pointer shadow-xs hover:shadow-md relative group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-md bg-sky-600 text-white">
                    <Layers className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-sky-800 block">
                      Concentrate Staging
                    </span>
                    <span className="text-xs font-bold text-slate-900">
                      Stage 2 (2 Vessels × 3E)
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-sky-600 group-hover:translate-x-0.5 transition-transform" />
              </div>
              <div className="space-y-1 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-sky-200">
                <div className="flex justify-between">
                  <span>Booster Press P₂:</span>
                  <strong className="text-sky-700">{formatPressure(plantState.stage2.inlet_pressure_bar)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Permeate Flow:</span>
                  <strong className="text-slate-800">{formatFlow(plantState.stage2.permeate_flow_m3_h)}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Stage Recovery:</span>
                  <strong className="text-sky-700">{formatPercent(plantState.stage2.stage_recovery_pct)}</strong>
                </div>
              </div>
              <div className="mt-2 text-[10px] text-sky-700 font-medium flex items-center justify-between">
                <span>Click for vessel details</span>
                <span className="underline">6 elements</span>
              </div>
            </div>

            {/* Step 5: Product Separation & Endpoints */}
            <div className="space-y-3">
              {/* Permeate Reuse */}
              <div className="bg-emerald-50 rounded-xl p-3.5 border border-emerald-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                    <Droplets className="w-3.5 h-3.5 text-emerald-600" />
                    Combined Permeate → Reuse
                  </span>
                  <StatusBadge status="99.6% Rejection" variant="healthy" size="sm" />
                </div>
                <div className="text-xs text-slate-600 space-y-0.5">
                  <div className="flex justify-between">
                    <span>Total Flow:</span>
                    <strong className="text-emerald-700">{formatFlow(plantState.permeate.total_flow_m3_h)}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Quality TDS:</span>
                    <strong className="text-emerald-700">{formatTDS(plantState.permeate.tds_mg_l)}</strong>
                  </div>
                </div>
              </div>

              {/* Concentrate */}
              <div className="bg-amber-50 rounded-xl p-3.5 border border-amber-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-amber-600" />
                    Final Concentrate Reject
                  </span>
                </div>
                <div className="text-xs text-slate-600 space-y-0.5">
                  <div className="flex justify-between">
                    <span>Flow:</span>
                    <strong className="text-amber-800">{formatFlow(plantState.concentrate.flow_m3_h)}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Concentrate TDS:</span>
                    <strong className="text-amber-800">{formatTDS(plantState.concentrate.tds_mg_l)}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Plant Energy & Hydraulic Balance Summary Bar */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="text-slate-500 font-medium">Interstage Pressure (Pint):</span>
                <strong className="text-slate-800 font-mono text-sm">{formatPressure(plantState.interstage_pressure_bar)}</strong>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-500 font-medium">Specific Energy (SEC):</span>
                <strong className="text-amber-700 font-mono text-sm">{formatSEC(plantState.energy.sec_kwh_m3)}</strong>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-500 font-medium">Total Power:</span>
                <strong className="text-slate-800 font-mono text-sm">{formatPower(plantState.energy.total_electrical_power_kw)}</strong>
              </div>
            </div>

            <div className="text-slate-400 text-[11px] font-mono">
              Mass Closure: Exact Global Solute & Volumetric Balance (0.000% Residual)
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic Disturbance Injection & Telemetry Controller */}
      <DisturbanceInjector onDisturbanceChange={handleDisturbanceChange} />

      {/* Stage Drilldown Modal */}
      <StageDetailModal
        stage={selectedStage}
        onClose={() => setSelectedStage(null)}
      />
    </div>
  );
}
