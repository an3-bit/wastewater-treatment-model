'use client';

import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { AxialFoulingPoint } from '@/types/membrane';

interface AxialFoulingChartProps {
  data: AxialFoulingPoint[];
}

export function AxialFoulingChart({ data }: AxialFoulingChartProps) {
  const [metric, setMetric] = useState<'rf' | 'permeability' | 'decline'>('rf');

  const configs = {
    rf: {
      dataKey: 'rf_e12',
      name: 'Fouling Resistance Rf (×10¹² m⁻¹)',
      unit: '×10¹² m⁻¹',
      color: '#0284c7', // sky-600
      yLabel: 'Resistance Rf [10¹² m⁻¹]',
      domain: [0, 14],
    },
    permeability: {
      dataKey: 'permeability_lmh_bar',
      name: 'Normalized Permeability (LMH/bar)',
      unit: 'LMH/bar',
      color: '#10b981', // emerald-500
      yLabel: 'Permeability [LMH/bar]',
      domain: [2.5, 4.0],
    },
    decline: {
      dataKey: 'decline_pct',
      name: 'Permeability Decline (%)',
      unit: '%',
      color: '#f59e0b', // amber-500
      yLabel: 'Flux Decline [%]',
      domain: [0, 16],
    },
  };

  const currentConfig = configs[metric];

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
      {/* Header with Toggle Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Axial Membrane Fouling & Permeability Profile
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Spatial distribution across the 6-zone axial coordinate (Stage 1 Lead → Stage 2 Tail).
          </p>
        </div>

        {/* Metric Toggles */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setMetric('rf')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              metric === 'rf'
                ? 'bg-white text-sky-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Resistance (Rf)
          </button>
          <button
            onClick={() => setMetric('permeability')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              metric === 'permeability'
                ? 'bg-white text-emerald-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Permeability
          </button>
          <button
            onClick={() => setMetric('decline')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              metric === 'decline'
                ? 'bg-white text-amber-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Decline %
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="zone_name"
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
            />
            <YAxis
              domain={currentConfig.domain as [number, number]}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              label={{
                value: currentConfig.yLabel,
                angle: -90,
                position: 'insideLeft',
                fill: '#64748b',
                fontSize: 11,
              }}
            />
            <Tooltip
              formatter={(value: any) => [`${value} ${currentConfig.unit}`, currentConfig.name]}
              labelFormatter={(label) => `Zone: ${label}`}
              contentStyle={{
                backgroundColor: '#ffffff',
                borderColor: '#e2e8f0',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />

            {metric === 'decline' && (
              <>
                <ReferenceLine
                  y={5.0}
                  stroke="#10b981"
                  strokeDasharray="4 4"
                  label={{ value: 't5 Threshold (5%)', fill: '#10b981', fontSize: 10, position: 'right' }}
                />
                <ReferenceLine
                  y={10.0}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  label={{ value: 't10 Threshold (10%)', fill: '#f59e0b', fontSize: 10, position: 'right' }}
                />
              </>
            )}

            <Bar
              dataKey={currentConfig.dataKey}
              name={currentConfig.name}
              fill={currentConfig.color}
              radius={[6, 6, 0, 0]}
              maxBarSize={48}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
        <span>Lead element fouling is flux-dominated; Tail element fouling is salinity/concentration polarization-dominated.</span>
        <span className="font-mono">Stage 7 Mechanistic EKF</span>
      </div>
    </div>
  );
}
