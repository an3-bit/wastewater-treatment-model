'use client';

import React from 'react';
import Link from 'next/link';
import {
  Layers,
  Cpu,
  Activity,
  Sliders,
  Sparkles,
  FileSpreadsheet,
  ArrowRight,
  FlaskConical,
} from 'lucide-react';

const features = [
  {
    icon: Layers,
    title: 'First-Principles RO Hydraulics Solver',
    category: 'Stage 1 & 2 Hydraulics',
    tag: 'Mechanistic Core',
    description:
      'Element-by-element solution of Spiegler-Kedem transport, film theory concentration polarization (CP), and osmotic pressure gradients across 15 Toray TM720D-400 membrane elements.',
    metrics: '15 Elements • 3:2 Staging Array • Element-by-Element CP',
    link: '/dashboard/twin',
    iconBg: 'bg-sky-50 text-sky-600 border-sky-200',
    cardBorder: 'hover:border-sky-300',
  },
  {
    icon: Cpu,
    title: 'Physics-Reconstructed Neural Surrogate',
    category: 'Surrogate Machine Learning',
    tag: '1,218× Acceleration',
    description:
      'Multi-layer perceptron surrogate trained on Latin Hypercube parameter spaces. Incorporates exact algebraic mass balance reconstruction (Q_r = Q_f - Q_p) ensuring 0.000% solute drift.',
    metrics: '0.036 ms/eval • R² > 0.9998 • 0.000% Solute Residual',
    link: '/dashboard/scenarios',
    iconBg: 'bg-purple-50 text-purple-600 border-purple-200',
    cardBorder: 'hover:border-purple-300',
  },
  {
    icon: Activity,
    title: '6-Zone Axial Extended Kalman Filter (EKF)',
    category: 'Stage 7 State Estimation',
    tag: 'Virtual Sensing',
    description:
      'Non-invasive hidden state estimation tracking localized hydraulic fouling resistance (R_f) in real time from standard 10-sensor skid telemetry without taking pressure vessels offline.',
    metrics: 'n = 6 State Dimension • Converged P < 10⁻⁴ • 1.0s Telemetry',
    link: '/dashboard/membranes',
    iconBg: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    cardBorder: 'hover:border-emerald-300',
  },
  {
    icon: Sliders,
    title: 'NSGA-II Multi-Objective Pareto Frontier',
    category: 'Evolutionary Optimization',
    tag: 'Multi-Objective',
    description:
      'Non-dominated Sorting Genetic Algorithm II resolving non-convex trade-offs between Water Recovery (%), Specific Energy (kWh/m³), and Membrane Flux Longevity.',
    metrics: '50 Optimal Candidates • Strategy A/B/C/D Modes',
    link: '/dashboard/optimization',
    iconBg: 'bg-amber-50 text-amber-600 border-amber-200',
    cardBorder: 'hover:border-amber-300',
  },
  {
    icon: FlaskConical,
    title: 'Dynamic Chemical CIP Decision Advisor',
    category: 'Membrane Longevity',
    tag: 'CIP Optimization',
    description:
      'Simulate Alkaline, Acid, 2-Step, and Enzymatic Cleaning-In-Place protocols with physics-backed resistance restoration formulas and comprehensive chemical/energy downtime cost calculations.',
    metrics: '4 Protocols • 85-98% Clean Efficiency • Stage-Selective',
    link: '/dashboard/forecast',
    iconBg: 'bg-cyan-50 text-cyan-600 border-cyan-200',
    cardBorder: 'hover:border-cyan-300',
  },
  {
    icon: FileSpreadsheet,
    title: 'Executive Compliance Audit & Dossier Export',
    category: 'Regulatory Validation',
    tag: 'Print & Export',
    description:
      'Generate authoritative engineering dossiers with complete stream mass balance ledgers, 15-element staging matrices, and textile reuse standard compliance certificates.',
    metrics: 'One-Click Print/Export • TDS < 10 mg/L Certified',
    link: '/dashboard',
    iconBg: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    cardBorder: 'hover:border-indigo-300',
  },
];

export function FeaturesGrid() {
  return (
    <section id="features" className="py-20 bg-slate-50/80 text-slate-900 relative border-t border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 space-y-12">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-2xs">
            <Sparkles className="w-3.5 h-3.5 text-sky-600" />
            <span>Integrated Digital Twin Subsystems</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Engineered for Industrial Rigor and Maximum Water Recovery
          </h2>
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
            Every module is validated against literature standards, manufacturer performance specs, and dynamic chemical resistance kinetics.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, idx) => {
            const Icon = f.icon;
            return (
              <div
                key={idx}
                className={`p-7 rounded-3xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-all duration-200 group ${f.cardBorder}`}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center ${f.iconBg}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                      {f.tag}
                    </span>
                  </div>

                  <div>
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold block">
                      {f.category}
                    </span>
                    <h3 className="text-lg font-bold text-slate-900 mt-1 group-hover:text-sky-600 transition-colors">
                      {f.title}
                    </h3>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    {f.description}
                  </p>
                </div>

                <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-500 font-medium">
                    {f.metrics}
                  </span>
                  <Link
                    href={f.link}
                    className="p-2 rounded-xl bg-slate-50 hover:bg-sky-600 hover:text-white text-slate-600 border border-slate-200 transition-all"
                    title="Open module"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
