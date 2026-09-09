'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ShieldCheck,
  Lock,
  ArrowRight,
  UserCheck,
  Cpu,
  Activity,
  X,
  Sparkles,
  Eye,
  CheckCircle2,
} from 'lucide-react';
import { UserRole, PRESET_USERS } from '@/types/auth';
import { loginAsRole } from '@/utils/auth';

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialRole?: UserRole;
}

export function SignInModal({ isOpen, onClose, initialRole = 'plant_engineer' }: SignInModalProps) {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<UserRole>(initialRole);
  const [username, setUsername] = useState<string>('elena.vance@plant-ro.org');
  const [password, setPassword] = useState<string>('••••••••••••');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    const user = PRESET_USERS[role];
    setUsername(user.email);
    setPassword('••••••••••••');
  };

  const handleLogin = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsSubmitting(true);
    
    // Authenticate and save session
    loginAsRole(selectedRole);

    setTimeout(() => {
      setIsSubmitting(false);
      onClose();
      router.push('/dashboard');
    }, 450);
  };

  const handleQuickLaunch = (role: UserRole) => {
    loginAsRole(role);
    onClose();
    router.push('/dashboard');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/40 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden text-slate-900">
        
        {/* Top Header Banner */}
        <div className="bg-gradient-to-r from-sky-600 via-indigo-600 to-sky-700 text-white p-6 sm:p-8 relative">
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-2 rounded-xl text-sky-100 hover:text-white hover:bg-white/10 transition-colors"
            title="Close modal"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2 text-sky-200 text-xs font-mono font-semibold uppercase tracking-widest mb-1.5">
            <ShieldCheck className="w-4 h-4" />
            <span>Industrial Control Access Gateway</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
            AquaTwin RO™ Sign In
          </h2>
          <p className="text-xs sm:text-sm text-sky-100 mt-1 max-w-lg leading-relaxed">
            Select an operational role to access the live 2-stage digital twin, 6-zone Extended Kalman Filter, and optimization control center.
          </p>
        </div>

        <div className="p-6 sm:p-8 space-y-6">
          {/* 4 Role Selection Cards */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2.5">
              Select Operator Persona (1-Click Demo Login)
            </label>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* Role 1: Chief Process Engineer */}
              <button
                type="button"
                onClick={() => handleRoleSelect('plant_engineer')}
                className={`p-3.5 rounded-2xl border text-left transition-all relative flex flex-col justify-between ${
                  selectedRole === 'plant_engineer'
                    ? 'border-sky-500 bg-sky-50/80 ring-2 ring-sky-500/20 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <UserCheck className="w-4 h-4 text-sky-600" />
                      Chief Process Engineer
                    </span>
                    {selectedRole === 'plant_engineer' && (
                      <CheckCircle2 className="w-4 h-4 text-sky-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    Full setpoint control, disturbance injection, CIP chemical advisor overrides.
                  </p>
                </div>
                <span className="inline-block mt-2 text-[10px] font-mono font-semibold text-sky-700 bg-sky-100/70 px-2 py-0.5 rounded-md self-start">
                  Dr. Elena Vance • Full Control
                </span>
              </button>

              {/* Role 2: RO Operator */}
              <button
                type="button"
                onClick={() => handleRoleSelect('ro_operator')}
                className={`p-3.5 rounded-2xl border text-left transition-all relative flex flex-col justify-between ${
                  selectedRole === 'ro_operator'
                    ? 'border-emerald-500 bg-emerald-50/80 ring-2 ring-emerald-500/20 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Activity className="w-4 h-4 text-emerald-600" />
                      Senior RO Skid Operator
                    </span>
                    {selectedRole === 'ro_operator' && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    Live 10-sensor telemetry, P&ID visual stream monitor, alarm acknowledgments.
                  </p>
                </div>
                <span className="inline-block mt-2 text-[10px] font-mono font-semibold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-md self-start">
                  Marcus Chen • Operational
                </span>
              </button>

              {/* Role 3: Optimization Scientist */}
              <button
                type="button"
                onClick={() => handleRoleSelect('optimization_scientist')}
                className={`p-3.5 rounded-2xl border text-left transition-all relative flex flex-col justify-between ${
                  selectedRole === 'optimization_scientist'
                    ? 'border-purple-500 bg-purple-50/80 ring-2 ring-purple-500/20 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Cpu className="w-4 h-4 text-purple-600" />
                      AI & Physics Scientist
                    </span>
                    {selectedRole === 'optimization_scientist' && (
                      <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    NSGA-II Pareto frontiers, ANN surrogate parity bench, Latin Hypercube training.
                  </p>
                </div>
                <span className="inline-block mt-2 text-[10px] font-mono font-semibold text-purple-700 bg-purple-100/70 px-2 py-0.5 rounded-md self-start">
                  Dr. Amina Al-Mansoor • Scientific
                </span>
              </button>

              {/* Role 4: Guest Auditor */}
              <button
                type="button"
                onClick={() => handleRoleSelect('guest_auditor')}
                className={`p-3.5 rounded-2xl border text-left transition-all relative flex flex-col justify-between ${
                  selectedRole === 'guest_auditor'
                    ? 'border-amber-500 bg-amber-50/80 ring-2 ring-amber-500/20 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Eye className="w-4 h-4 text-amber-600" />
                      Guest Auditor / Visitor
                    </span>
                    {selectedRole === 'guest_auditor' && (
                      <CheckCircle2 className="w-4 h-4 text-amber-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    Read-only evaluation of 3:2 textile wastewater reuse compliance and dossier export.
                  </p>
                </div>
                <span className="inline-block mt-2 text-[10px] font-mono font-semibold text-amber-700 bg-amber-100/70 px-2 py-0.5 rounded-md self-start">
                  Guest Demo • Read-Only
                </span>
              </button>
            </div>
          </div>

          {/* Form Input Section */}
          <form onSubmit={handleLogin} className="space-y-4 pt-1 border-t border-slate-100">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Operator Email / ID
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white"
                    placeholder="operator@plant.org"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Security Passcode / Token
                </label>
                <div className="relative">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white"
                    placeholder="••••••••••••"
                    required
                  />
                  <Lock className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-3.5 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
              <button
                type="button"
                onClick={() => handleQuickLaunch(selectedRole)}
                className="w-full sm:w-auto text-xs font-semibold text-slate-600 hover:text-slate-900 py-2.5 px-4 rounded-xl border border-slate-200 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition-colors"
              >
                <Sparkles className="w-4 h-4 text-amber-500" />
                <span>Instant 1-Click Launch</span>
              </button>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full sm:w-auto bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-bold py-3 px-6 rounded-xl shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Authorizing Session...</span>
                  </>
                ) : (
                  <>
                    <span>Enter Control Center</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Compliance & Security Footer */}
          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-3 border-t border-slate-100">
            <span className="flex items-center gap-1">
              <Lock className="w-3 h-3 text-emerald-600" />
              TLS 1.3 Encrypted • Stage 7 Verified
            </span>
            <span className="font-mono">v2.4.0 • Zero-Trust Skid Interface</span>
          </div>
        </div>
      </div>
    </div>
  );
}
