'use client';

import React, { useState } from 'react';
import {
  Layers,
  Activity,
  CheckCircle2,
  Cpu,
  Info,
} from 'lucide-react';

export function ProcessArchitecture() {
  const [selectedNode, setSelectedNode] = useState<'feed' | 'stage1' | 'booster' | 'stage2' | 'permeate' | 'concentrate'>('stage1');

  const nodeDetails = {
    feed: {
      title: 'Equalized Textile Effluent Feed Inlet',
      specs: 'Q_f = 30.00 m³/h • C_f = 2,041 mg/L TDS • Temp = 25.0°C',
      description:
        'Raw pretreated textile dye wastewater containing high total dissolved solids and reactive dye hydrolysates entering the RO feed manifold at atmospheric pressure.',
      badge: 'Feed Inflow (100%)',
    },
    stage1: {
      title: 'Stage 1 RO Pressure Vessels (3 Vessels × 3 Elements)',
      specs: 'Feed Pressure = 16.06 bar • 9 Elements (Toray TM720D-400) • Recovery = 52.7%',
      description:
        'Three parallel pressure vessels operating under first-principles Spiegler-Kedem transport. Generates 15.82 m³/h of ultra-pure permeate with 5.8 mg/L TDS.',
      badge: '3 Parallel Vessels',
    },
    booster: {
      title: 'Interstage Booster Pump Subsystem',
      specs: 'Boost = +0.35 bar • Inlet Pressure = 16.06 bar → Stage 2 Feed = 16.41 bar',
      description:
        'Re-energizes the concentrated brine from Stage 1 to overcome increasing osmotic pressure in Stage 2, preserving uniform flux and minimizing tail-element scaling.',
      badge: 'Hydraulic Booster',
    },
    stage2: {
      title: 'Stage 2 RO Pressure Vessels (2 Vessels × 3 Elements)',
      specs: 'Feed Pressure = 16.41 bar • 6 Elements (Toray TM720D-400) • Permeate = 5.24 m³/h',
      description:
        'Two parallel pressure vessels receiving concentrated brine (4,312 mg/L TDS). Produces 5.24 m³/h permeate and brings overall plant recovery to 70.22%.',
      badge: '2 Parallel Vessels',
    },
    permeate: {
      title: 'High-Purity Permeate Reclaim Manifold',
      specs: 'Q_p,total = 21.06 m³/h • C_p,total = 7.21 mg/L TDS • Recovery = 70.22%',
      description:
        'Combined permeate streams from Stage 1 and Stage 2 exceeding textile wet processing reuse standards (TDS < 50 mg/L, COD < 10 mg/L).',
      badge: 'Product Water',
    },
    concentrate: {
      title: 'Concentrate / Brine Discharge Stream',
      specs: 'Q_c = 8.94 m³/h • C_c = 6,835.4 mg/L TDS • Strict Mass Balance',
      description:
        'High-salinity brine routed to downstream evaporation or zero liquid discharge (ZLD) crystallizers. Strict mathematical closure verified.',
      badge: 'ZLD Brine Line',
    },
  };

  return (
    <section id="architecture" className="py-20 bg-white text-slate-900 relative">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 space-y-12">
        
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-sky-50 border border-sky-200 text-xs font-semibold text-sky-800 shadow-2xs">
            <Layers className="w-3.5 h-3.5 text-sky-600" />
            <span>Authoritative 3:2 Staging Configuration</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            15 Physical Elements in a 2-Stage Staging Array
          </h2>
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
            Click on any process block in the flow sheet below to inspect real-time hydraulic pressures, flow rates, and solute concentration dynamics.
          </p>
        </div>

        {/* 3D Digital Twin Visualization & Interactive Diagram */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left: 3D Membrane Digital Twin Cutaway Image */}
          <div className="lg:col-span-5 relative rounded-3xl overflow-hidden border border-slate-200 shadow-md group">
            <img
              src="/images/digital_twin_model.jpg"
              alt="3D Digital Twin Membrane Model"
              className="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-md text-slate-900 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-mono flex items-center gap-2 shadow-xs">
              <span className="w-2 h-2 rounded-full bg-sky-600 animate-pulse" />
              <span>Toray TM720D-400 Element Cross-Section</span>
            </div>
          </div>

          {/* Right: Interactive Node Blocks */}
          <div className="lg:col-span-7 space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {/* Feed Node */}
              <button
                type="button"
                onClick={() => setSelectedNode('feed')}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  selectedNode === 'feed'
                    ? 'border-sky-500 bg-sky-50/80 ring-2 ring-sky-500/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <span className="text-[10px] font-mono text-sky-700 uppercase font-bold block mb-1">
                  Inlet Stream
                </span>
                <span className="text-xs font-bold text-slate-900 block">Raw Feed</span>
                <span className="text-[11px] font-mono text-slate-500 block mt-1">30.0 m³/h</span>
              </button>

              {/* Stage 1 Node */}
              <button
                type="button"
                onClick={() => setSelectedNode('stage1')}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  selectedNode === 'stage1'
                    ? 'border-sky-500 bg-sky-50/80 ring-2 ring-sky-500/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <span className="text-[10px] font-mono text-sky-700 uppercase font-bold block mb-1">
                  Stage 1 (3 Vess.)
                </span>
                <span className="text-xs font-bold text-slate-900 block">9 Elements</span>
                <span className="text-[11px] font-mono text-slate-500 block mt-1">16.06 bar</span>
              </button>

              {/* Booster Node */}
              <button
                type="button"
                onClick={() => setSelectedNode('booster')}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  selectedNode === 'booster'
                    ? 'border-indigo-500 bg-indigo-50/80 ring-2 ring-indigo-500/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <span className="text-[10px] font-mono text-indigo-700 uppercase font-bold block mb-1">
                  Booster Pump
                </span>
                <span className="text-xs font-bold text-slate-900 block">+0.35 bar</span>
                <span className="text-[11px] font-mono text-slate-500 block mt-1">14.18 m³/h</span>
              </button>

              {/* Stage 2 Node */}
              <button
                type="button"
                onClick={() => setSelectedNode('stage2')}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  selectedNode === 'stage2'
                    ? 'border-purple-500 bg-purple-50/80 ring-2 ring-purple-500/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <span className="text-[10px] font-mono text-purple-700 uppercase font-bold block mb-1">
                  Stage 2 (2 Vess.)
                </span>
                <span className="text-xs font-bold text-slate-900 block">6 Elements</span>
                <span className="text-[11px] font-mono text-slate-500 block mt-1">16.41 bar</span>
              </button>

              {/* Permeate Node */}
              <button
                type="button"
                onClick={() => setSelectedNode('permeate')}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  selectedNode === 'permeate'
                    ? 'border-emerald-500 bg-emerald-50/80 ring-2 ring-emerald-500/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <span className="text-[10px] font-mono text-emerald-700 uppercase font-bold block mb-1">
                  Product Stream
                </span>
                <span className="text-xs font-bold text-slate-900 block">Permeate Reclaim</span>
                <span className="text-[11px] font-mono text-emerald-600 block mt-1">21.06 m³/h</span>
              </button>

              {/* Concentrate Node */}
              <button
                type="button"
                onClick={() => setSelectedNode('concentrate')}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  selectedNode === 'concentrate'
                    ? 'border-amber-500 bg-amber-50/80 ring-2 ring-amber-500/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <span className="text-[10px] font-mono text-amber-700 uppercase font-bold block mb-1">
                  Discharge
                </span>
                <span className="text-xs font-bold text-slate-900 block">Concentrate</span>
                <span className="text-[11px] font-mono text-amber-600 block mt-1">8.94 m³/h</span>
              </button>
            </div>

            {/* Selected Node Details Card */}
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-sky-600" />
                  <h3 className="text-base font-bold text-slate-900">
                    {nodeDetails[selectedNode].title}
                  </h3>
                </div>
                <span className="text-xs font-mono font-bold bg-white border border-slate-200 px-3 py-1 rounded-lg text-sky-800 shadow-2xs self-start sm:self-auto">
                  {nodeDetails[selectedNode].badge}
                </span>
              </div>

              <div className="text-xs font-mono text-sky-900 bg-sky-100/60 px-3.5 py-2 rounded-xl border border-sky-200/80">
                {nodeDetails[selectedNode].specs}
              </div>

              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                {nodeDetails[selectedNode].description}
              </p>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
