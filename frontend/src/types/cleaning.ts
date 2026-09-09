/**
 * Cleaning-In-Place (CIP) & Maintenance Advisor Types
 * Models chemical cleaning events that restore active layer permeability:
 *   R_f,new = (1 - eta_clean) * R_f,old
 */

export type CIPProtocolType = 'alkaline_organic' | 'acid_inorganic' | 'enzymatic_bio' | 'combined_two_step';

export interface CIPProtocol {
  id: CIPProtocolType;
  name: string;
  target_foulant: string;
  recommended_stage: 'Stage 1 (Lead Zones)' | 'Stage 2 (Tail Zones)' | 'All Stages';
  chemical_agent: string;
  ph_target: string;
  temperature_c: number;
  contact_time_min: number;
  typical_efficiency_pct: number;
  description: string;
}

export interface CleaningSimulationInput {
  cleaning_efficiency: number; // e.g. 0.90 for 90% removal of Rf
  protocol_id: CIPProtocolType;
  target_stages: 'both' | 'stage1_only' | 'stage2_only';
}

export interface CleaningSimulationResult {
  timestamp: string;
  protocol: CIPProtocol;
  efficiency_pct: number;
  initial_global_rf_m_inv: number;
  restored_global_rf_m_inv: number;
  initial_flux_decline_pct: number;
  restored_flux_decline_pct: number;
  initial_sec_kwh_m3: number;
  restored_sec_kwh_m3: number;
  sec_savings_kwh_m3: number;
  sec_reduction_pct: number;
  extended_operating_life_hours: number;
  chemical_cost_usd_est: number;
  net_energy_savings_usd_month: number;
  zone_restorations: {
    zone_id: string;
    zone_label: string;
    initial_rf_e12: number;
    restored_rf_e12: number;
    initial_decline_pct: number;
    restored_decline_pct: number;
  }[];
}
