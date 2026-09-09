'use client';

import React, { useState, useEffect } from 'react';
import {
  Layers,
  Activity,
  Cpu,
  TrendingUp,
  ShieldCheck,
  Filter,
} from 'lucide-react';
import { membraneService } from '@/services/membraneService';
import {
  MembraneZoneState,
  PhysicalElementMapping,
  AxialFoulingPoint,
  EKFEstimatorStatus,
} from '@/types/membrane';
import { MembraneZoneCard } from '@/components/membrane/MembraneZoneCard';
import { Train15ElementVisualizer } from '@/components/membrane/Train15ElementVisualizer';
import { AxialFoulingChart } from '@/components/membrane/AxialFoulingChart';
import { EKFStatusPanel } from '@/components/membrane/EKFStatusPanel';
import { CleaningAdvisor } from '@/components/membrane/CleaningAdvisor';
import { Timeline } from '@/components/common/Timeline';
import { StatusBadge } from '@/components/common/StatusBadge';

export default function MembraneHealthPage() {
  const [zones, setZones] = useState<MembraneZoneState[]>([]);
  const [elements, setElements] = useState<PhysicalElementMapping[]>([]);
  const [axialData, setAxialData] = useState<AxialFoulingPoint[]>([]);
  const [ekfStatus, setEkfStatus] = useState<EKFEstimatorStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [z, el, ax, ekf] = await Promise.all([
          membraneService.getMembraneZones(),
          membraneService.getPhysicalElements(),
          membraneService.getAxialFoulingProfile(),
          membraneService.getEKFStatus(),
        ]);
        setZones(z);
        setElements(el);
        setAxialData(ax);
        setEkfStatus(ekf);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !ekfStatus) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-200 rounded w-1/4" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
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
              Membrane Health & EKF Virtual Sensor
            </h2>
            <StatusBadge status="Stage 7 Virtual Sensor" variant="healthy" />
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time reconstruction of unmeasured axial fouling resistance ($R_f$) across the 6-zone state representation.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg text-xs text-emerald-800">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Extended Kalman Filter Converged (~105 ms)</span>
        </div>
      </div>

      {/* Six Axial Membrane Zone Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
            <Layers className="w-4 h-4 text-sky-600" />
            Authoritative 6-Zone Axial States (n = 6)
          </h3>
          <span className="text-xs text-slate-400">Toray TM720D-400 Calibration</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {zones.map((zone) => (
            <MembraneZoneCard key={zone.zone_id} zone={zone} />
          ))}
        </div>
      </div>

      {/* 15-Element Physical Train Graphical Visualizer */}
      <Train15ElementVisualizer elements={elements} />

      {/* Axial Fouling Profile Chart */}
      <AxialFoulingChart data={axialData} />

      {/* Chemical Cleaning-in-Place (CIP) & Maintenance Advisor */}
      <CleaningAdvisor />

      {/* EKF Estimator Status Panel */}
      <EKFStatusPanel status={ekfStatus} />

      {/* Reusable Digital Twin Timeline */}
      <Timeline />
    </div>
  );
}
