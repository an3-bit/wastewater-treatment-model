/**
 * WaterTwin AI — Frontend API Contract Types
 * Authoritative schemas corresponding to FastAPI backend Pydantic models.
 */

export interface ApiMeta {
  timestamp: string;
  model_version: string;
  stage: string;
  mode: string;
  scientific_status: string;
}

export interface TwinMetadata {
  model_version: string;
  estimator: string;
  fouling_zones: number;
  display_elements: number;
  forecast_horizon_h: number;
  status: string;
  stage: string;
  industrial_validation: boolean;
  economic_model_status: string;
  data_mode: string;
  last_update: string;
  scientific_caveat: string;
}

export interface TwinState {
  timestamp: string;
  simulation_time_h: number;
  feed_flow_m3_h: number;
  feed_tds_mg_l: number;
  temperature_c: number;
  p1_bar: number;
  p2_bar: number;
  p_interstage_bar: number;
  permeate_flow_m3_h: number;
  concentrate_flow_m3_h: number;
  recovery_percent: number;
  sec_kwh_m3: number;
  power_kw: number;
  permeate_tds_mg_l: number;
  concentrate_tds_mg_l: number;
  salt_rejection_percent: number;
  overall_permeability_decline_percent: number;
  membrane_health_score_percent: number;
  current_operating_policy: string;
  twin_status: string;
  data_quality: string;
  hours_since_cip: number;
}

export interface TwinAdvanceRequest {
  hours: number;
}

export interface TwinResetRequest {
  reset_to_clean?: boolean;
  initial_p1_bar?: number;
  initial_p2_bar?: number;
}

export interface TwinAdvanceResponse {
  success: boolean;
  advanced_hours: number;
  current_simulation_time_h: number;
  state: TwinState;
}

export interface SensorReadingApi {
  id: string;
  name: string;
  description: string;
  value: number;
  unit: string;
  timestamp: string;
  status: string;
  quality: string;
  source: string;
  min_range?: number;
  max_range?: number;
}

export interface SensorListResponse {
  sensors: SensorReadingApi[];
  total_count: number;
  data_mode: string;
}

export interface SensorHistoryPoint {
  timestamp: string;
  value: number;
  quality: string;
}

export interface SensorHistoryResponse {
  sensor_id: string;
  sensor_name: string;
  unit: string;
  history: SensorHistoryPoint[];
  hours_retrieved: number;
}

export interface MembraneZone {
  zone_id: string;
  stage: number;
  position: 'Lead' | 'Middle' | 'Tail';
  vessels_covered: string;
  elements_count: number;
  Rf_m_inv: number;
  normalized_Rf: number;
  permeability_m_pa_s: number;
  permeability_decline_percent: number;
  health_percent: number;
  severity: 'HEALTHY' | 'MODERATE' | 'SEVERE' | 'CRITICAL';
}

export interface MembraneZoneListResponse {
  zones: MembraneZone[];
  total_zones: number;
  estimator: string;
  mean_health_percent: number;
  max_decline_percent: number;
  critical_zone_id?: string | null;
}

export interface MembraneElementApi {
  element_id: string;
  stage_id: number;
  vessel_id: number;
  position_in_vessel: number;
  parent_zone_id: string;
  estimated_from_zone: boolean;
  health_percent: number;
  decline_percent: number;
  flux_lmh: number;
  salt_rejection_percent: number;
  fouling_resistance_m_inv: number;
  status: string;
}

export interface MembraneElementListResponse {
  elements: MembraneElementApi[];
  total_elements: number;
  mapping_notice: string;
  estimator: string;
}

export interface ForecastPoint {
  time_offset_h: number;
  recovery_percent: number;
  permeate_flow_m3_h: number;
  sec_kwh_m3: number;
  power_kw: number;
  permeate_tds_mg_l: number;
  permeability_decline_percent: number;
  stage1_decline_percent: number;
  stage2_decline_percent: number;
  zone_rf_m_inv: Record<string, number>;
}

export interface ForecastConfidence {
  horizon_hours: number;
  is_standard_horizon: boolean;
  confidence_level_percent: number;
  flux_uncertainty_band_pct: number;
  fouling_uncertainty_band_pct: number;
  notes: string;
}

export interface ForecastResponse {
  horizon_hours: number;
  step_hours: number;
  standard_horizon_note: string;
  confidence: ForecastConfidence;
  trajectory: ForecastPoint[];
  predicted_threshold_crossing_h?: number | null;
}

export interface MaintenanceRecommendationResponse {
  recommended_action: 'CLEAN' | 'CONTINUE' | 'MONITOR';
  urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  time_since_last_CIP_h: number;
  predicted_time_to_threshold_h: number;
  current_decline_percent: number;
  predicted_decline_24h_percent: number;
  reason_codes: string[];
  primary_rationale: string;
  economic_advantage_kes: number;
  lockout_active: boolean;
  lockout_period_h: number;
  next_eligible_cleaning_time_h: number;
  decision_support_role: string;
  scientific_status: string;
}

export interface MaintenanceEvent {
  event_id: string;
  timestamp_h: number;
  duration_h: number;
  pre_clean_decline_pct: number;
  post_clean_decline_pct: number;
  estimated_restoration_pct: number;
  reason: string;
  estimated_cost_kes: number;
  downtime_h: number;
}

export interface MaintenanceHistoryResponse {
  total_cip_count_annual: number;
  calendar_baseline_cip_count: number;
  condition_based_cip_count: number;
  predictive_cip_count: number;
  mean_interval_h: number;
  history: MaintenanceEvent[];
}

export interface WaterBalanceMetrics {
  baseline_permeate_m3: number;
  watertwin_permeate_m3: number;
  additional_permeate_m3: number;
  water_increase_pct: number;
}

export interface EnergyBalanceMetrics {
  baseline_total_kwh: number;
  watertwin_total_kwh: number;
  total_electricity_change_pct: number;
  baseline_sec_kwh_m3: number;
  watertwin_sec_kwh_m3: number;
  sec_reduction_pct: number;
  energy_interpretation: string;
}

export interface EconomicValues {
  integrated_framework_value_kes_year: number;
  static_optimization_value_kes_year: number;
  condition_based_value_kes_year: number;
  prediction_value_kes_year: number;
  mpc_value_kes_year: number;
  predictive_decision_intelligence_kes_year: number;
  treatment_lcow_kes_m3: number;
}

export interface EconomicSummaryResponse {
  water: WaterBalanceMetrics;
  energy: EnergyBalanceMetrics;
  economics: EconomicValues;
  scenarios_summary: {
    conservative_benefit_kes: number;
    base_benefit_kes: number;
    favourable_benefit_kes: number;
  };
  scientific_caveat: string;
}

export interface ValueDecompositionItem {
  code: string;
  name: string;
  formula: string;
  value_kes_year: number;
  share_pct: number;
  classification: string;
  commercial_recommendation: string;
}

export interface ValueDecompositionResponse {
  items: ValueDecompositionItem[];
  total_integrated_value_kes_year: number;
  pure_prediction_share_pct: number;
  condition_monitoring_share_pct: number;
  mpc_share_pct: number;
  mpc_caveat: string;
}

export interface ScenarioDetail {
  name: string;
  description: string;
  reuse_demand_pct: number;
  cip_cost_multiplier: number;
  cip_downtime_h: number;
  discharge_credit_kes_m3: number;
  integrated_value_kes_year: number;
  digital_twin_net_benefit_kes_year: number;
  treatment_lcow_kes_m3: number;
}

export interface EconomicScenariosResponse {
  scenarios: ScenarioDetail[];
  authoritative_scenario: string;
  scientific_caveat: string;
}

export interface PolicyItem {
  policy_code: string;
  policy_name: string;
  architecture: string;
  p1_bar: number;
  p2_bar: number;
  permeate_m3: number;
  effective_recovery_pct: number;
  total_energy_kwh: number;
  sec_kwh_m3: number;
  cip_count: number;
  cip_downtime_h: number;
  operating_uptime_h: number;
  treatment_lcow_kes_m3: number;
  net_annual_benefit_kes: number;
  incremental_value_vs_baseline_kes: number;
  policy_type: string;
  deployable: boolean;
  oracle: boolean;
  theoretical_upper_bound: boolean;
}

export interface PolicyComparisonResponse {
  policies: PolicyItem[];
  total_policies: number;
  authoritative_recommended_policy: string;
  oracle_notice: string;
}

export interface SimulationRequest {
  feed_flow_m3_h: number;
  feed_tds_mg_l: number;
  temperature_c: number;
  p1_bar: number;
  p2_bar: number;
  forecast_horizon_h?: number;
  economic_scenario?: string;
}

export interface SimulationWarning {
  code: string;
  message: string;
  severity: string;
}

export interface SimulationResult {
  feasible: boolean;
  feed_flow_m3_h: number;
  feed_tds_mg_l: number;
  temperature_c: number;
  p1_bar: number;
  p2_bar: number;
  permeate_flow_m3_h: number;
  concentrate_flow_m3_h: number;
  recovery_percent: number;
  sec_kwh_m3: number;
  power_kw: number;
  permeate_tds_mg_l: number;
  concentrate_tds_mg_l: number;
  salt_rejection_percent: number;
  fouling_metrics: Record<string, number>;
  estimated_daily_value_kes: number;
  constraint_status: Record<string, boolean>;
  warnings: SimulationWarning[];
  execution_time_ms: number;
}
