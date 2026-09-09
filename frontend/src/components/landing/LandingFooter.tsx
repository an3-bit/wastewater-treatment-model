'use client';

import React from 'react';
import Link from 'next/link';
import {
  Droplets,
  ShieldCheck,
} from 'lucide-react';

export function LandingFooter() {
  return (
    <footer className="bg-slate-100 text-slate-600 border-t border-slate-200/80 pt-16 pb-12 text-xs">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 space-y-12">
        
        {/* Main 4-Column Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          
          {/* Brand & Description (2 Cols) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-xs">
                <Droplets className="w-5 h-5" />
              </div>
              <span className="text-base font-black text-slate-900 tracking-tight">
                AquaTwin <span className="text-sky-600">RO™</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed max-w-sm">
              AI-Enabled Digital Twin for Fouling-Aware Multi-Objective Optimization of Textile Wastewater Reuse. Developed with first-principles mechanics, Extended Kalman Filtering, and NSGA-II Pareto analytics.
            </p>
          </div>

          {/* Quick Links Column 1: Twin Navigation */}
          <div className="space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 block">
              Control Center
            </span>
            <ul className="space-y-2">
              <li>
                <Link href="/dashboard" className="hover:text-sky-600 transition-colors">
                  Plant Overview
                </Link>
              </li>
              <li>
                <Link href="/dashboard/twin" className="hover:text-sky-600 transition-colors">
                  Live P&ID Process Flow
                </Link>
              </li>
              <li>
                <Link href="/dashboard/membranes" className="hover:text-sky-600 transition-colors">
                  6-Zone EKF Virtual Sensors
                </Link>
              </li>
              <li>
                <Link href="/dashboard/optimization" className="hover:text-sky-600 transition-colors">
                  NSGA-II Pareto Optimizer
                </Link>
              </li>
              <li>
                <Link href="/dashboard/forecast" className="hover:text-sky-600 transition-colors">
                  Dynamic CIP Advisor
                </Link>
              </li>
            </ul>
          </div>

          {/* Quick Links Column 2: Analytics & Research */}
          <div className="space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 block">
              Physics & Surrogates
            </span>
            <ul className="space-y-2">
              <li>
                <Link href="/dashboard/scenarios" className="hover:text-sky-600 transition-colors">
                  ANN Parity Audit Bench
                </Link>
              </li>
              <li>
                <Link href="/dashboard/water-quality" className="hover:text-sky-600 transition-colors">
                  Solute Mass Balance Ledger
                </Link>
              </li>
              <li>
                <Link href="/dashboard/energy" className="hover:text-sky-600 transition-colors">
                  Specific Energy Breakdown
                </Link>
              </li>
              <li>
                <Link href="/dashboard/sensors" className="hover:text-sky-600 transition-colors">
                  10-Sensor Skid Telemetry
                </Link>
              </li>
              <li>
                <Link href="/dashboard/research" className="hover:text-sky-600 transition-colors">
                  Literature & Provenance
                </Link>
              </li>
            </ul>
          </div>

          {/* Standards & Provenance */}
          <div className="space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 block">
              Scientific Standards
            </span>
            <ul className="space-y-2 text-slate-500 font-mono text-[11px]">
              <li>Toray TM720D-400 Spec</li>
              <li>Spiegler-Kedem Hydraulics</li>
              <li>Stage 7 EKF Observability</li>
              <li>NSGA-II Non-Dominated Sort</li>
              <li>Strict Mass Closure (0.000%)</li>
            </ul>
          </div>
        </div>

        {/* Bottom Copyright Bar */}
        <div className="pt-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>AquaTwin RO™ Digital Twin Platform • Stage 7 Verified Version 2.4.0</span>
          </div>
          <div>
            <span>Industrial Pilot System • Built for Textile Wastewater Reuse & ZLD</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
