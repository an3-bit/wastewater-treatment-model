/**
 * Scenario Simulator Domain Types
 * Connects to Virtual Twin Simulator (Mock or POST /api/v1/simulate)
 */

export interface SimulationRequest {
  feed_flow_m3_h: number;
  feed_tds_mg_l: number;
  temperature_c: number;
  p1_bar: number;
  p2_bar: number;
  simulation_duration_hours: number;
}

export interface SimulationResult {
  request: SimulationRequest;
  timestamp: string;
  execution_time_ms: number;
  model_version: string;
  is_verified_mechanistic: boolean;
  outputs: {
    overall_recovery_pct: number;
    permeate_flow_m3_h: number;
    permeate_tds_mg_l: number;
    concentrate_flow_m3_h: number;
    concentrate_tds_mg_l: number;
    sec_kwh_m3: number;
    total_power_kw: number;
    max_element_recovery_pct: number;
    predicted_fouling_decline_pct: number;
    salt_rejection_pct: number;
    stage1_recovery_pct: number;
    stage2_recovery_pct: number;
    hydraulic_pressure_drop_bar: number;
  };
  warnings: string[];
}
