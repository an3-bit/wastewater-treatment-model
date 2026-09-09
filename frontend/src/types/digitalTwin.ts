/**
 * Digital Twin System Domain Types
 * Authoritative Model: RO_MODEL_VERSION = "2.0-pressure-corrected"
 * Virtual Plant Research Framework
 */

export type TwinConnectionStatus = 'connected' | 'reconnecting' | 'disconnected' | 'error';
export type TwinDataMode = 'mock' | 'api';
export type PlantOperatingMode = 'Virtual Plant' | 'Simulation Replay' | 'Historical Benchmark';

export interface FeedState {
  flow_m3_h: number;
  tds_mg_l: number;
  temperature_c: number;
  pressure_bar: number;
  ph: number;
  cod_mg_l: number;
}

export interface ROStageState {
  stage_number: 1 | 2;
  vessels_count: number;
  elements_per_vessel: number;
  total_elements: number;
  inlet_pressure_bar: number;
  outlet_pressure_bar: number;
  pressure_drop_bar: number;
  feed_flow_m3_h: number;
  permeate_flow_m3_h: number;
  concentrate_flow_m3_h: number;
  permeate_tds_mg_l: number;
  concentrate_tds_mg_l: number;
  stage_recovery_pct: number;
  avg_flux_lmh: number;
}

export interface PermeateState {
  total_flow_m3_h: number;
  tds_mg_l: number;
  recovery_pct: number;
  salt_rejection_pct: number;
}

export interface ConcentrateState {
  flow_m3_h: number;
  tds_mg_l: number;
  pressure_bar: number;
}

export interface EnergyMetrics {
  sec_kwh_m3: number;
  total_electrical_power_kw: number;
  stage1_pump_power_kw: number;
  stage2_booster_power_kw: number;
  energy_per_hour_kwh: number;
  cumulative_energy_kwh: number;
}

export interface PlantState {
  timestamp: string;
  simulation_time_hours: number;
  model_version: string;
  data_mode: TwinDataMode;
  operating_mode: PlantOperatingMode;
  connection_status: TwinConnectionStatus;
  feed: FeedState;
  stage1: ROStageState;
  stage2: ROStageState;
  interstage_pressure_bar: number;
  permeate: PermeateState;
  concentrate: ConcentrateState;
  energy: EnergyMetrics;
  overall_recovery_pct: number;
  max_element_recovery_pct: number;
  current_strategy_id: string;
  current_strategy_name: string;
}

export interface DigitalTwinStatus {
  sensors_status: 'Online' | 'Degraded' | 'Offline';
  ekf_status: 'Running' | 'Converged' | 'Diverged' | 'Standby';
  forecast_status: 'Available' | 'Computing' | 'Unavailable';
  model_version: string;
  data_source: 'Virtual Plant' | 'FastAPI Service' | 'Historical Archive';
  latency_ms: number;
  last_sync_timestamp: string;
}
