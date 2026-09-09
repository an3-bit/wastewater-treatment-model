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
  ArrowUpRight,
  FileText,
  AlertTriangle,
  Coins,
  Wrench,
} from 'lucide-react';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Timeline } from '@/components/common/Timeline';
import { ReportExportModal } from '@/components/common/ReportExportModal';
import { digitalTwinService } from '@/services/digitalTwinService';
import { economicsApi } from '@/services/api/economics';
import { maintenanceApi } from '@/services/api/maintenance';
import { PlantState, DigitalTwinStatus } from '@/types/digitalTwin';
import { EconomicSummaryResponse, MaintenanceRecommendationResponse } from '@/types/api';
import { formatFlow, formatTDS, formatPressure, formatSEC, formatPower, formatPercent } from '@/utils/formatters';
import Link from 'next/link';

export default function OverviewPage() {
  const [plantState, setPlantState] = useState<PlantState | null>(null);
  const [twinStatus, setTwinStatus] = useState<DigitalTwinStatus | null>(null);
  const [econSummary, setEconSummary] = useState<EconomicSummaryResponse | null>(null);
  const [maintRec, setMaintRec] = useState<MaintenanceRecommendationResponse | null>(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setErrorMsg(null);
        const [state, status, econ, maint] = await Promise.all([
          digitalTwinService.getPlantState(),
          digitalTwinService.getDigitalTwinStatus(),
          economicsApi.getSummary().catch(() => null),
          maintenanceApi.getRecommendation().catch(() => null),
        ]);
        setPlantState(state);
        setTwinStatus(status);
        setEconSummary(econ);
        setMaintRec(maint);
      } catch (err) {
        console.error('Failed to load overview data:', err);
        setErrorMsg('FastAPI backend connection degraded. Showing local fallback cache.');
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 rounded-xl" />
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
            <span className="text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200 px-2.5 py-0.5 rounded-md">
              Industrial Validation Pending
            </span>
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
            <span>Stage 7 6-Zone EKF Active (RMSE &lt; 0.36% Rₘ)</span>
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="font-semibold underline hover:text-amber-900"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Top KPI Cards (6 Key Indicators in 2x3 Spacious Grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <MetricCard
          title="Water Recovery"
          value={formatPercent(plantState.overall_recovery_pct)}
          icon={Droplets}
          accentColor="emerald"
          tooltipTerm="Water Recovery"
          customTooltip="Percentage of total feed water converted into reusable permeate product."
          trend={{
            value: econSummary ? `+${econSummary.water.water_increase_pct.toFixed(1)}%` : '+68.1%',
            isPositive: true,
            label: 'water impact',
          }}
        />

        <MetricCard
          title="Current SEC"
          value={plantState.energy.sec_kwh_m3.toFixed(4)}
          unit="kWh/m³"
          icon={Zap}
          accentColor="amber"
          tooltipTerm="SEC"
          trend={{
            value: econSummary ? `-${econSummary.energy.sec_reduction_pct.toFixed(2)}%` : '-6.19%',
            isPositive: true,
            label: 'SEC reduction',
          }}
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
          subtitle="Target: <100 mg/L"
          trend={{ value: `${plantState.permeate.salt_rejection_pct.toFixed(1)}%`, isPositive: true, label: 'rejection' }}
        />

        <MetricCard
          title="Membrane Health"
          value={plantState.overall_recovery_pct > 50 ? 'Healthy (91.5%)' : 'Fouling Warning'}
          icon={Layers}
          accentColor="emerald"
          tooltipTerm="Rf"
          subtitle="6-Zone EKF Converged"
          badge={<StatusBadge status="95% Confidence" variant="healthy" size="sm" />}
        />

        <MetricCard
          title="Total Power"
          value={formatPower(plantState.energy.total_electrical_power_kw)}
          icon={Gauge}
          accentColor="amber"
          subtitle="Pump η = 75%"
          trend={{
            value: econSummary ? `+${econSummary.energy.total_electricity_change_pct.toFixed(1)}%` : '+57.7%',
            isPositive: false,
            label: 'total kWh/yr (due to +68% water)',
          }}
        />
      </div>

      {/* Second Row: Stage 8C Economics & Maintenance Advisor Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Techno-Economic Value Banner (2 Cols) */}
        <div className="lg:col-span-2 bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-6 border border-slate-700 text-white shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between gap-4 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Coins className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Stage 8C Authoritative Techno-Economic Study
                  </span>
                </div>
                <h3 className="text-2xl font-bold tracking-tight text-white">
                  Integrated Net Value: KES {econSummary ? econSummary.economics.integrated_framework_value_kes_year.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '4,391,948.14'} / year
                </h3>
                <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                  Predictive supervisory optimization unlocks <strong className="text-emerald-300">+44,458 m³/yr (+68.10%)</strong> additional textile wastewater reuse while reducing treatment specific energy by <strong className="text-amber-300">-6.19%</strong>.
                </p>
              </div>

              <Link
                href="/dashboard/optimization"
                className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 hover:text-emerald-300 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors shrink-0"
              >
                <span>Value Waterfall</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Economic Sub-Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/80">
                <span className="text-[11px] font-medium text-slate-400 block">Pure Prediction (D-C)</span>
                <span className="text-base font-bold text-emerald-400">
                  KES {econSummary ? (econSummary.economics.prediction_value_kes_year / 1000).toFixed(1) : '424.2'}k
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">9.66% of total value</span>
              </div>

              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/80">
                <span className="text-[11px] font-medium text-slate-400 block">Condition Monitoring (C-B)</span>
                <span className="text-base font-bold text-emerald-400">
                  KES {econSummary ? (econSummary.economics.condition_based_value_kes_year / 1000000).toFixed(2) : '3.90'}M
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">88.86% of total value</span>
              </div>

              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/80">
                <span className="text-[11px] font-medium text-slate-400 block">Dynamic Pressure MPC</span>
                <span className="text-base font-bold text-amber-400">
                  KES {econSummary ? econSummary.economics.mpc_value_kes_year.toFixed(0) : '2,782'}
                </span>
                <span className="text-[10px] text-amber-400/80 block mt-0.5">0.06% (Marginal Trim)</span>
              </div>

              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/80">
                <span className="text-[11px] font-medium text-slate-400 block">Treatment LCOW</span>
                <span className="text-base font-bold text-sky-400">
                  KES {econSummary ? econSummary.economics.treatment_lcow_kes_m3.toFixed(2) : '23.20'} / m³
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">vs 120 KES tariff</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-700/80 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
            <span>Authoritative Scenario: <strong className="text-white">Base (100% Reuse, 1.0x CIP, 4h Downtime)</strong></span>
            <span className="text-[11px] font-mono text-slate-400">Stage 8C Authoritative Results Freeze</span>
          </div>
        </div>

        {/* Predictive Maintenance Decision Card */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <Wrench className="w-4 h-4 text-indigo-600" />
                Maintenance Decision Advisor
              </h3>
              <StatusBadge
                status={maintRec?.recommended_action || 'CONTINUE'}
                variant={maintRec?.recommended_action === 'CLEAN' ? 'severe' : 'healthy'}
                size="sm"
              />
            </div>

            <div className="space-y-3 mt-4">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[11px] font-medium text-slate-500 block">Advisor Recommendation</span>
                <strong className="text-sm text-slate-900 block mt-0.5">
                  {maintRec?.recommended_action === 'CONTINUE' ? 'Continue Normal Operation' : (maintRec?.recommended_action === 'CLEAN' ? 'Execute Proactive CIP Cleaning' : 'Monitor Permeability Drop')}
                </strong>
                <p className="text-xs text-slate-600 mt-1">
                  {maintRec?.primary_rationale || 'Membrane resistance within normal operating envelope.'}
                </p>
              </div>

              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-600 font-medium">Time Since Last CIP:</span>
                <span className="font-semibold text-slate-800">
                  {maintRec?.time_since_last_CIP_h.toFixed(1) || '48.0'} hours
                </span>
              </div>

              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <span className="text-slate-600 font-medium">Lockout Enforcement:</span>
                <span className="font-semibold text-emerald-700">
                  {maintRec?.lockout_active ? `Active (${maintRec.next_eligible_cleaning_time_h.toFixed(1)}h remaining)` : 'Inactive (Eligible)'}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
            <span>Role: <strong>Operator Decision Support</strong></span>
            <span>Horizon: <strong>24h Standard</strong></span>
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
