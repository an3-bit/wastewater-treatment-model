/**
 * Membrane Health & Stage 7 EKF Virtual Sensor Types
 * Authoritative 6-Zone Axial Representation (n = 6) mapped across 15 physical elements
 */

export type MembraneHealthStatus = 'healthy' | 'normal' | 'approaching_threshold' | 'severe_warning';
export type FoulingTrend = 'stable' | 'slow_growth' | 'rapid_growth' | 'improving';

export interface MembraneZoneState {
  zone_id: string; // 'S1_Lead', 'S1_Mid', 'S1_Tail', 'S2_Lead', 'S2_Mid', 'S2_Tail'
  stage_number: 1 | 2;
  position_name: 'Lead' | 'Middle' | 'Tail';
  zone_label: string; // e.g. "Stage 1 — Lead Zone"
  rf_m_inv: number; // Estimated fouling resistance [m^-1]
  rf_formatted: string; // e.g. "3.42 x 10^12 m^-1"
  normalized_permeability_lmh_bar: number; // [LMH/bar]
  permeability_decline_pct: number; // e.g. 6.4%
  state_confidence_pct: number; // e.g. 96.8%
  status: MembraneHealthStatus;
  trend: FoulingTrend;
  element_indices: number[]; // e.g. [0, 3, 6] for S1_Lead
  vessels_represented: string; // e.g. "V1-E1, V2-E1, V3-E1"
}

export interface PhysicalElementMapping {
  element_id: number; // 0 to 14 (15 physical elements)
  stage: 1 | 2;
  vessel_index: number; // 1 to 3 for S1, 1 to 2 for S2
  position_in_vessel: 1 | 2 | 3; // 1=Lead, 2=Mid, 3=Tail
  zone_id: string;
  zone_label: string;
  element_label: string; // e.g. "S1-V1-E1"
  rf_m_inv: number;
  permeability_decline_pct: number;
  status: MembraneHealthStatus;
}

export interface AxialFoulingPoint {
  position_index: number;
  zone_name: string;
  stage: number;
  position_category: string;
  rf_m_inv: number;
  rf_e12: number; // scaled for charts: 10^12 m^-1
  permeability_lmh_bar: number;
  decline_pct: number;
  threshold_5pct: number;
  threshold_10pct: number;
  threshold_15pct: number;
}

export interface EKFEstimatorStatus {
  estimator_name: 'Extended Kalman Filter';
  filter_status: 'Converged' | 'Iterating' | 'Initialized';
  state_dimension: 6;
  physical_elements_count: 15;
  sensor_suite_used: 'Standard 10-Sensor Skid (Case 2)';
  last_update_timestamp: string;
  update_latency_ms: number; // ~105 ms
  innovation_nis_status: 'Normal (Within 95% Confidence)' | 'Disturbance Detected' | 'API pending';
  global_estimation_rmse_m_inv: string; // "<0.36% Rm"
  decline_mae_pct: number; // ~0.118%
  state_confidence_note: string; // e.g. "State covariance P updated dynamically"
}
