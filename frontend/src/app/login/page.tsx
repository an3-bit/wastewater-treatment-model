'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Droplets,
  ShieldCheck,
  UserCheck,
  Activity,
  Cpu,
  Eye,
  CheckCircle2,
  Lock,
  ArrowRight,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';
import { UserRole, PRESET_USERS } from '@/types/auth';
import { loginAsRole } from '@/utils/auth';

export default function LoginPage() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<UserRole>('plant_engineer');
  const [username, setUsername] = useState<string>('elena.vance@plant-ro.org');
  const [password, setPassword] = useState<string>('••••••••••••');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    const user = PRESET_USERS[role];
    setUsername(user.email);
    setPassword('••••••••••••');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    loginAsRole(selectedRole);

    setTimeout(() => {
      setIsSubmitting(false);
      router.push('/dashboard');
    }, 400);
  };

  const handleQuickLaunch = (role: UserRole) => {
    loginAsRole(role);
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between selection:bg-sky-500 selection:text-white">
      
      {/* Top Navbar */}
      <header className="p-6 max-w-7xl mx-auto w-full flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
            <Droplets className="w-5 h-5" />
          </div>
          <div>
            <span className="text-base font-black tracking-tight text-slate-900">
              AquaTwin <span className="text-sky-600">RO™</span>
            </span>
            <p className="text-[10px] text-slate-500">Industrial Digital Twin Control System</p>
          </div>
        </Link>

        <Link
          href="/"
          className="text-xs font-semibold text-slate-700 hover:text-slate-900 flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors shadow-2xs"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Landing Page</span>
        </Link>
      </header>

      {/* Main Login Card */}
      <main className="max-w-2xl mx-auto w-full px-4 sm:px-6 py-8">
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden">
          
          {/* Header */}
          <div className="p-6 sm:p-8 bg-gradient-to-r from-sky-600 via-indigo-600 to-sky-700 text-white">
            <div className="flex items-center gap-2 text-sky-200 text-xs font-mono font-semibold uppercase tracking-widest mb-1.5">
              <ShieldCheck className="w-4 h-4" />
              <span>Operator Session Authentication</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Sign In to Control Center
            </h1>
            <p className="text-xs sm:text-sm text-sky-100 mt-1">
              Select an authorized operator persona or enter your digital twin credentials.
            </p>
          </div>

          <div className="p-6 sm:p-8 space-y-6">
            
            {/* 4 Role Cards */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-3">
                Select Operator Role (1-Click Demo Access)
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Role 1 */}
                <button
                  type="button"
                  onClick={() => handleRoleSelect('plant_engineer')}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    selectedRole === 'plant_engineer'
                      ? 'border-sky-500 bg-sky-50/80 ring-2 ring-sky-500/20 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <UserCheck className="w-4 h-4 text-sky-600" />
                      Chief Process Engineer
                    </span>
                    {selectedRole === 'plant_engineer' && (
                      <CheckCircle2 className="w-4 h-4 text-sky-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Full setpoint authority, disturbance simulation, and CIP chemical advisor overrides.
                  </p>
                  <span className="inline-block mt-2.5 text-[10px] font-mono text-sky-800 bg-sky-100/70 px-2 py-0.5 rounded-md font-semibold">
                    Dr. Elena Vance • Full Control
                  </span>
                </button>

                {/* Role 2 */}
                <button
                  type="button"
                  onClick={() => handleRoleSelect('ro_operator')}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    selectedRole === 'ro_operator'
                      ? 'border-emerald-500 bg-emerald-50/80 ring-2 ring-emerald-500/20 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Activity className="w-4 h-4 text-emerald-600" />
                      Senior RO Operator
                    </span>
                    {selectedRole === 'ro_operator' && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Live 10-sensor telemetry, P&ID visual stream monitor, and alarm acknowledgments.
                  </p>
                  <span className="inline-block mt-2.5 text-[10px] font-mono text-emerald-800 bg-emerald-100/70 px-2 py-0.5 rounded-md font-semibold">
                    Marcus Chen • Operational
                  </span>
                </button>

                {/* Role 3 */}
                <button
                  type="button"
                  onClick={() => handleRoleSelect('optimization_scientist')}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    selectedRole === 'optimization_scientist'
                      ? 'border-purple-500 bg-purple-50/80 ring-2 ring-purple-500/20 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Cpu className="w-4 h-4 text-purple-600" />
                      AI & Physics Scientist
                    </span>
                    {selectedRole === 'optimization_scientist' && (
                      <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500">
                    NSGA-II Pareto trade-off frontiers, ANN surrogate parity bench, Latin Hypercube.
                  </p>
                  <span className="inline-block mt-2.5 text-[10px] font-mono text-purple-800 bg-purple-100/70 px-2 py-0.5 rounded-md font-semibold">
                    Dr. Amina Al-Mansoor • Scientific
                  </span>
                </button>

                {/* Role 4 */}
                <button
                  type="button"
                  onClick={() => handleRoleSelect('guest_auditor')}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    selectedRole === 'guest_auditor'
                      ? 'border-amber-500 bg-amber-50/80 ring-2 ring-amber-500/20 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Eye className="w-4 h-4 text-amber-600" />
                      Guest Auditor
                    </span>
                    {selectedRole === 'guest_auditor' && (
                      <CheckCircle2 className="w-4 h-4 text-amber-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Read-only evaluation of 3:2 textile wastewater reuse compliance and dossier export.
                  </p>
                  <span className="inline-block mt-2.5 text-[10px] font-mono text-amber-800 bg-amber-100/70 px-2 py-0.5 rounded-md font-semibold">
                    Guest Demo • Read-Only
                  </span>
                </button>
              </div>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="space-y-4 pt-2 border-t border-slate-100">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Operator Email
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white"
                    required
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Passcode / Token
                  </label>
                  <div className="relative">
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white"
                      required
                    />
                    <Lock className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-3.5 pointer-events-none" />
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => handleQuickLaunch(selectedRole)}
                  className="w-full sm:w-auto text-xs font-semibold text-slate-600 hover:text-slate-900 py-3 px-4 rounded-xl border border-slate-200 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span>Instant 1-Click Launch</span>
                </button>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full sm:w-auto bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-bold text-xs py-3 px-8 rounded-xl shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <span>Authorizing...</span>
                  ) : (
                    <>
                      <span>Enter Control Center</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>

          </div>
        </div>
      </main>

      {/* Bottom Footer */}
      <footer className="p-6 max-w-7xl mx-auto w-full text-center text-xs text-slate-500">
        AquaTwin RO™ Digital Twin • Stage 7 EKF Verified • 3:2 Staging Configuration (Toray TM720D-400)
      </footer>
    </div>
  );
}
