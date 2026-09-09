import React from 'react';

export type BadgeVariant =
  | 'healthy'
  | 'normal'
  | 'warning'
  | 'severe'
  | 'pareto'
  | 'dominated'
  | 'virtual'
  | 'neutral';

interface StatusBadgeProps {
  status: string;
  variant?: BadgeVariant;
  pulse?: boolean;
  size?: 'sm' | 'md';
}

export function StatusBadge({ status, variant, pulse = false, size = 'md' }: StatusBadgeProps) {
  // Infer variant if not provided
  let computedVariant: BadgeVariant = variant || 'neutral';
  const lower = status.toLowerCase();
  if (!variant) {
    if (lower.includes('healthy') || lower.includes('converged') || lower.includes('online')) {
      computedVariant = 'healthy';
    } else if (lower.includes('pareto') || lower.includes('optimal') || lower.includes('connected')) {
      computedVariant = 'pareto';
    } else if (lower.includes('approaching') || lower.includes('warning') || lower.includes('slow')) {
      computedVariant = 'warning';
    } else if (lower.includes('severe') || lower.includes('diverged') || lower.includes('offline') || lower.includes('dominated')) {
      computedVariant = 'severe';
    } else if (lower.includes('virtual') || lower.includes('v2.0') || lower.includes('model')) {
      computedVariant = 'virtual';
    } else {
      computedVariant = 'normal';
    }
  }

  const styles: Record<BadgeVariant, { bg: string; text: string; border: string; dot: string }> = {
    healthy: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700 font-medium',
      border: 'border-emerald-200',
      dot: 'bg-emerald-500',
    },
    normal: {
      bg: 'bg-sky-50',
      text: 'text-sky-700 font-medium',
      border: 'border-sky-200',
      dot: 'bg-sky-500',
    },
    warning: {
      bg: 'bg-amber-50',
      text: 'text-amber-800 font-medium',
      border: 'border-amber-200',
      dot: 'bg-amber-500',
    },
    severe: {
      bg: 'bg-rose-50',
      text: 'text-rose-700 font-medium',
      border: 'border-rose-200',
      dot: 'bg-rose-500',
    },
    pareto: {
      bg: 'bg-teal-50',
      text: 'text-teal-800 font-semibold',
      border: 'border-teal-200',
      dot: 'bg-teal-500',
    },
    dominated: {
      bg: 'bg-slate-100',
      text: 'text-slate-600 font-medium',
      border: 'border-slate-300',
      dot: 'bg-slate-400',
    },
    virtual: {
      bg: 'bg-indigo-50',
      text: 'text-indigo-700 font-medium',
      border: 'border-indigo-200',
      dot: 'bg-indigo-500',
    },
    neutral: {
      bg: 'bg-slate-50',
      text: 'text-slate-700 font-medium',
      border: 'border-slate-200',
      dot: 'bg-slate-400',
    },
  };

  const currentStyle = styles[computedVariant] || styles.neutral;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${currentStyle.bg} ${currentStyle.text} ${currentStyle.border} ${sizeClasses}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${currentStyle.dot} ${pulse ? 'animate-pulse' : ''}`}
      />
      {status}
    </span>
  );
}
