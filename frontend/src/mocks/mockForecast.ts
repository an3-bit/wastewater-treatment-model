import { ForecastResult, ForecastTrajectoryPoint } from '@/types/forecast';

// Generate 120-hour trajectory points
const generateTrajectory = (): ForecastTrajectoryPoint[] => {
  const points: ForecastTrajectoryPoint[] = [];
  const originTime = 48;

  for (let t = 0; t <= 120; t += 4) {
    // Model realistic fouling growth curve: decline % = 0.85 * (t^0.62)
    const historicalVal = t <= originTime ? Number((0.82 * Math.pow(t, 0.62)).toFixed(2)) : null;
    const forecastVal = t >= originTime ? Number((0.82 * Math.pow(t, 0.62)).toFixed(2)) : null;
    const currentMarker = t === originTime ? historicalVal : null;

    points.push({
      time_hours: t,
      historical_decline_pct: historicalVal,
      forecast_decline_pct: forecastVal,
      current_state_marker: currentMarker,
      threshold_5: 5.0,
      threshold_10: 10.0,
      threshold_15: 15.0,
    });
  }
  return points;
};

export const mockForecastResult: ForecastResult = {
  origin_time_hours: 48.0,
  current_decline_pct: 9.04,
  horizon_hours: 72.0,
  model_status: 'Available',
  uncertainty_status: 'Uncertainty API pending',
  predicted_t5_hours: 41.2,
  predicted_t10_hours: 82.5,
  predicted_t15_hours: 118.0,
  remaining_to_t5_hours: 0.0, // already crossed
  remaining_to_t10_hours: 34.5,
  remaining_to_t15_hours: 70.0,
  trajectory: generateTrajectory(),
  thresholds: {
    t5: {
      threshold_pct: 5.0,
      predicted_crossing_time_hours: 41.2,
      remaining_time_hours: 0.0,
      label: '5% Analysis Threshold (t₅)',
      scientific_status: 'Crossed at t = 41.2 h (Evaluated)',
      lead_time_accuracy_note: 'Stage 7 error: 0.79 h at 1.0 h lead time',
    },
    t10: {
      threshold_pct: 10.0,
      predicted_crossing_time_hours: 82.5,
      remaining_time_hours: 34.5,
      label: '10% Analysis Threshold (t₁₀)',
      scientific_status: 'Projected at t = 82.5 h (Active Forecast)',
      lead_time_accuracy_note: 'Stage 7 error: 0.50 h at 3.0 h lead time',
    },
    t15: {
      threshold_pct: 15.0,
      predicted_crossing_time_hours: 118.0,
      remaining_time_hours: 70.0,
      label: '15% Analysis Threshold (t₁₅)',
      scientific_status: 'Projected at t = 118.0 h (Research Benchmark Horizon)',
      lead_time_accuracy_note: 'Stage 7 error: 0.99 h at 12.0 h lead time',
    },
  },
  scientific_notice:
    'Analysis thresholds (t5, t10, t15) represent research benchmark milestones for progressive flux decay tracking, not automated cleaning or membrane replacement triggers.',
};
