'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  Droplets,
  Zap,
  ShieldCheck,
  Cpu,
  Layers,
  Activity,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Gauge,
} from 'lucide-react';

interface HeroSectionProps {
  onOpenSignIn: () => void;
}

export function HeroSection({ onOpenSignIn }: HeroSectionProps) {
  const [activeTab, setActiveTab] = useState<'pid' | 'ekf' | 'pareto'>('pid');

  return (
    <section id="overview" className="relative pt-12 pb-20 overflow-hidden bg-gradient-to-b from-slate-50 via-sky-50/30 to-white text-slate-900">
      {/* Background Soft Glow Accents */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[450px] bg-gradient-to-b from-sky-200/40 via-indigo-100/20 to-transparent blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 relative z-10 space-y-12">
        
        {/* Main Title & Value Proposition */}
        <div className="text-center max-w-4xl mx-auto space-y-6">
          
          {/* Top Pill Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-sky-200 text-xs font-semibold text-sky-800 shadow-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>AI-Enabled Stage 7 Digital Twin Framework</span>
            <span className="text-slate-300">•</span>
            <span className="text-slate-600 font-mono">Toray TM720D-400 (3:2 Staging)</span>
          </div>

          {/* Large Clean Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-slate-900 leading-[1.1]">
            Autonomous AI Digital Twin for <br />
            <span className="bg-gradient-to-r from-sky-600 via-indigo-600 to-cyan-600 bg-clip-text text-transparent">
              Industrial Wastewater Reuse
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
            A first-principles industrial digital twin integrating 3:2 staging hydraulics, 6-zone Extended Kalman Filter (EKF) virtual sensing, and NSGA-II multi-objective optimization for zero-liquid discharge textile operations.
          </p>

          {/* Hero CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <button
              onClick={onOpenSignIn}
              className="w-full sm:w-auto bg-gradient-to-r from-sky-600 via-indigo-600 to-sky-700 hover:from-sky-500 hover:to-indigo-500 text-white font-bold text-sm px-8 py-4 rounded-2xl shadow-lg shadow-sky-600/20 hover:shadow-xl transition-all flex items-center justify-center gap-2 group"
            >
              <span>Sign In with Operator Role</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <Link
              href="/dashboard"
              className="w-full sm:w-auto bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm px-8 py-4 rounded-2xl border border-slate-300 hover:border-slate-400 transition-all flex items-center justify-center gap-2 shadow-xs"
            >
              <Sparkles className="w-4 h-4 text-sky-600" />
              <span>Launch Live Control Center</span>
            </Link>
          </div>

          {/* Verification Highlights */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 pt-1 font-medium">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Preloaded Industrial Datasets
            </span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-sky-600" />
              Stage 7 EKF Observability Proven
            </span>
            <span className="flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-purple-600" />
              0.036 ms/eval Neural Surrogate
            </span>
          </div>
        </div>

        {/* 4 Core Quantitative Proof Cards (Light Aesthetic) */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-1 hover:border-sky-300 hover:shadow-sm transition-all">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
              <span>Water Recovery</span>
              <Droplets className="w-4 h-4 text-sky-600" />
            </div>
            <div className="text-3xl sm:text-4xl font-black text-slate-900">70.22%</div>
            <p className="text-[11px] text-slate-500">Meets &ge;70% reuse standard</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-1 hover:border-emerald-300 hover:shadow-sm transition-all">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
              <span>Specific Energy (SEC)</span>
              <Zap className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-3xl sm:text-4xl font-black text-emerald-700">
              0.727 <span className="text-sm font-semibold text-slate-500">kWh/m³</span>
            </div>
            <p className="text-[11px] text-slate-500">Optimized booster pump power</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-1 hover:border-purple-300 hover:shadow-sm transition-all">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
              <span>ANN Surrogate</span>
              <Cpu className="w-4 h-4 text-purple-600" />
            </div>
            <div className="text-3xl sm:text-4xl font-black text-purple-700">1,218×</div>
            <p className="text-[11px] text-slate-500">27,685 evals/sec speedup</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-1 hover:border-indigo-300 hover:shadow-sm transition-all">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
              <span>Mass Residual</span>
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="text-3xl sm:text-4xl font-black text-indigo-700">0.000%</div>
            <p className="text-[11px] text-slate-500">Analytical mass conservation</p>
          </div>
        </div>

        {/* Hero RO Skid Visual Showcase Card (Embeds Generated Photo + Live Telemetry) */}
        <div className="rounded-3xl border border-slate-200/90 bg-white shadow-xl overflow-hidden">
          
          {/* Header Bar */}
          <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-500 ring-4 ring-emerald-100 animate-pulse" />
              <div>
                <span className="text-xs font-bold text-slate-900 block">
                  Industrial Reverse Osmosis Skid Alpha-1 (Live Pilot Skid)
                </span>
                <span className="text-[11px] text-slate-500 font-mono">
                  3:2 Staging Configuration • 15 Toray TM720D-400 Elements
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 text-xs font-medium self-start sm:self-auto shadow-2xs">
              <button
                onClick={() => setActiveTab('pid')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeTab === 'pid'
                    ? 'bg-sky-600 text-white font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Pilot Plant View
              </button>
              <button
                onClick={() => setActiveTab('ekf')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeTab === 'ekf'
                    ? 'bg-sky-600 text-white font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                6-Zone EKF Matrix
              </button>
              <button
                onClick={() => setActiveTab('pareto')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeTab === 'pareto'
                    ? 'bg-sky-600 text-white font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                NSGA-II Frontier
              </button>
            </div>
          </div>

          {/* Main Visual Showcase Content */}
          <div className="p-6 sm:p-8 space-y-6">
            {activeTab === 'pid' && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                {/* Left: Generated Photorealistic Industrial Image */}
                <div className="lg:col-span-7 relative rounded-2xl overflow-hidden border border-slate-200 shadow-md group">
                  <img
                    src="/images/ro_plant_hero.jpg"
                    alt="Industrial RO Pilot Plant Skid"
                    className="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-md text-white px-3 py-1.5 rounded-xl text-xs font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span>Toray TM720D-400 Skid Telemetry Active</span>
                  </div>
                </div>

                {/* Right: Live Stream Telemetry Cards */}
                <div className="lg:col-span-5 space-y-4">
                  <div className="p-4 rounded-2xl bg-sky-50/60 border border-sky-100 space-y-2">
                    <span className="text-[11px] font-bold text-sky-800 uppercase tracking-wider">
                      Feed Stream Inflow
                    </span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-black text-sky-950 font-mono">30.00 m³/h</span>
                      <span className="text-xs font-mono font-bold text-sky-700">2,041 mg/L TDS</span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Temperature: 25.0°C • Stage 1 Feed Pressure: 16.06 bar
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100 space-y-2">
                    <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">
                      High-Purity Permeate Reclaim
                    </span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-black text-emerald-950 font-mono">21.06 m³/h</span>
                      <span className="text-xs font-mono font-bold text-emerald-700">7.21 mg/L TDS</span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Overall Recovery: <strong>70.22%</strong> • Rejection: 99.65%
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100 space-y-2">
                    <span className="text-[11px] font-bold text-indigo-800 uppercase tracking-wider">
                      Interstage Booster & Brine
                    </span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-black text-indigo-950 font-mono">+0.35 bar Boost</span>
                      <span className="text-xs font-mono font-bold text-indigo-700">Stage 2: 16.41 bar</span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Concentrate Discharge: 8.94 m³/h @ 6,835 mg/L TDS
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'ekf' && (
              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-sky-600" />
                      Stage 7 Axial EKF Virtual Sensors (n = 6 State Dimension)
                    </h4>
                    <p className="text-xs text-slate-500">
                      Non-invasive hydraulic resistance (R<sub>f</sub>) estimation across 15 physical elements from standard 10-sensor telemetry.
                    </p>
                  </div>
                  <span className="text-xs font-mono text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 font-semibold self-start sm:self-auto">
                    Covariance: Converged (P &lt; 10⁻⁴)
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  {[
                    { name: 'S1-Lead', rf: '3.42 × 10¹²', decline: '4.2%', status: 'Healthy' },
                    { name: 'S1-Mid', rf: '4.10 × 10¹²', decline: '5.8%', status: 'Healthy' },
                    { name: 'S1-Tail', rf: '5.20 × 10¹²', decline: '7.1%', status: 'Normal' },
                    { name: 'S2-Lead', rf: '5.85 × 10¹²', decline: '8.4%', status: 'Normal' },
                    { name: 'S2-Mid', rf: '7.40 × 10¹²', decline: '10.2%', status: 'Warning' },
                    { name: 'S2-Tail', rf: '9.82 × 10¹²', decline: '12.8%', status: 'Fouled' },
                  ].map((z, idx) => (
                    <div key={idx} className="p-3.5 rounded-xl bg-white border border-slate-200 text-center space-y-1 shadow-2xs">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">{z.name}</span>
                      <span className="text-xs font-bold font-mono text-slate-900 block">{z.rf}</span>
                      <span className="text-[11px] font-semibold text-sky-700 block">{z.decline} decline</span>
                      <span className="text-[10px] text-slate-500">{z.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'pareto' && (
              <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-purple-600" />
                      NSGA-II Genetic Multi-Objective Optimization Frontier
                    </h4>
                    <p className="text-xs text-slate-500">
                      Simultaneous optimization of Water Recovery (Maximize) vs Specific Energy Consumption (Minimize).
                    </p>
                  </div>
                  <span className="text-xs font-mono text-purple-700 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-200 font-semibold self-start sm:self-auto">
                    50 Non-Dominated Solutions
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
                  <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-1 shadow-2xs">
                    <span className="text-slate-400 text-[10px] uppercase font-bold block">Strategy A (Max Recovery)</span>
                    <div className="text-lg font-bold text-sky-700">75.1% Recovery</div>
                    <p className="text-slate-500">SEC: 0.892 kWh/m³ • High permeate yield</p>
                  </div>
                  <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-1 shadow-2xs">
                    <span className="text-emerald-800 text-[10px] uppercase font-bold block">Strategy B (Balanced - Optimal)</span>
                    <div className="text-lg font-bold text-emerald-800">70.2% Recovery</div>
                    <p className="text-emerald-700">SEC: 0.727 kWh/m³ • Minimum overall cost</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-1 shadow-2xs">
                    <span className="text-slate-400 text-[10px] uppercase font-bold block">Strategy C (Minimum Energy)</span>
                    <div className="text-lg font-bold text-indigo-700">65.0% Recovery</div>
                    <p className="text-slate-500">SEC: 0.615 kWh/m³ • Ultra-low power</p>
                  </div>
                </div>
              </div>
            )}

            {/* Bottom Action Footer */}
            <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-xs text-slate-500 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>Connected to Stage 7 Verified Virtual Plant Simulation Engine</span>
              </div>
              <Link
                href="/dashboard"
                className="w-full sm:w-auto bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold px-6 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 shadow-xs"
              >
                <span>Enter Full Digital Twin Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
