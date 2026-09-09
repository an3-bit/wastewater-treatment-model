'use client';

import React, { useEffect, useState } from 'react';
import {
  Droplets,
  Zap,
  Gauge,
  Activity,
  Layers,
  ShieldCheck,
  CheckCircle2,
  Cpu,
  TrendingDown,
  ArrowUpRight,
  FileText,
} from 'lucide-react';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Timeline } from '@/components/common/Timeline';
import { EngineeringTooltip } from '@/components/common/EngineeringTooltip';
import { ReportExportModal } from '@/components/common/ReportExportModal';
import { digitalTwinService } from '@/services/digitalTwinService';
import { PlantState, DigitalTwinStatus } from '@/types/digitalTwin';
import { formatFlow, formatTDS, formatPressure, formatSEC, formatPower, formatPercent } from '@/utils/formatters';
import Link from 'next/link';

export default function OverviewPage() {
  const [plantState, setPlantState] = useState<PlantState | null>(null);
  const [twinStatus, setTwinStatus] = useState<DigitalTwinStatus | null>(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [state, status] = await Promise.all([
          digitalTwinService.getPlantState(),
          digitalTwinService.getDigitalTwinStatus(),
        ]);
        setPlantState(state);
        setTwinStatus(status);
      } catch (err) {
        console.error('Failed to load overview data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !plantState || !twinStatus) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-200 rounded w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Title & Research Notice Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Executive Digital Twin Overview
            </h2>
            <StatusBadge status="Virtual Plant" variant="virtual" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time physics-informed monitoring and supervisory decision metrics for 2-stage MBR–RO.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setReportOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-xs transition-all active:scale-95"
          >
            <FileText className="w-3.5 h-3.5 text-sky-400" />
            <span>Export Dossier</span>
          </button>

          <div className="hidden sm:flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg text-xs text-emerald-800">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Stage 7 Virtual Sensor Active (RMSE &lt; 0.36% Rₘ)</span>
          </div>
        </div>
      </div>

      {/* Top KPI Cards (6 Key Indicators in 2x3 Spacious Grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <MetricCard
          title="Water Recovery"
          value={formatPercent(plantState.overall_recovery_pct)}
          icon={Droplets}
          accentColor="emerald"
          tooltipTerm="Water Recovery"
          customTooltip="Percentage of total feed water converted into reusable permeate product."
          trend={{ value: '+0.86%', isPositive: true, label: 'vs baseline' }}
        />

        <MetricCard
          title="Current SEC"
          value={plantState.energy.sec_kwh_m3.toFixed(4)}
          unit="kWh/m³"
          icon={Zap}
          accentColor="amber"
          tooltipTerm="SEC"
          trend={{ value: '-5.72%', isPositive: true, label: 'reduction' }}
        />

        <MetricCard
          title="Permeate Flow"
          value={formatFlow(plantState.permeate.total_flow_m3_h)}
          icon={Activity}
          accentColor="sky"
          subtitle={`Feed: ${formatFlow(plantState.feed.flow_m3_h)}`}
        />

        <MetricCard
          title="Permeate TDS"
          value={formatTDS(plantState.permeate.tds_mg_l)}
          icon={Droplets}
          accentColor="sky"
          subtitle="Ref target: <18.0 mg/L"
          trend={{ value: '99.65%', isPositive: true, label: 'rejection' }}
        />

        <MetricCard
          title="Membrane Health"
          value="Healthy"
          icon={Layers}
          accentColor="emerald"
          tooltipTerm="Rf"
          subtitle="6-Zone EKF Converged"
          badge={<StatusBadge status="97.2% Confidence" variant="healthy" size="sm" />}
        />

        <MetricCard
          title="Total Power"
          value={formatPower(plantState.energy.total_electrical_power_kw)}
          icon={Gauge}
          accentColor="amber"
          subtitle="Pump η = 80%"
        />
      </div>

      {/* Second Row: Strategy Card & Digital Twin Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Operating Strategy Card (2 Columns wide) */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Active Operating Strategy
                  </span>
                  <StatusBadge status="PARETO OPTIMAL" variant="pareto" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">
                  {plantState.current_strategy_name}
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Multi-objective compromise strategy derived via Stage 5 NSGA-II optimization. Dominates original industrial baseline with lower energy and lower peak membrane stress.
                </p>
              </div>

              <Link
                href="/dashboard/optimization"
                className="inline-flex items-center gap-1 text-xs font-semibold text-sky-600 hover:text-sky-700 bg-sky-50 px-3 py-1.5 rounded-lg border border-sky-200 transition-colors"
              >
                <span>View Pareto Front</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Strategy Parameters Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block">Stage 1 Pressure (P₁)</span>
                <span className="text-lg font-bold text-slate-800">{formatPressure(plantState.stage1.inlet_pressure_bar)}</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Pump discharge</span>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block">Stage 2 Pressure (P₂)</span>
                <span className="text-lg font-bold text-slate-800">{formatPressure(plantState.stage2.inlet_pressure_bar)}</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Interstage booster</span>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block">Water Recovery</span>
                <span className="text-lg font-bold text-emerald-700">{formatPercent(plantState.overall_recovery_pct)}</span>
                <span className="text-[10px] text-emerald-600 font-medium block mt-0.5">+0.86% over baseline</span>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block">Specific Energy (SEC)</span>
                <span className="text-lg font-bold text-amber-700">{formatSEC(plantState.energy.sec_kwh_m3)}</span>
                <span className="text-[10px] text-emerald-600 font-medium block mt-0.5">-5.72% energy saving</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
            <div className="flex items-center gap-4">
              <span>Peak Element Recovery: <strong className="text-slate-700">{formatPercent(plantState.max_element_recovery_pct)}</strong> (&le; 30% limit)</span>
              <span>Permeate TDS: <strong className="text-slate-700">{formatTDS(plantState.permeate.tds_mg_l)}</strong></span>
            </div>
            <span className="text-[11px] font-mono text-slate-400">Ground-truth verified against Model V2.0</span>
          </div>
        </div>

        {/* Digital Twin Status Card */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-sky-600" />
                Digital Twin Engine Status
              </h3>
              <StatusBadge status={twinStatus.data_source} variant="virtual" size="sm" />
            </div>

            <div className="space-y-3 mt-4">
              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-600 font-medium">Instrumentation Suite:</span>
                <span className="font-semibold text-emerald-700 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  10 Sensors Online
                </span>
              </div>

              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-600 font-medium">State Estimator:</span>
                <span className="font-semibold text-emerald-700 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  EKF 6-Zone Converged
                </span>
              </div>

              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-600 font-medium">Predictive Forecast:</span>
                <span className="font-semibold text-sky-700 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-500" />
                  Available (Horizon: 72h)
                </span>
              </div>

              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-600 font-medium">Physics Engine:</span>
                <span className="font-mono font-semibold text-slate-800">
                  {twinStatus.model_version}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
            <span>Cycle Latency: <strong>{twinStatus.latency_ms.toFixed(1)} ms</strong></span>
            <span>Update: <strong>Real-time</strong></span>
          </div>
        </div>
      </div>

      {/* Digital Twin Timeline Component */}
      <Timeline currentSimHour={plantState.simulation_time_hours} />

      {/* Report Export Dossier Modal */}
      <ReportExportModal
        isOpen={reportOpen}
        onClose={() => setReportOpen(false)}
        plantState={plantState}
      />
    </div>
  );
}
