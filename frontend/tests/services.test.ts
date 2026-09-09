import { describe, it, expect } from 'vitest';
import {
  digitalTwinService,
  sensorService,
  membraneService,
  forecastService,
  optimizationService,
  simulationService,
  cleaningService,
} from '../src/services';

describe('Data Services & Mock Engine Integrity', () => {
  it('retrieves valid plant state with exact mass closure', async () => {
    const state = await digitalTwinService.getPlantState();
    expect(state).toBeDefined();
    expect(state.model_version).toBe('2.0-pressure-corrected');
    expect(state.overall_recovery_pct).toBe(70.22);
    expect(state.stage1.total_elements).toBe(9);
    expect(state.stage2.total_elements).toBe(6);
  });

  it('retrieves the 10 standard sensors', async () => {
    const sensors = await sensorService.getSensors();
    expect(sensors).toHaveLength(10);
    const tags = sensors.map((s) => s.tag);
    expect(tags).toContain('FT-101');
    expect(tags).toContain('PT-101');
    expect(tags).toContain('ET-101');
  });

  it('retrieves membrane zones and EKF status', async () => {
    const zones = await membraneService.getMembraneZones();
    const ekf = await membraneService.getEKFStatus();

    expect(zones).toHaveLength(6);
    expect(ekf.state_dimension).toBe(6);
    expect(ekf.filter_status).toBe('Converged');
  });

  it('retrieves forecast results', async () => {
    const forecast = await forecastService.getForecast();
    expect(forecast.horizon_hours).toBe(72.0);
    expect(forecast.predicted_t10_hours).toBe(82.5);
  });

  it('retrieves optimization summary and sets active strategy', async () => {
    const summary = await optimizationService.getOptimizationSummary();
    expect(summary.total_pareto_points).toBe(424);

    const activeStrat = await optimizationService.setActiveStrategy('strategy_b');
    expect(activeStrat?.code).toBe('Strategy B');
  });

  it('runs scenario simulation and returns physically bounded outputs', async () => {
    const simReq = {
      feed_flow_m3_h: 30.0,
      feed_tds_mg_l: 2041.0,
      temperature_c: 25.0,
      p1_bar: 16.06,
      p2_bar: 16.41,
      simulation_duration_hours: 48.0,
    };

    const simRes = await simulationService.runSimulation(simReq);
    expect(simRes.is_verified_mechanistic).toBe(true);
    expect(simRes.outputs.overall_recovery_pct).toBeGreaterThan(60.0);
    expect(simRes.outputs.overall_recovery_pct).toBeLessThan(85.0);
    expect(simRes.outputs.sec_kwh_m3).toBeGreaterThan(0.5);
    expect(simRes.outputs.sec_kwh_m3).toBeLessThan(1.5);
    expect(simRes.outputs.max_element_recovery_pct).toBeLessThanOrEqual(30.0);
  });

  it('retrieves CIP protocols and runs cleaning simulation', async () => {
    const protocols = await cleaningService.getCIPProtocols();
    expect(protocols.length).toBeGreaterThanOrEqual(4);

    const res = await cleaningService.runCleaningSimulation({
      cleaning_efficiency: 0.92,
      protocol_id: 'combined_two_step',
      target_stages: 'both',
    });
    expect(res.restored_flux_decline_pct).toBeLessThan(res.initial_flux_decline_pct);
    expect(res.extended_operating_life_hours).toBeGreaterThan(0);
  });
});
