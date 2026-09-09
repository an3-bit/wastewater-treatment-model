'use client';

import React from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  Legend,
} from 'recharts';
import { ParetoPoint } from '@/types/optimization';

interface ParetoChartProps {
  data: ParetoPoint[];
  onSelectPoint?: (point: ParetoPoint) => void;
}

export function ParetoChart({ data, onSelectPoint }: ParetoChartProps) {
  // Separate representative strategies and continuous pareto points
  const continuousPoints = data.filter((p) => !p.is_representative);
  const representativePoints = data.filter((p) => p.is_representative);

  const getStrategyColor = (tag?: string) => {
    switch (tag) {
      case 'Baseline':
        return '#64748b'; // slate-500
      case 'A':
        return '#0284c7'; // sky-600
      case 'B':
        return '#10b981'; // emerald-500
      case 'C':
        return '#8b5cf6'; // violet-500
      case 'D':
        return '#f59e0b'; // amber-500 (Balanced Knee)
      default:
        return '#0284c7';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            NSGA-II Non-Dominated Pareto Frontier
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Conflicting trade-off between Specific Energy Consumption (SEC) and Overall Water Recovery.
          </p>
        </div>

        {/* Strategy Badges Legend */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-500" />
            Baseline (Dominated)
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-sky-50 text-sky-800 font-medium border border-sky-200">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-600" />
            Strategy A (Max Rec)
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 font-medium border border-emerald-200">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            Strategy B (Min SEC)
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-violet-50 text-violet-800 font-medium border border-violet-200">
            <span className="w-2.5 h-2.5 rounded-full bg-violet-500" />
            Strategy C (Min Stress)
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-50 text-amber-900 font-bold border border-amber-300">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            Strategy D (Balanced Knee)
          </span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-80 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              type="number"
              dataKey="sec_kwh_m3"
              name="SEC"
              domain={[0.7, 0.85]}
              unit=" kWh/m³"
              tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'Specific Energy Consumption (SEC) [kWh/m³]', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 11 }}
            />
            <YAxis
              type="number"
              dataKey="recovery_pct"
              name="Recovery"
              domain={[45, 90]}
              unit="%"
              tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'Water Recovery [%]', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
            />
            <ZAxis type="number" dataKey="max_element_recovery_pct" range={[60, 240]} name="Max Element Stress" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const p = payload[0].payload as ParetoPoint;
                  return (
                    <div className="bg-white p-3 rounded-xl shadow-lg border border-slate-200 text-xs space-y-1">
                      <div className="font-bold text-slate-900 flex items-center justify-between gap-4">
                        <span>{p.strategy_tag ? `Strategy ${p.strategy_tag}` : `Pareto Solution #${p.id}`}</span>
                        <span className="text-slate-400 font-normal">P₁: {p.p1_bar} bar | P₂: {p.p2_bar} bar</span>
                      </div>
                      <div className="text-slate-600 flex justify-between">
                        <span>Water Recovery:</span>
                        <strong className="text-emerald-700">{p.recovery_pct}%</strong>
                      </div>
                      <div className="text-slate-600 flex justify-between">
                        <span>Specific Energy (SEC):</span>
                        <strong className="text-amber-700">{p.sec_kwh_m3} kWh/m³</strong>
                      </div>
                      <div className="text-slate-600 flex justify-between">
                        <span>Peak Element Recovery:</span>
                        <strong className="text-slate-800">{p.max_element_recovery_pct}%</strong>
                      </div>
                      <div className="text-slate-600 flex justify-between">
                        <span>Permeate TDS:</span>
                        <strong className="text-slate-800">{p.permeate_tds_mg_l} mg/L</strong>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            {/* Continuous Non-Dominated Frontier */}
            <Scatter name="Pareto Solutions (424 Points)" data={continuousPoints} fill="#38bdf8" opacity={0.65} />

            {/* Highlighted Representative Strategies */}
            <Scatter
              name="Representative Operating Strategies"
              data={representativePoints}
              shape="circle"
              onClick={(p) => onSelectPoint && onSelectPoint(p as any)}
            >
              {representativePoints.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={getStrategyColor(entry.strategy_tag)}
                  stroke="#ffffff"
                  strokeWidth={2}
                  r={8}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
        <span>Bubble size indicates maximum single-element recovery (R<sub>elem,max</sub> ≤ 30.0% constraint).</span>
        <span className="font-mono">Hypervolume = 2002.955 ± 0.758</span>
      </div>
    </div>
  );
}
