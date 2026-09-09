'use client';

import React from 'react';
import { SensorReading } from '@/types/sensors';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Gauge, Activity, Droplets, Thermometer, Zap } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, YAxis } from 'recharts';

interface SensorCardProps {
  sensor: SensorReading;
}

export function SensorCard({ sensor }: SensorCardProps) {
  const categoryIcons = {
    hydraulic: Gauge,
    quality: Droplets,
    thermal: Thermometer,
    energy: Zap,
  };

  const Icon = categoryIcons[sensor.category] || Activity;

  // Format sparkline data
  const sparklineData = sensor.history_sparkline.map((val, idx) => ({
    i: idx,
    val,
  }));

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div>
        {/* Top Tag & Status */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-slate-100 text-slate-700">
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] font-mono font-bold text-sky-700 block">
                {sensor.tag}
              </span>
              <h4 className="text-sm font-bold text-slate-900 leading-tight">
                {sensor.name}
              </h4>
            </div>
          </div>
          <StatusBadge status={sensor.status} variant={sensor.status === 'Online' ? 'healthy' : 'warning'} size="sm" />
        </div>

        {/* Current Reading */}
        <div className="flex items-baseline gap-2 my-3">
          <span className="text-2xl font-bold font-mono text-slate-900">
            {sensor.current_value.toLocaleString(undefined, {
              minimumFractionDigits: sensor.unit === 'bar' ? 2 : sensor.unit === 'mg/L' ? 1 : 2,
              maximumFractionDigits: 2,
            })}
          </span>
          <span className="text-xs font-semibold text-slate-500">{sensor.unit}</span>
        </div>

        {/* Mini Sparkline Graph */}
        <div className="h-12 w-full my-2 bg-slate-50 rounded-lg p-1 border border-slate-100">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sparklineData}>
              <YAxis domain={['dataMin', 'dataMax']} hide />
              <Line
                type="monotone"
                dataKey="val"
                stroke="#0284c7"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Metadata Footer */}
      <div className="pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span className="truncate max-w-[160px] text-slate-400" title={sensor.location}>
          {sensor.location}
        </span>
        <span className="text-slate-400">σ = ±{sensor.noise_std}</span>
      </div>
    </div>
  );
}
