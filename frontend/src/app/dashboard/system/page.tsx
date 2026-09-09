'use client';

import React, { useState, useEffect } from 'react';
import {
  Settings,
  Server,
  Radio,
  Layers,
  Cpu,
  TrendingUp,
  Sliders,
  CheckCircle2,
  Clock,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { isMockMode, setDataMode, getApiBaseUrl, setApiBaseUrl } from '@/services/api';
import { StatusBadge } from '@/components/common/StatusBadge';

interface ArchLayer {
  layer: string;
  name: string;
  technology: string;
  status: 'IMPLEMENTED' | 'NEXT' | 'FUTURE';
  description: string;
  icon: React.ElementType;
}

const architectureLayers: ArchLayer[] = [
  {
    layer: 'Layer 1',
    name: 'Physical / Virtual RO Skid',
    technology: 'Toray TM720D-400 (3:2 Staging, 15 Elements)',
    status: 'IMPLEMENTED',
    description: 'First-principles mechanistic simulator generating dynamic hydraulic and salinity crossflow trajectories.',
    icon: Layers,
  },
  {
    layer: 'Layer 2',
    name: 'Instrumentation & Telemetry',
    technology: 'Standard 10-Sensor Skid Suite (Case 2)',
    status: 'IMPLEMENTED',
    description: 'Flow, pressure, temperature, salinity (TDS), and electrical power instrumentation with industrial noise.',
    icon: Radio,
  },
  {
    layer: 'Layer 3',
    name: 'Digital Twin Service Adapter',
    technology: 'FastAPI / Typed REST & WebSocket Protocol',
    status: 'IMPLEMENTED',
    description: 'Clean data contracts bridging Next.js frontend with Python scientific engines without JS model duplication.',
    icon: Server,
  },
  {
    layer: 'Layer 4',
    name: 'Physics Engine & Estimator',
    technology: 'Model V2.0 + Extended Kalman Filter (n = 6)',
    status: 'IMPLEMENTED',
    description: 'Reconstructs unmeasured axial membrane fouling resistance (Rf) with zero feed disturbance leakage.',
    icon: Cpu,
  },
  {
    layer: 'Layer 5',
    name: 'Forecasting & Multi-Objective Engine',
    technology: 'Dynamic Fouling Kinetics + NSGA-II Optimizer',
    status: 'IMPLEMENTED',
    description: 'Projects remaining time to t5, t10, t15 Analysis Thresholds and maintains 424 non-dominated Pareto setpoints.',
    icon: TrendingUp,
  },
  {
    layer: 'Layer 6',
    name: 'Operator Decision Support UI',
    technology: 'Next.js 15, TypeScript, Tailwind CSS, Recharts',
    status: 'IMPLEMENTED',
    description: 'Bright modern engineering console for plant supervision, scenario experiments, and telemetry analytics.',
    icon: Sliders,
  },
  {
    layer: 'Layer 7',
    name: 'Stage 8 Closed-Loop Controller',
    technology: 'Dynamic Setpoint Governor & CIP Advisor',
    status: 'NEXT',
    description: 'Automated pressure trajectory optimization and fouling-aware cleaning cycle recommendations.',
    icon: Clock,
  },
];

export default function SystemArchitecturePage() {
  const [dataMode, setLocalDataMode] = useState<'mock' | 'api'>('mock');
  const [apiUrl, setLocalApiUrl] = useState('http://localhost:8000');
  const [testingConn, setTestingConn] = useState(false);
  const [connResult, setConnResult] = useState<{ success: boolean; msg: string } | null>(null);

  useEffect(() => {
    setLocalDataMode(isMockMode() ? 'mock' : 'api');
    setLocalApiUrl(getApiBaseUrl());
  }, []);

  const handleModeToggle = (mode: 'mock' | 'api') => {
    setLocalDataMode(mode);
    setDataMode(mode);
  };

  const handleUrlSave = () => {
    setApiBaseUrl(apiUrl);
    setConnResult({ success: true, msg: 'API URL updated successfully.' });
  };

  const testConnection = async () => {
    setTestingConn(true);
    setConnResult(null);
    try {
      const res = await fetch(`${apiUrl}/api/v1/twin/status`, { method: 'GET' });
      if (res.ok) {
        setConnResult({ success: true, msg: 'Connected to live Python Digital Twin API!' });
      } else {
        setConnResult({ success: false, msg: `API returned status ${res.status}. Falling back to mock engine.` });
      }
    } catch (err: any) {
      setConnResult({
        success: false,
        msg: `Unable to reach ${apiUrl}. Ensure the FastAPI server is running. Using typed mock fallback.`,
      });
    } finally {
      setTestingConn(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              System Architecture & Service Configuration
            </h2>
            <StatusBadge status="Modular Architecture" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Decoupled Next.js client connecting to Python Digital Twin services without physics code conversion.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs">
          <Server className="w-4 h-4 text-sky-600" />
          <span>Active Data Mode: <strong className="uppercase text-slate-800">{dataMode}</strong></span>
        </div>
      </div>

      {/* Integration Mode & API Switcher Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-sky-600" />
            <h3 className="text-base font-bold text-slate-900">
              Data Source & API Adapter Settings
            </h3>
          </div>
          <StatusBadge status={dataMode === 'mock' ? 'Mock Data Mode' : 'Live API Mode'} variant={dataMode === 'mock' ? 'warning' : 'healthy'} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Mode Switcher */}
          <div className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Frontend Data Retrieval Mode
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleModeToggle('mock')}
                className={`p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
                  dataMode === 'mock'
                    ? 'bg-amber-50/70 border-2 border-amber-400 text-amber-950 shadow-xs'
                    : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <div className="font-bold flex items-center justify-between mb-1">
                  <span>Typed Mock Engine</span>
                  {dataMode === 'mock' && <CheckCircle2 className="w-4 h-4 text-amber-600" />}
                </div>
                <p className="text-[11px] text-slate-500">
                  Deterministic, validated data from Model V2.0, Stage 5 NSGA-II, and Stage 7 EKF.
                </p>
              </button>

              <button
                type="button"
                onClick={() => handleModeToggle('api')}
                className={`p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
                  dataMode === 'api'
                    ? 'bg-emerald-50/70 border-2 border-emerald-400 text-emerald-950 shadow-xs'
                    : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <div className="font-bold flex items-center justify-between mb-1">
                  <span>FastAPI Backend</span>
                  {dataMode === 'api' && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                </div>
                <p className="text-[11px] text-slate-500">
                  Live REST & WebSocket communication with Python scientific service.
                </p>
              </button>
            </div>
          </div>

          {/* API URL Config */}
          <div className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              FastAPI Endpoint URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setLocalApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
                className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
              <button
                type="button"
                onClick={handleUrlSave}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-xl text-xs transition-colors"
              >
                Save
              </button>
              <button
                type="button"
                onClick={testConnection}
                disabled={testingConn}
                className="px-3 py-2 bg-sky-600 hover:bg-sky-700 text-white font-medium rounded-xl text-xs transition-colors flex items-center gap-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${testingConn ? 'animate-spin' : ''}`} />
                Test API
              </button>
            </div>

            {connResult && (
              <div
                className={`p-2.5 rounded-lg border text-xs flex items-center gap-2 ${
                  connResult.success
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                    : 'bg-amber-50 text-amber-800 border-amber-200'
                }`}
              >
                {connResult.success ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                )}
                <span>{connResult.msg}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Layered System Architecture Breakdown */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Multi-Tier Digital Twin Architecture
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Strictly decoupled layers separating physical processes, data acquisition, state estimators, and user interfaces.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              <span className="text-slate-600 font-medium">Implemented</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
              <span className="text-slate-600 font-medium">Next (Stage 8)</span>
            </span>
          </div>
        </div>

        <div className="space-y-3">
          {architectureLayers.map((layer, idx) => {
            const Icon = layer.icon;
            const isImplemented = layer.status === 'IMPLEMENTED';
            const isNext = layer.status === 'NEXT';

            return (
              <div
                key={idx}
                className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors ${
                  isImplemented
                    ? 'bg-slate-50/70 border-slate-200 hover:bg-slate-50'
                    : isNext
                    ? 'bg-indigo-50/50 border-indigo-200'
                    : 'bg-slate-50/30 border-slate-100'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`p-2 rounded-xl mt-0.5 ${
                      isImplemented
                        ? 'bg-white text-sky-700 border border-slate-200 shadow-2xs'
                        : 'bg-indigo-600 text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono font-bold text-slate-400">
                        {layer.layer}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900">{layer.name}</h4>
                      <span className="text-slate-300">|</span>
                      <span className="text-xs text-sky-700 font-medium">{layer.technology}</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed">{layer.description}</p>
                  </div>
                </div>

                <StatusBadge
                  status={layer.status}
                  variant={isImplemented ? 'healthy' : isNext ? 'virtual' : 'neutral'}
                  size="sm"
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
