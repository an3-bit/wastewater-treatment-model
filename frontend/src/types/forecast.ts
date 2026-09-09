/**
 * Stage 7 Predictive Forecasting & Remaining-Time Threshold Types
 * Analysis Thresholds: t5 (5%), t10 (10%), t15 (15%)
 * Note: These are scientific analysis thresholds, NOT cleaning or CIP triggers.
 */

export interface ForecastTrajectoryPoint {
  time_hours: number;
  historical_decline_pct: number | null;
  forecast_decline_pct: number | null;
  current_state_marker: number | null;
  threshold_5: number;
  threshold_10: number;
  threshold_15: number;
}

export interface AnalysisThresholdInfo {
  threshold_pct: number;
  predicted_crossing_time_hours: number | null;
  remaining_time_hours: number | null;
  label: string; // e.g. "5% Analysis Threshold"
  scientific_status: string; // "Projected via virtual sensor forward model"
  lead_time_accuracy_note: string; // "Stage 7 benchmark error: 0.50h"
}

export interface ForecastResult {
  origin_time_hours: number;
  current_decline_pct: number;
  horizon_hours: number;
  model_status: 'Available' | 'Predicting' | 'Calibrating';
  uncertainty_status: 'Uncertainty API pending' | 'Bounded Process Envelope';
  predicted_t5_hours: number | null;
  predicted_t10_hours: number | null;
  predicted_t15_hours: number | null;
  remaining_to_t5_hours: number | null;
  remaining_to_t10_hours: number | null;
  remaining_to_t15_hours: number | null;
  trajectory: ForecastTrajectoryPoint[];
  thresholds: {
    t5: AnalysisThresholdInfo;
    t10: AnalysisThresholdInfo;
    t15: AnalysisThresholdInfo;
  };
  scientific_notice: string;
}
