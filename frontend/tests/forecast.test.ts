import { describe, it, expect } from 'vitest';
import { mockForecastResult } from '../src/mocks/mockForecast';

describe('Forecasting & Scientific Threshold Labels Verification', () => {
  it('strictly labels t5, t10, t15 as Analysis Thresholds', () => {
    expect(mockForecastResult.thresholds.t5.label).toContain('Analysis Threshold');
    expect(mockForecastResult.thresholds.t10.label).toContain('Analysis Threshold');
    expect(mockForecastResult.thresholds.t15.label).toContain('Analysis Threshold');

    // Ensure NO cleaning or CIP trigger claims are made
    expect(mockForecastResult.thresholds.t15.label.toLowerCase()).not.toContain('cleaning');
    expect(mockForecastResult.thresholds.t15.label.toLowerCase()).not.toContain('cip');
    expect(mockForecastResult.thresholds.t15.label.toLowerCase()).not.toContain('replacement');
  });

  it('contains valid trajectory points spanning historical and forecast horizons', () => {
    const trajectory = mockForecastResult.trajectory;
    expect(trajectory.length).toBeGreaterThan(10);

    const origin = mockForecastResult.origin_time_hours;
    const originPoint = trajectory.find((p) => p.time_hours === origin);
    expect(originPoint).toBeDefined();
    expect(originPoint?.current_state_marker).toBe(mockForecastResult.current_decline_pct);
  });

  it('includes mandatory scientific notice about analysis thresholds', () => {
    expect(mockForecastResult.scientific_notice).toContain('Analysis thresholds (t5, t10, t15)');
    expect(mockForecastResult.scientific_notice).toContain('not automated cleaning');
  });
});
