'use client';

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ReferenceDot,
} from 'recharts';
import { ForecastTrajectoryPoint } from '@/types/forecast';

interface ForecastTrajectoryChartProps {
  data: ForecastTrajectoryPoint[];
  currentSimHour?: number;
  currentDeclinePct?: number;
}

export function ForecastTrajectoryChart({
  data,
  currentSimHour = 48.0,
  currentDeclinePct = 5.42,
}: ForecastTrajectoryChartProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Fouling Permeability Decline & Threshold Forecast Trajectory
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Physics-informed forward dynamic simulation from current EKF estimated state (t = {currentSimHour} h).
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5 text-slate-600">
            <span className="w-3 h-0.5 bg-sky-600" />
            <span>Historical EKF</span>
          </span>
          <span className="flex items-center gap-1.5 text-slate-600">
            <span className="w-3 h-0.5 bg-indigo-600 border-dashed border-t-2" />
            <span>Forward Forecast</span>
          </span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-80 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 40, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="time_hours"
              tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'Operating Horizon [hours]', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 11 }}
            />
            <YAxis
              domain={[0, 18]}
              tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'Permeability Decline [%]', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
            />
            <Tooltip
              formatter={(val: any, name: any) => {
                if (val === null || val === undefined) return [null, null];
                return [`${val}%`, name === 'historical_decline_pct' ? 'Historical Decline' : 'Forecast Trajectory'];
              }}
              labelFormatter={(label) => `Time: ${label} hours`}
              contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
            />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />

            {/* Analysis Threshold Reference Lines */}
            <ReferenceLine
              y={5.0}
              stroke="#10b981"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ value: 't₅ Analysis Threshold (5%)', fill: '#10b981', fontSize: 11, position: 'right' }}
            />
            <ReferenceLine
              y={10.0}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ value: 't₁₀ Analysis Threshold (10%)', fill: '#f59e0b', fontSize: 11, position: 'right' }}
            />
            <ReferenceLine
              y={15.0}
              stroke="#ef4444"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ value: 't₁₅ Analysis Threshold (15%)', fill: '#ef4444', fontSize: 11, position: 'right' }}
            />

            {/* Vertical Marker for NOW (Current Time) */}
            <ReferenceLine
              x={currentSimHour}
              stroke="#6366f1"
              strokeWidth={2}
              label={{ value: `NOW (t = ${currentSimHour}h)`, fill: '#6366f1', fontSize: 11, position: 'top' }}
            />

            {/* Current State Marker Dot */}
            <ReferenceDot
              x={currentSimHour}
              y={currentDeclinePct}
              r={6}
              fill="#6366f1"
              stroke="#ffffff"
              strokeWidth={2}
            />

            {/* Historical Decline (Solid) */}
            <Line
              type="monotone"
              dataKey="historical_decline_pct"
              name="Historical Estimated Decline"
              stroke="#0284c7"
              strokeWidth={2.5}
              dot={false}
              connectNulls={false}
            />

            {/* Forecast Trajectory (Dashed) */}
            <Line
              type="monotone"
              dataKey="forecast_decline_pct"
              name="Predicted Forward Trajectory"
              stroke="#6366f1"
              strokeWidth={2.5}
              strokeDasharray="5 5"
              dot={false}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <span className="text-amber-800 bg-amber-50 px-2.5 py-1 rounded-md border border-amber-200">
          <strong>Notice:</strong> Analysis thresholds (t₅, t₁₀, t₁₅) represent progressive evaluation horizons, not automated cleaning triggers.
        </span>
        <span className="font-mono text-slate-400">Stage 7 Forecaster</span>
      </div>
    </div>
  );
}
