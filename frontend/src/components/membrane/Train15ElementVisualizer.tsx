import React from 'react';
import { PhysicalElementMapping } from '@/types/membrane';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Layers, AlertCircle } from 'lucide-react';
import { formatPercent } from '@/utils/formatters';

interface Train15ElementVisualizerProps {
  elements: PhysicalElementMapping[];
}

export function Train15ElementVisualizer({ elements }: Train15ElementVisualizerProps) {
  // Separate elements by Stage
  const stage1Elements = elements.filter((e) => e.stage === 1);
  const stage2Elements = elements.filter((e) => e.stage === 2);

  // Group by Vessel
  const s1Vessels = [1, 2, 3].map((vIdx) => stage1Elements.filter((e) => e.vessel_index === vIdx));
  const s2Vessels = [1, 2].map((vIdx) => stage2Elements.filter((e) => e.vessel_index === vIdx));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-emerald-500 text-white';
      case 'normal':
        return 'bg-sky-500 text-white';
      case 'approaching_threshold':
        return 'bg-amber-500 text-white';
      case 'severe_warning':
        return 'bg-rose-500 text-white';
      default:
        return 'bg-slate-400 text-white';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-6">
      {/* Header & Scientific Notice */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-5 h-5 text-sky-600" />
            15-Element Physical Membrane Train Mapping
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Physical layout of Toray TM720D-400 elements mapped to the authoritative 6-zone axial state estimator.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-emerald-500" />
            <span className="text-slate-600">Lead Zone</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-sky-500" />
            <span className="text-slate-600">Mid Zone</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-amber-500" />
            <span className="text-slate-600">Tail Zone (High Salt)</span>
          </span>
        </div>
      </div>

      {/* Observability Boundary Banner */}
      <div className="bg-sky-50/70 border border-sky-200 rounded-xl p-3 text-xs text-sky-950 flex items-start gap-2.5">
        <AlertCircle className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="font-semibold text-sky-900">Observability Notice:</strong> Parallel vessels within each stage share identical boundary feed pressures and salinities. To avoid rank-deficiency (dim n = 15, rank 4, κ = ∞), the Stage 7 EKF operates on the recommended <strong>6-zone axial state representation</strong> (n = 6). The 15 elements below reflect this axial projection.
        </div>
      </div>

      {/* Membrane Stages Graphic Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stage 1 Vessels (3 parallel vessels) */}
        <div className="space-y-3 bg-slate-50/60 p-4 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">
              Stage 1 (3 Vessels × 3 Elements in Series)
            </span>
            <span className="text-[10px] font-mono text-slate-500">9 Elements (333 m²)</span>
          </div>

          <div className="space-y-2.5">
            {s1Vessels.map((vesselElems, vIdx) => (
              <div key={vIdx} className="bg-white p-3 rounded-lg border border-slate-200 space-y-1.5">
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span className="font-semibold text-slate-700">Pressure Vessel #{vIdx + 1}</span>
                  <span>Inlet P₁ = 16.06 bar</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {vesselElems.map((elem) => (
                    <div
                      key={elem.element_id}
                      className="bg-slate-50 rounded-md p-2 border border-slate-200 text-center hover:bg-slate-100 transition-colors"
                    >
                      <div className="text-[10px] font-bold text-slate-700">{elem.element_label}</div>
                      <div className="text-[10px] text-slate-500">{elem.zone_label.split(' ')[2]}</div>
                      <div className="mt-1">
                        <span
                          className={`inline-block px-1.5 py-0.2 rounded text-[10px] font-mono font-semibold ${getStatusColor(
                            elem.status
                          )}`}
                        >
                          -{formatPercent(elem.permeability_decline_pct, 1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stage 2 Vessels (2 parallel vessels) */}
        <div className="space-y-3 bg-slate-50/60 p-4 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">
              Stage 2 (2 Vessels × 3 Elements in Series)
            </span>
            <span className="text-[10px] font-mono text-slate-500">6 Elements (222 m²)</span>
          </div>

          <div className="space-y-2.5">
            {s2Vessels.map((vesselElems, vIdx) => (
              <div key={vIdx} className="bg-white p-3 rounded-lg border border-slate-200 space-y-1.5">
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span className="font-semibold text-slate-700">Pressure Vessel #{vIdx + 1}</span>
                  <span>Booster P₂ = 16.41 bar</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {vesselElems.map((elem) => (
                    <div
                      key={elem.element_id}
                      className="bg-slate-50 rounded-md p-2 border border-slate-200 text-center hover:bg-slate-100 transition-colors"
                    >
                      <div className="text-[10px] font-bold text-slate-700">{elem.element_label}</div>
                      <div className="text-[10px] text-slate-500">{elem.zone_label.split(' ')[2]}</div>
                      <div className="mt-1">
                        <span
                          className={`inline-block px-1.5 py-0.2 rounded text-[10px] font-mono font-semibold ${getStatusColor(
                            elem.status
                          )}`}
                        >
                          -{formatPercent(elem.permeability_decline_pct, 1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
