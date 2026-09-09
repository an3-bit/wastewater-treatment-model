'use client';

import React from 'react';
import {
  CheckCircle2,
  XCircle,
  TrendingUp,
  ArrowRight,
} from 'lucide-react';
import Link from 'next/link';

interface BenchmarkRow {
  parameter: string;
  traditional: string;
  digitalTwin: string;
  benefit: string;
}

const comparisonRows: BenchmarkRow[] = [
  {
    parameter: 'Water Recovery Rate',
    traditional: '60% – 65% (Conservative fixed setpoint)',
    digitalTwin: '70.22% – 75.10% (Pareto optimized)',
    benefit: '+10.2% water yield, reducing fresh intake demand',
  },
  {
    parameter: 'Specific Energy Consumption (SEC)',
    traditional: '0.95 – 1.15 kWh/m³ (Excessive throttling)',
    digitalTwin: '0.727 kWh/m³ (Dynamic booster staging)',
    benefit: '23.5% energy savings under peak hydraulic load',
  },
  {
    parameter: 'Fouling Awareness & Visibility',
    traditional: 'Blind total skid differential pressure (dP)',
    digitalTwin: '6-Zone Axial EKF Virtual Sensing (Rf local)',
    benefit: 'Pinpoints fouling in lead vs tail vessels non-invasively',
  },
  {
    parameter: 'Cleaning (CIP) Trigger Mechanism',
    traditional: 'Calendar-based or reactive after irreversible scaling',
    digitalTwin: 'Proactive Dynamic Fouling Kinetics (t5, t10, t15)',
    benefit: '34.5 h advance warning before irreversible compaction',
  },
  {
    parameter: 'Simulation & Optimization Speed',
    traditional: '44 ms / eval (Mechanistic PDE solver only)',
    digitalTwin: '0.036 ms / eval (1,218× ANN Surrogate)',
    benefit: 'Real-time NSGA-II genetic evolutionary optimization',
  },
  {
    parameter: 'Mass Conservation Verification',
    traditional: 'Black-box neural approximations drift over time',
    digitalTwin: 'Strict Physics Reconstruction (0.000% residual)',
    benefit: 'Zero drift in concentrate solute and recovery metrics',
  },
];

export function BenchmarkComparison() {
  return (
    <section id="benchmarks" className="py-20 bg-slate-50/90 text-slate-900 relative border-t border-slate-200/80">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 space-y-12">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-2xs">
            <TrendingUp className="w-3.5 h-3.5 text-sky-600" />
            <span>Industrial Literature vs AI Digital Twin</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Quantifiable Operational Advantages
          </h2>
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
            Side-by-side performance comparison against conventional static Reverse Osmosis control frameworks.
          </p>
        </div>

        {/* Clean Light Comparison Table */}
        <div className="rounded-3xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm border-collapse">
              <thead>
                <tr className="bg-slate-50/90 text-slate-600 font-bold border-b border-slate-200 text-xs uppercase tracking-wider">
                  <th className="py-4 px-6">Performance Parameter</th>
                  <th className="py-4 px-6 text-rose-800">Conventional Static Skid</th>
                  <th className="py-4 px-6 text-sky-800">AquaTwin RO™ Digital Twin</th>
                  <th className="py-4 px-6 text-emerald-800">Industrial Advantage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {comparisonRows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-bold text-slate-900 whitespace-nowrap">
                      {row.parameter}
                    </td>
                    <td className="py-4 px-6 text-slate-500">
                      <div className="flex items-center gap-2">
                        <XCircle className="w-4 h-4 text-rose-500 shrink-0" />
                        <span>{row.traditional}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-sky-900 font-semibold">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-sky-600 shrink-0" />
                        <span>{row.digitalTwin}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-emerald-700 font-mono text-xs font-semibold">
                      {row.benefit}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Clean Callout Banner */}
        <div className="p-8 rounded-3xl bg-gradient-to-r from-sky-50 via-indigo-50/60 to-white border border-sky-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-1">
            <h4 className="text-lg font-bold text-slate-900">
              Ready to explore the live digital twin control center?
            </h4>
            <p className="text-xs sm:text-sm text-slate-600">
              Sign in with your plant role or launch the instant guest evaluation demo.
            </p>
          </div>

          <Link
            href="/dashboard"
            className="bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-bold px-7 py-3.5 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 self-start sm:self-auto shrink-0"
          >
            <span>Launch Digital Twin Now</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

      </div>
    </section>
  );
}
