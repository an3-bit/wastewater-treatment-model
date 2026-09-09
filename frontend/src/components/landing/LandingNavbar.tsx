'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Droplets,
  ArrowRight,
  LogIn,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';

interface LandingNavbarProps {
  onOpenSignIn: () => void;
}

export function LandingNavbar({ onOpenSignIn }: LandingNavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full bg-white/85 backdrop-blur-xl border-b border-slate-200/80 text-slate-900 shadow-xs transition-all">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 h-20 flex items-center justify-between">
        
        {/* Brand Logo & Clean Subtitle */}
        <Link href="/" className="flex items-center gap-3.5 group">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-500 via-cyan-500 to-indigo-600 flex items-center justify-center shadow-md shadow-sky-500/20 group-hover:scale-105 transition-transform">
            <Droplets className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-black tracking-tight text-slate-900">
                AquaTwin <span className="text-sky-600">RO™</span>
              </span>
              <span className="hidden sm:inline-flex items-center gap-1.5 text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80 px-2.5 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Stage 7 Verified
              </span>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block tracking-wide font-medium">
              AI Digital Twin for Textile Wastewater Reuse
            </p>
          </div>
        </Link>

        {/* Desktop Navigation - Spacious & Clean */}
        <nav className="hidden lg:flex items-center gap-8 text-sm font-semibold text-slate-600">
          <a href="#overview" className="hover:text-sky-600 transition-colors">
            Overview
          </a>
          <a href="#features" className="hover:text-sky-600 transition-colors">
            Core Modules
          </a>
          <a href="#architecture" className="hover:text-sky-600 transition-colors">
            3:2 Staging Physics
          </a>
          <a href="#ekf-virtual" className="hover:text-sky-600 transition-colors">
            6-Zone EKF
          </a>
          <a href="#benchmarks" className="hover:text-sky-600 transition-colors">
            Literature Benchmarks
          </a>
        </nav>

        {/* Right CTA Area (Spacious, No GitHub link) */}
        <div className="hidden sm:flex items-center gap-4">
          <button
            onClick={onOpenSignIn}
            className="px-4 py-2.5 rounded-xl text-xs font-bold text-slate-700 hover:text-slate-950 hover:bg-slate-100 transition-all flex items-center gap-2 border border-slate-200 bg-white shadow-xs"
          >
            <LogIn className="w-4 h-4 text-sky-600" />
            <span>Sign In</span>
          </button>

          <Link
            href="/dashboard"
            className="bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-md shadow-sky-500/20 hover:shadow-lg transition-all flex items-center gap-2 group"
          >
            <span>Launch Control Center</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="lg:hidden flex items-center gap-3">
          <button
            onClick={onOpenSignIn}
            className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-sky-50 text-sky-700 border border-sky-200"
          >
            Sign In
          </button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-slate-200 px-6 py-5 space-y-4 animate-in slide-in-from-top duration-200 shadow-xl">
          <div className="flex flex-col gap-3.5 text-sm font-semibold text-slate-700">
            <a
              href="#overview"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-sky-600 py-1"
            >
              Overview
            </a>
            <a
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-sky-600 py-1"
            >
              Core Modules
            </a>
            <a
              href="#architecture"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-sky-600 py-1"
            >
              3:2 Staging Physics
            </a>
            <a
              href="#ekf-virtual"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-sky-600 py-1"
            >
              6-Zone EKF
            </a>
            <a
              href="#benchmarks"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-sky-600 py-1"
            >
              Literature Benchmarks
            </a>
          </div>

          <div className="pt-4 border-t border-slate-100 flex flex-col gap-2.5">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenSignIn();
              }}
              className="w-full py-2.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-800 flex items-center justify-center gap-2"
            >
              <LogIn className="w-4 h-4 text-sky-600" />
              <span>Sign In with Operator Role</span>
            </button>
            <Link
              href="/dashboard"
              className="w-full bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold py-2.5 rounded-xl text-center flex items-center justify-center gap-2 shadow-sm"
            >
              <span>Launch Control Center</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
