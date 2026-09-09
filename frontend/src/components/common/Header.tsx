'use client';

import React, { useState, useEffect } from 'react';
import {
  Bell,
  Clock,
  Radio,
  Server,
  User,
  ExternalLink,
  FileText,
  Activity,
  ShieldCheck,
} from 'lucide-react';
import { APP_CONFIG } from '@/utils/constants';
import { isMockMode } from '@/services/api';
import { digitalTwinService } from '@/services/digitalTwinService';
import { PlantState } from '@/types/digitalTwin';
import { ReportExportModal } from './ReportExportModal';
import Link from 'next/link';

interface HeaderProps {
  currentSimHour?: number;
}

export function Header({ currentSimHour = 48.0 }: HeaderProps) {
  const [mockActive, setMockActive] = useState(true);
  const [currentTime, setCurrentTime] = useState('');
  const [reportOpen, setReportOpen] = useState(false);
  const [plantState, setPlantState] = useState<PlantState | null>(null);

  useEffect(() => {
    setMockActive(isMockMode());
    digitalTwinService.getPlantState().then(setPlantState).catch(console.error);

    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);

    const handleModeChange = () => setMockActive(isMockMode());
    window.addEventListener('wt-mode-change', handleModeChange);

    return () => {
      clearInterval(interval);
      window.removeEventListener('wt-mode-change', handleModeChange);
    };
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      {/* Left: Clean Plant Identity */}
      <div className="flex items-center gap-4 min-w-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-2.5 h-2.5 rounded-full bg-sky-500 shrink-0 ring-4 ring-sky-50" />
          <h1 className="text-sm font-bold text-slate-900 truncate whitespace-nowrap">
            Textile RO Pilot Plant
          </h1>
          <span className="hidden sm:inline-flex items-center text-[11px] font-medium text-slate-500 bg-slate-100/80 border border-slate-200 px-2 py-0.5 rounded-md whitespace-nowrap">
            3:2 Staging (15 Elements)
          </span>
        </div>

        {/* Status Indicator */}
        <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-slate-200">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Virtual Twin Live
          </span>
          <span className="text-[11px] font-mono text-slate-400">
            {APP_CONFIG.MODEL_VERSION}
          </span>
        </div>
      </div>

      {/* Right: Streamlined Actions & Telemetry */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Sim Clock Tag */}
        <div className="flex items-center gap-2 bg-slate-50 px-3 py-1 rounded-lg border border-slate-200 text-xs font-mono text-slate-700 whitespace-nowrap">
          <Clock className="w-3.5 h-3.5 text-sky-600 shrink-0" />
          <span>t = <strong>{currentSimHour.toFixed(1)}h</strong></span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500 font-sans text-[11px]">{currentTime || '06:45:00'}</span>
        </div>

        {/* Data Source Badge */}
        <Link
          href="/dashboard/system"
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all whitespace-nowrap ${
            mockActive
              ? 'bg-amber-50/80 text-amber-800 border-amber-200/80 hover:bg-amber-100'
              : 'bg-emerald-50/80 text-emerald-800 border-emerald-200/80 hover:bg-emerald-100'
          }`}
          title="Configure API connection"
        >
          <Server className="w-3 h-3 text-amber-600 shrink-0" />
          <span>{mockActive ? 'Mock Engine' : 'FastAPI Live'}</span>
        </Link>

        {/* Export Dossier Button */}
        <button
          onClick={() => setReportOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-xs transition-all active:scale-95 whitespace-nowrap"
          title="Generate executive process audit dossier"
        >
          <FileText className="w-3.5 h-3.5 text-sky-400 shrink-0" />
          <span>Export Dossier</span>
        </button>

        {/* Notification Bell */}
        <button
          type="button"
          className="relative p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-amber-500 rounded-full ring-2 ring-white" />
        </button>

        {/* Operator User */}
        <div className="flex items-center pl-2 border-l border-slate-200">
          <div
            className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 font-bold text-[11px]"
            title="Process AI Group — Operator"
          >
            OP
          </div>
        </div>
      </div>

      {/* Report Export Dossier Modal */}
      {plantState && (
        <ReportExportModal
          isOpen={reportOpen}
          onClose={() => setReportOpen(false)}
          plantState={plantState}
        />
      )}
    </header>
  );
}
