import React from 'react';
import { EKFEstimatorStatus } from '@/types/membrane';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Cpu, CheckCircle2, ShieldCheck, Activity, HelpCircle } from 'lucide-react';
import { EngineeringTooltip } from '@/components/common/EngineeringTooltip';

interface EKFStatusPanelProps {
  status: EKFEstimatorStatus;
}

export function EKFStatusPanel({ status }: EKFStatusPanelProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-emerald-50 text-emerald-700">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-1.5">
              Extended Kalman Filter (EKF) State Estimator
              <EngineeringTooltip term="EKF" />
            </h3>
            <p className="text-xs text-slate-500">
              Stage 7 Physics-Informed Nonlinear Virtual Sensor
            </p>
          </div>
        </div>

        <StatusBadge status={status.filter_status} variant="healthy" />
      </div>

      {/* Estimator Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            State Dim (n)
          </span>
          <span className="text-lg font-bold font-mono text-slate-800">
            {status.state_dimension} Zones
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Axial Model B</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Cycle Latency
          </span>
          <span className="text-lg font-bold font-mono text-emerald-700">
            ~{status.update_latency_ms.toFixed(1)} ms
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Real-time capable</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Sensor Suite
          </span>
          <span className="text-sm font-bold text-slate-800 line-clamp-1">
            Standard 10-Skid
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Case 2 Optimal</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Estimation RMSE
          </span>
          <span className="text-sm font-bold font-mono text-emerald-700">
            {status.global_estimation_rmse_m_inv}
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Fouling resistance</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Decline MAE
          </span>
          <span className="text-lg font-bold font-mono text-emerald-700">
            {status.decline_mae_pct.toFixed(3)}%
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Permeability error</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
            Innovation / NIS
          </span>
          <span className="text-xs font-bold text-sky-700 block mt-1">
            {status.innovation_nis_status}
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">95% confidence</span>
        </div>
      </div>

      {/* Physics Decoupling Note */}
      <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
        <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="font-semibold text-slate-800">Disturbance Rejection Verification:</strong> The estimator processes feed salinity and flow shock pulses through the nonlinear observation operator h(x, u) as osmotic and viscosity perturbations, preventing spurious fouling state jumps.
        </div>
      </div>
    </div>
  );
}
