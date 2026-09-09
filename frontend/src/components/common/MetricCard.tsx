import React from 'react';
import { LucideIcon } from 'lucide-react';
import { EngineeringTooltip } from './EngineeringTooltip';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon?: LucideIcon;
  tooltipTerm?: string;
  customTooltip?: string;
  trend?: {
    value: string;
    isPositive?: boolean;
    label?: string;
  };
  accentColor?: 'emerald' | 'sky' | 'amber' | 'indigo' | 'slate';
  badge?: React.ReactNode;
  subtitle?: string;
  simulated?: boolean;
}

export function MetricCard({
  title,
  value,
  unit,
  icon: Icon,
  tooltipTerm,
  customTooltip,
  trend,
  accentColor = 'slate',
  badge,
  subtitle,
  simulated = true,
}: MetricCardProps) {
  const accentBorders = {
    emerald: 'border-l-emerald-500',
    sky: 'border-l-sky-500',
    amber: 'border-l-amber-500',
    indigo: 'border-l-indigo-500',
    slate: 'border-l-slate-300',
  };

  const iconColors = {
    emerald: 'text-emerald-600 bg-emerald-50',
    sky: 'text-sky-600 bg-sky-50',
    amber: 'text-amber-600 bg-amber-50',
    indigo: 'text-indigo-600 bg-indigo-50',
    slate: 'text-slate-600 bg-slate-100',
  };

  return (
    <div
      className={`bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-sm border-l-4 ${accentBorders[accentColor]} hover:shadow-md transition-shadow relative`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </span>
          {(tooltipTerm || customTooltip) && (
            <EngineeringTooltip term={tooltipTerm || title} customText={customTooltip} />
          )}
        </div>

        <div className="flex items-center gap-1.5">
          {badge}
          {Icon && (
            <div className={`p-2 rounded-lg ${iconColors[accentColor]}`}>
              <Icon className="w-4 h-4" />
            </div>
          )}
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          {value}
        </span>
        {unit && <span className="text-sm font-medium text-slate-500">{unit}</span>}
      </div>

      <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-100 text-xs">
        {subtitle && <span className="text-slate-500">{subtitle}</span>}
        {trend && (
          <span
            className={`font-medium ${
              trend.isPositive ? 'text-emerald-600' : 'text-amber-600'
            }`}
          >
            {trend.value} <span className="text-slate-400 font-normal">{trend.label || ''}</span>
          </span>
        )}
        {simulated && (
          <span className="text-[10px] font-mono text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200">
            Simulated
          </span>
        )}
      </div>
    </div>
  );
}
