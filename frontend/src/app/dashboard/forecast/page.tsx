'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Clock,
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  Cpu,
  Layers,
} from 'lucide-react';
import { forecastService } from '@/services/forecastService';
import { ForecastResult } from '@/types/forecast';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Timeline } from '@/components/common/Timeline';
import { ForecastTrajectoryChart } from '@/components/charts/ForecastTrajectoryChart';
import { CleaningAdvisor } from '@/components/membrane/CleaningAdvisor';
import { formatPercent, formatHours } from '@/utils/formatters';

export default function ForecastPage() {
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<number>(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await forecastService.getForecast(selectedHorizon);
        setForecast(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedHorizon]);

  if (loading || !forecast) {
    return <div className="h-96 bg-white rounded-2xl border border-slate-200 animate-pulse" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              Predictive Fouling & Threshold Forecasting
            </h2>
            <StatusBadge status="Stage 8C Standard" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Forward projection of fouling resistance and remaining time estimation to progressive analysis thresholds.
          </p>
        </div>

        {/* Horizon Selector */}
        <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-xl border border-slate-200">
          <span className="text-xs font-semibold text-slate-500 pl-2 pr-1">Horizon:</span>
          {[6, 12, 24, 48, 72].map((h) => (
            <button
              key={h}
              onClick={() => setSelectedHorizon(h)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                selectedHorizon === h
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-200'
              }`}
            >
              {h}h {h === 24 && '(Std)'}
            </button>
          ))}
        </div>
      </div>

      {/* Top Cards: Current Decline + Analysis Thresholds (t5, t10, t15) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Current Flux Decline"
          value={formatPercent(forecast.current_decline_pct)}
          icon={TrendingUp}
          accentColor="sky"
          subtitle="EKF State at t = 48h"
          badge={<StatusBadge status="Active State" variant="normal" size="sm" />}
        />

        <MetricCard
          title="Predicted t₅ Threshold"
          value={formatHours(forecast.predicted_t5_hours)}
          icon={Clock}
          accentColor="emerald"
          subtitle="Analysis Threshold (5%)"
          badge={<StatusBadge status="Crossed" variant="healthy" size="sm" />}
        />

        <MetricCard
          title="Predicted t₁₀ Threshold"
          value={formatHours(forecast.predicted_t10_hours)}
          icon={Clock}
          accentColor="amber"
          subtitle="Analysis Threshold (10%)"
          trend={{ value: `+${forecast.remaining_to_t10_hours}h`, isPositive: false, label: 'remaining' }}
        />

        <MetricCard
          title="Predicted t₁₅ Threshold"
          value={formatHours(forecast.predicted_t15_hours)}
          icon={Clock}
          accentColor="indigo"
          subtitle="Analysis Threshold (15%)"
          trend={{ value: `+${forecast.remaining_to_t15_hours}h`, isPositive: false, label: 'remaining' }}
        />
      </div>

      {/* Trajectory Forecast Chart */}
      <ForecastTrajectoryChart
        data={forecast.trajectory}
        currentSimHour={forecast.origin_time_hours}
        currentDeclinePct={forecast.current_decline_pct}
      />

      {/* Threshold Analysis Ledger & Benchmark Accuracy */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* t5 Card */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-800">
              {forecast.thresholds.t5.label}
            </span>
            <StatusBadge status="5% Marker" variant="healthy" size="sm" />
          </div>
          <div className="text-sm font-bold text-slate-900">
            Crossed at t = {forecast.thresholds.t5.predicted_crossing_time_hours} h
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            {forecast.thresholds.t5.scientific_status}
          </p>
          <div className="pt-2 text-[11px] text-slate-400 font-mono">
            {forecast.thresholds.t5.lead_time_accuracy_note}
          </div>
        </div>

        {/* t10 Card */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-800">
              {forecast.thresholds.t10.label}
            </span>
            <StatusBadge status="10% Marker" variant="warning" size="sm" />
          </div>
          <div className="text-sm font-bold text-amber-700">
            Projected at t = {forecast.thresholds.t10.predicted_crossing_time_hours} h ({forecast.thresholds.t10.remaining_time_hours}h remaining)
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            {forecast.thresholds.t10.scientific_status}
          </p>
          <div className="pt-2 text-[11px] text-slate-400 font-mono">
            {forecast.thresholds.t10.lead_time_accuracy_note}
          </div>
        </div>

        {/* t15 Card */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-800">
              {forecast.thresholds.t15.label}
            </span>
            <StatusBadge status="15% Marker" variant="severe" size="sm" />
          </div>
          <div className="text-sm font-bold text-indigo-700">
            Projected at t = {forecast.thresholds.t15.predicted_crossing_time_hours} h ({forecast.thresholds.t15.remaining_time_hours}h remaining)
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            {forecast.thresholds.t15.scientific_status}
          </p>
          <div className="pt-2 text-[11px] text-slate-400 font-mono">
            {forecast.thresholds.t15.lead_time_accuracy_note}
          </div>
        </div>
      </div>

      {/* Uncertainty & API Status */}
      <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div>
          <span className="font-bold text-slate-700 block">Forecast Model Status</span>
          <span className="text-slate-500">Stage 8C Proactive Supervisory Predictor ({selectedHorizon}h Horizon)</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-slate-500">Uncertainty Bounds:</span>
          <span className="text-emerald-800 bg-emerald-100 px-2.5 py-1 rounded font-semibold">
            {forecast.uncertainty_status} (95% Confidence Band)
          </span>
        </div>
      </div>

      {/* Chemical Cleaning-In-Place (CIP) & Maintenance Advisor */}
      <CleaningAdvisor />

      {/* Digital Twin Timeline */}
      <Timeline />
    </div>
  );
}
