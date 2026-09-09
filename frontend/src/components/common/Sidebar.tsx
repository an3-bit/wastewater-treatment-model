'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  GitGraph,
  Layers,
  Gauge,
  Droplets,
  Zap,
  TrendingUp,
  Sliders,
  FlaskConical,
  BookOpen,
  Settings,
  ShieldCheck,
} from 'lucide-react';
import { APP_CONFIG } from '@/utils/constants';

interface NavSection {
  title: string;
  items: {
    label: string;
    href: string;
    icon: React.ElementType;
    badge?: string;
  }[];
}

const navSections: NavSection[] = [
  {
    title: 'Operations',
    items: [
      { label: 'Overview', href: '/dashboard', icon: LayoutDashboard },
      { label: 'Live Process Twin', href: '/dashboard/twin', icon: GitGraph },
      { label: 'Sensors Telemetry', href: '/dashboard/sensors', icon: Gauge, badge: '10' },
      { label: 'Membrane Health', href: '/dashboard/membranes', icon: Layers },
    ],
  },
  {
    title: 'Analytics & Physics',
    items: [
      { label: 'Water Quality', href: '/dashboard/water-quality', icon: Droplets },
      { label: 'Energy & SEC', href: '/dashboard/energy', icon: Zap },
      { label: 'Fouling Forecaster', href: '/dashboard/forecast', icon: TrendingUp },
      { label: 'Optimization', href: '/dashboard/optimization', icon: Sliders, badge: 'NSGA-II' },
    ],
  },
  {
    title: 'Research & System',
    items: [
      { label: 'What-If Scenarios', href: '/dashboard/scenarios', icon: FlaskConical },
      { label: 'Research Roadmap', href: '/dashboard/research', icon: BookOpen, badge: 'Stages 1-8' },
      { label: 'Architecture & API', href: '/dashboard/system', icon: Settings },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between h-screen sticky top-0 z-30 select-none shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-100">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500 to-emerald-500 flex items-center justify-center text-white font-extrabold text-sm shadow-xs shadow-sky-200">
            WT
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-slate-900 tracking-tight text-sm group-hover:text-sky-600 transition-colors">
                {APP_CONFIG.NAME}
              </span>
              <span className="text-[10px] bg-sky-100 text-sky-800 font-semibold px-1.5 py-0.2 rounded">
                v2.0
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">
              Industrial Digital Twin
            </p>
          </div>
        </Link>
      </div>

      {/* Grouped Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-4">
        {navSections.map((section, sIdx) => (
          <div key={sIdx} className="space-y-1">
            <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {section.title}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === '/dashboard'
                  ? pathname === '/dashboard'
                  : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-sky-50 text-sky-700 font-semibold shadow-xs'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={`w-4 h-4 shrink-0 ${
                        isActive ? 'text-sky-600' : 'text-slate-400 group-hover:text-slate-600'
                      }`}
                    />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.2 rounded shrink-0 ${
                        isActive
                          ? 'bg-sky-200/70 text-sky-800'
                          : 'bg-slate-100 text-slate-500'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Bottom Status Card */}
      <div className="p-3 border-t border-slate-100 bg-slate-50/50">
        <div className="bg-white rounded-lg p-2.5 border border-slate-200 text-xs space-y-1 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Model Engine</span>
            <span className="font-semibold text-slate-800 font-mono text-[11px]">
              V2.0 Corrected
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-500 font-medium">Observability</span>
            <span className="text-emerald-700 font-semibold text-[11px] flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              EKF (n = 6)
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
