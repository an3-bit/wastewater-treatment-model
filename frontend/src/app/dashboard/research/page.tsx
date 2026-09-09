'use client';

import React from 'react';
import {
  BookOpen,
  CheckCircle2,
  Clock,
  ShieldAlert,
  Layers,
  Cpu,
  Sliders,
  TrendingUp,
  Activity,
  FileText,
  ExternalLink,
} from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { ModelAuditBench } from '@/components/charts/ModelAuditBench';
import { APP_CONFIG } from '@/utils/constants';

interface ResearchStage {
  stage: number;
  title: string;
  subtitle: string;
  status: 'Complete' | 'Next' | 'Future';
  description: string;
  icon: React.ElementType;
  deliverables: string[];
}

const researchStages: ResearchStage[] = [
  {
    stage: 1,
    title: 'Mechanistic RO Model V2.0',
    subtitle: 'First-Principles Solution-Diffusion & Film Theory',
    status: 'Complete',
    description:
      'Pressure-corrected coupled nonlinear equations for water flux (Jw), solute flux (Js), van \'t Hoff osmotic pressure, and concentration polarization.',
    icon: Layers,
    deliverables: ['RO_MODEL_VERSION = "2.0-pressure-corrected"', 'Toray TM720D-400 Calibration', 'Exact Mass Closure (0.000% residual)'],
  },
  {
    stage: 2,
    title: 'Industrial 15-Element Baseline',
    subtitle: 'Concentrate-Staging Array (3:2 Staging)',
    status: 'Complete',
    description:
      '3 vessels in Stage 1 (9 elements) and 2 vessels in Stage 2 (6 elements) totaling 15 elements (555 m² membrane area). Verified against industrial literature.',
    icon: Activity,
    deliverables: ['Topology A Concentrate Staging', 'P1 = 13 bar, P2 = 18 bar Baseline', 'Recovery: 69.36%, SEC: 0.771 kWh/m³'],
  },
  {
    stage: 3,
    title: 'Design of Experiments (DoE)',
    subtitle: 'Sobol Quasi-Random Domain Generation',
    status: 'Complete',
    description:
      'High-throughput parametric dataset spanning operating pressures, feed salinity, flow rate, and temperature for ML surrogate training.',
    icon: FileText,
    deliverables: ['Physics-reconstructed simulation dataset', 'OptimizationDomainGuard bounds', 'Multi-variate sensitivity envelopes'],
  },
  {
    stage: 4,
    title: 'ANN Surrogate Model',
    subtitle: 'Physics-Reconstructed High-Speed Inference',
    status: 'Complete',
    description:
      'Feed-forward neural network achieving 1,218× speedup (27,685 evaluations/sec) with strict physics reconstruction on mass balance outputs.',
    icon: Cpu,
    deliverables: ['R² > 0.999 fidelity on test splits', 'Sub-millisecond inference latency', 'Zero solute mass balance residual'],
  },
  {
    stage: 5,
    title: 'NSGA-II Multi-Objective Optimization',
    subtitle: 'Pareto Frontier Discovery across 5 Seeds',
    status: 'Complete',
    description:
      'Tri-objective evolutionary optimization maximizing recovery, minimizing SEC, and safeguarding peak single-element recovery below 30%.',
    icon: Sliders,
    deliverables: ['424 unique non-dominated Pareto solutions', 'Strategy D Balanced Knee identification', 'Proven dominance over industrial baseline'],
  },
  {
    stage: 6,
    title: 'Dynamic Membrane Fouling Model',
    subtitle: 'Mechanistic Cake-Layer & Pore-Blocking Kinetics',
    status: 'Complete',
    description:
      'Time-dependent evolution of hydraulic resistance (Rf) based on organic and particulate crossflow filtration kinetics.',
    icon: TrendingUp,
    deliverables: ['Axial lead-to-tail fouling rate dynamics', 'Temperature-corrected water viscosity', 'Critical flux threshold boundaries'],
  },
  {
    stage: 7,
    title: 'Hidden-State Estimation & Virtual Sensor',
    subtitle: 'Extended Kalman Filter (EKF) & Forecasting',
    status: 'Complete',
    description:
      'Continuous reconstruction of unmeasured 6-zone axial fouling states from standard 10-sensor skid telemetry with remaining-time threshold forecasting.',
    icon: ShieldAlert,
    deliverables: ['EKF estimation RMSE < 0.36% Rm', 'Convergence in 11.0 h, latency ~105 ms', 't5, t10, t15 Analysis Threshold forecasting'],
  },
  {
    stage: 8,
    title: 'Supervisory Decision Optimization',
    subtitle: 'Fouling-Aware Closed-Loop Setpoint Advisory',
    status: 'Next',
    description:
      'Dynamic supervisory setpoint scheduling and optimal cleaning cycle decision support coupling the EKF virtual sensor with real-time NSGA-II re-optimization.',
    icon: Clock,
    deliverables: ['Adaptive pressure trajectory governor', 'CIP schedule optimization', 'Operator recommendation API'],
  },
];

export default function ResearchPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Research Pipeline & Development Roadmap
            </h2>
            <StatusBadge status="Stages 1–8 Roadmap" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Overview of the 8-stage scientific methodology powering the WaterTwin AI digital twin.
          </p>
        </div>

        <div className="text-xs text-slate-500 font-mono bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg">
          Authoritative Engine: Model V2.0 Corrected
        </div>
      </div>

      {/* Prominent Mandatory Scientific Disclaimer */}
      <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-5 sm:p-6 text-amber-950 shadow-xs space-y-2">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-amber-900">
            Mandatory Scientific Notice & Framework Classification
          </h3>
        </div>
        <p className="text-xs leading-relaxed text-amber-900">
          {APP_CONFIG.DISCLAIMER}
        </p>
        <p className="text-[11px] text-amber-800 pt-1 border-t border-amber-200">
          This system represents a simulation-derived research twin. The 3:2 vessel staging array and baseline parameters are model-derived configurations calibrated against published literature (Sowgath et al., 2025). The EKF virtual sensor operates on a 6-zone axial state representation. Analysis thresholds (t₅, t₁₀, t₁₅) are scientific evaluation milestones, not automated CIP triggers.
        </p>
      </div>

      {/* Stage 4/5 Surrogate vs Mechanistic Ground Truth Parity Matrix */}
      <ModelAuditBench />

      {/* Stages 1 to 8 Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {researchStages.map((stage) => {
          const Icon = stage.icon;
          const isComplete = stage.status === 'Complete';
          const isNext = stage.status === 'Next';

          return (
            <div
              key={stage.stage}
              className={`rounded-2xl p-6 border shadow-xs transition-all flex flex-col justify-between ${
                isComplete
                  ? 'bg-white border-slate-200 hover:border-slate-300'
                  : isNext
                  ? 'bg-indigo-50/40 border-2 border-indigo-400 shadow-md ring-2 ring-indigo-100'
                  : 'bg-slate-50 border-slate-200'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2.5">
                    <div
                      className={`p-2 rounded-xl ${
                        isComplete
                          ? 'bg-emerald-50 text-emerald-700'
                          : isNext
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-200 text-slate-600'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                        Stage {stage.stage}
                      </span>
                      <h4 className="text-base font-bold text-slate-900">{stage.title}</h4>
                    </div>
                  </div>

                  <StatusBadge
                    status={stage.status}
                    variant={isComplete ? 'healthy' : isNext ? 'virtual' : 'neutral'}
                  />
                </div>

                <div className="text-xs font-semibold text-sky-700 mb-2">{stage.subtitle}</div>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">{stage.description}</p>
              </div>

              <div className="pt-3 border-t border-slate-100 space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Key Research Deliverables
                </span>
                <ul className="space-y-1 text-xs text-slate-700">
                  {stage.deliverables.map((del, dIdx) => (
                    <li key={dIdx} className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{del}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
