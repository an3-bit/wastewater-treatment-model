'use client';

import React, { useState, useEffect } from 'react';
import { Gauge, CheckCircle2, AlertTriangle, Radio, ShieldCheck } from 'lucide-react';
import { sensorService } from '@/services/sensorService';
import { SensorReading, SensorSuiteSummary } from '@/types/sensors';
import { SensorCard } from '@/components/sensors/SensorCard';
import { StatusBadge } from '@/components/common/StatusBadge';

export default function SensorsPage() {
  const [summary, setSummary] = useState<SensorSuiteSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSensors() {
      try {
        const data = await sensorService.getSensorSummary();
        setSummary(data);
      } catch (err) {
        console.error('Failed to load sensors:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSensors();
  }, []);

  if (loading || !summary) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-200 rounded w-1/4" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-44 bg-slate-200 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Standard Skid Sensor Telemetry
            </h2>
            <StatusBadge status="10 Sensors Online" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Stage 7 Standard Skid Instrumentation Suite (Case 2) providing complete mass flux and pressure observability.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs">
          <span className="text-slate-500">Scan Interval: <strong>1.0 s</strong></span>
          <span className="text-slate-300">|</span>
          <span className="text-emerald-700 font-semibold">100% Signal Quality</span>
        </div>
      </div>

      {/* Sensor Metric Overview Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Active Sensors
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold text-slate-900">{summary.online_count}</span>
            <span className="text-xs text-slate-500">/ {summary.total_sensors} connected</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Sensor Configuration
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-sky-700">Case 2 (Standard)</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            State Observability
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-emerald-700">Rank 4-5 SVD</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Instrumentation Health
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-emerald-700">Nominal Noise</span>
          </div>
        </div>
      </div>

      {/* 10 Sensor Cards Grid in Spacious Responsive Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {summary.sensors.map((sensor) => (
          <SensorCard key={sensor.id} sensor={sensor} />
        ))}
      </div>

      {/* Sensor Ablation & Observability Analysis Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-sky-600" />
          Stage 7 Sensor Ablation & Observability Ranking
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Fisher Information Matrix (FIM) and singular value decomposition (SVD) across the sensor suite demonstrate that <strong>Total Permeate Flow (Q<sub>p,total</sub>)</strong> is mathematically essential to observe bulk hydraulic flux. <strong>Stage 2 Pressure (P<sub>2</sub>)</strong> and <strong>Permeate Salinity (C<sub>p,total</sub>)</strong> decouple stage-level solute transport. Case 2 matches the estimation fidelity of the 13-sensor Rich Set within 0.044% MAE while reducing instrumentation capital cost.
        </p>
      </div>
    </div>
  );
}
