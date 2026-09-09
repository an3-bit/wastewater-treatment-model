import { CIPProtocol, CleaningSimulationInput, CleaningSimulationResult } from '@/types/cleaning';
import { mockMembraneZones } from './mockMembranes';

export const mockCIPProtocols: CIPProtocol[] = [
  {
    id: 'alkaline_organic',
    name: 'Alkaline Organic & Dye Stripping (NaOH + SDS)',
    target_foulant: 'Textile Reactive Dyes, Surfactants, Biofilm Cake Layer',
    recommended_stage: 'Stage 1 (Lead Zones)',
    chemical_agent: '0.1% NaOH (w/w) + 0.05% Sodium Dodecyl Sulfate',
    ph_target: 'pH 11.0 – 11.5',
    temperature_c: 35.0,
    contact_time_min: 45,
    typical_efficiency_pct: 92.0,
    description:
      'Highly effective for hydrolyzing organic macromolecules and solubilizing dye matrices deposited on lead membrane active layers.',
  },
  {
    id: 'acid_inorganic',
    name: 'Inorganic Mineral Descaling (Citric Acid / HCl)',
    target_foulant: 'Calcium Carbonate, Calcium Sulfate, Silica Colloid Scale',
    recommended_stage: 'Stage 2 (Tail Zones)',
    chemical_agent: '2.0% Citric Acid or 0.2% HCl',
    ph_target: 'pH 2.0 – 2.5',
    temperature_c: 25.0,
    contact_time_min: 30,
    typical_efficiency_pct: 95.0,
    description:
      'Dissolves inorganic precipitate crystals and scale that concentrate in high-salinity tail vessels (Stage 2 elements).',
  },
  {
    id: 'combined_two_step',
    name: 'Two-Step Standard Industrial Protocol (Alkaline → Acid)',
    target_foulant: 'Mixed Textile Wastewater Multi-Layer Cake & Scale',
    recommended_stage: 'All Stages',
    chemical_agent: 'Step 1: 0.1% NaOH (pH 11.5) followed by Step 2: 2.0% Citric Acid (pH 2.2)',
    ph_target: 'pH 11.5 then pH 2.2',
    temperature_c: 30.0,
    contact_time_min: 90,
    typical_efficiency_pct: 96.5,
    description:
      'Full restorative treatment removing organic surface fouling first, followed by dissolution of mineral scaling crystals.',
  },
  {
    id: 'enzymatic_bio',
    name: 'Enzymatic Mild Bio-Disruption',
    target_foulant: 'Extracellular Polymeric Substances (EPS) & Biofilm',
    recommended_stage: 'Stage 1 (Lead Zones)',
    chemical_agent: '0.05% Protease / Cellulase Enzyme Complex',
    ph_target: 'pH 7.5 – 8.5',
    temperature_c: 32.0,
    contact_time_min: 60,
    typical_efficiency_pct: 88.0,
    description:
      'Non-damaging enzymatic cleavage of protein and polysaccharide biofilm matrices with zero pH shock.',
  },
];

export function calculateCleaningSimulation(input: CleaningSimulationInput): CleaningSimulationResult {
  const protocol =
    mockCIPProtocols.find((p) => p.id === input.protocol_id) || mockCIPProtocols[0];
  const eta = Math.max(0.5, Math.min(0.99, input.cleaning_efficiency));

  const initialGlobalRf = 5.25e12; // Baseline avg Rf [m^-1]
  const Rm = 9.77e13; // Clean Toray membrane resistance [m^-1]

  const restoredZones = mockMembraneZones.map((z) => {
    let applyRestoration = true;
    if (input.target_stages === 'stage1_only' && z.stage_number !== 1) applyRestoration = false;
    if (input.target_stages === 'stage2_only' && z.stage_number !== 2) applyRestoration = false;

    const currentRf = z.rf_m_inv;
    const restoredRf = applyRestoration ? (1.0 - eta) * currentRf : currentRf;

    const initialDecline = (currentRf / (Rm + currentRf)) * 100.0;
    const restoredDecline = (restoredRf / (Rm + restoredRf)) * 100.0;

    return {
      zone_id: z.zone_id,
      zone_label: z.zone_label,
      initial_rf_e12: Number((currentRf / 1e12).toFixed(2)),
      restored_rf_e12: Number((restoredRf / 1e12).toFixed(2)),
      initial_decline_pct: Number(initialDecline.toFixed(2)),
      restored_decline_pct: Number(restoredDecline.toFixed(2)),
    };
  });

  const avgInitialRf =
    restoredZones.reduce((acc, z) => acc + z.initial_rf_e12 * 1e12, 0) / restoredZones.length;
  const avgRestoredRf =
    restoredZones.reduce((acc, z) => acc + z.restored_rf_e12 * 1e12, 0) / restoredZones.length;

  const initialFluxDecline = (avgInitialRf / (Rm + avgInitialRf)) * 100.0;
  const restoredFluxDecline = (avgRestoredRf / (Rm + avgRestoredRf)) * 100.0;

  const initialSec = 0.7269; // kWh/m3
  const restoredSec = initialSec * (1.0 - (initialFluxDecline - restoredFluxDecline) * 0.008);
  const secSavings = initialSec - restoredSec;
  const secReductionPct = (secSavings / initialSec) * 100.0;

  // Extended life calculation (hours back to t10 threshold)
  const extendedHours = Number(((eta * 48.0) * 1.75).toFixed(1));

  // Economic estimation ($0.12/kWh industrial electricity, 30 m3/h, 21 m3/h permeate)
  const energyKwhPerMonth = 21.07 * secSavings * 24 * 30; // kWh saved / month
  const netEnergySavingsMonthly = energyKwhPerMonth * 0.12; // USD / month
  const chemicalCostEst = 45.0 + (input.target_stages === 'both' ? 35.0 : 0.0);

  return {
    timestamp: new Date().toISOString(),
    protocol,
    efficiency_pct: Number((eta * 100.0).toFixed(1)),
    initial_global_rf_m_inv: avgInitialRf,
    restored_global_rf_m_inv: avgRestoredRf,
    initial_flux_decline_pct: Number(initialFluxDecline.toFixed(2)),
    restored_flux_decline_pct: Number(restoredFluxDecline.toFixed(2)),
    initial_sec_kwh_m3: Number(initialSec.toFixed(4)),
    restored_sec_kwh_m3: Number(restoredSec.toFixed(4)),
    sec_savings_kwh_m3: Number(secSavings.toFixed(4)),
    sec_reduction_pct: Number(secReductionPct.toFixed(2)),
    extended_operating_life_hours: extendedHours,
    chemical_cost_usd_est: chemicalCostEst,
    net_energy_savings_usd_month: Number(netEnergySavingsMonthly.toFixed(2)),
    zone_restorations: restoredZones,
  };
}
