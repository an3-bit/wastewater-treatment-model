import { PlantState, DigitalTwinStatus } from '@/types/digitalTwin';
import { mockPlantState, mockDigitalTwinStatus } from '@/mocks/mockTwinState';
import { twinApi } from './api/twin';
import { TwinState } from '@/types/api';

function mapTwinStateToPlantState(apiState: TwinState): PlantState {
  const qf = apiState.feed_flow_m3_h;
  const qp = apiState.permeate_flow_m3_h;
  const qc = apiState.concentrate_flow_m3_h;
  const qp1 = qp * 0.58;
  const qp2 = qp * 0.42;

  return {
    timestamp: apiState.timestamp,
    simulation_time_hours: apiState.simulation_time_h,
    model_version: '2.0-pressure-corrected',
    data_mode: 'api',
    operating_mode: 'Virtual Plant',
    connection_status: 'connected',
    feed: {
      flow_m3_h: qf,
      tds_mg_l: apiState.feed_tds_mg_l,
      temperature_c: apiState.temperature_c,
      pressure_bar: apiState.p1_bar,
      ph: 7.8,
      cod_mg_l: 42.0,
    },
    stage1: {
      stage_number: 1,
      vessels_count: 3,
      elements_per_vessel: 3,
      total_elements: 9,
      inlet_pressure_bar: apiState.p1_bar,
      outlet_pressure_bar: apiState.p_interstage_bar,
      pressure_drop_bar: +(apiState.p1_bar - apiState.p_interstage_bar).toFixed(2),
      feed_flow_m3_h: qf,
      permeate_flow_m3_h: +qp1.toFixed(2),
      concentrate_flow_m3_h: +(qf - qp1).toFixed(2),
      permeate_tds_mg_l: +(apiState.permeate_tds_mg_l * 0.8).toFixed(1),
      concentrate_tds_mg_l: 4500.0,
      stage_recovery_pct: +((qp1 / qf) * 100).toFixed(2),
      avg_flux_lmh: 24.2,
    },
    stage2: {
      stage_number: 2,
      vessels_count: 2,
      elements_per_vessel: 3,
      total_elements: 6,
      inlet_pressure_bar: apiState.p2_bar,
      outlet_pressure_bar: +(apiState.p2_bar - 1.1).toFixed(2),
      pressure_drop_bar: 1.1,
      feed_flow_m3_h: +(qf - qp1).toFixed(2),
      permeate_flow_m3_h: +qp2.toFixed(2),
      concentrate_flow_m3_h: qc,
      permeate_tds_mg_l: +(apiState.permeate_tds_mg_l * 1.25).toFixed(1),
      concentrate_tds_mg_l: apiState.concentrate_tds_mg_l,
      stage_recovery_pct: +((qp2 / (qf - qp1)) * 100).toFixed(2),
      avg_flux_lmh: 19.8,
    },
    interstage_pressure_bar: apiState.p_interstage_bar,
    permeate: {
      total_flow_m3_h: qp,
      tds_mg_l: apiState.permeate_tds_mg_l,
      recovery_pct: apiState.recovery_percent,
      salt_rejection_pct: apiState.salt_rejection_percent,
    },
    concentrate: {
      flow_m3_h: qc,
      tds_mg_l: apiState.concentrate_tds_mg_l,
      pressure_bar: +(apiState.p2_bar - 1.1).toFixed(2),
    },
    energy: {
      sec_kwh_m3: apiState.sec_kwh_m3,
      total_electrical_power_kw: apiState.power_kw,
      stage1_pump_power_kw: +(apiState.power_kw * 0.65).toFixed(2),
      stage2_booster_power_kw: +(apiState.power_kw * 0.35).toFixed(2),
      energy_per_hour_kwh: apiState.power_kw,
      cumulative_energy_kwh: +(apiState.power_kw * apiState.simulation_time_h).toFixed(1),
    },
    overall_recovery_pct: apiState.recovery_percent,
    max_element_recovery_pct: +(apiState.recovery_percent * 0.42).toFixed(2),
    current_strategy_id: 'strategy_d',
    current_strategy_name: apiState.current_operating_policy,
  };
}

export const digitalTwinService = {
  async getPlantState(): Promise<PlantState> {
    try {
      const state = await twinApi.getState();
      return mapTwinStateToPlantState(state);
    } catch (e) {
      console.warn('FastAPI backend unavailable for getPlantState, falling back to mock:', e);
      return {
        ...mockPlantState,
        timestamp: new Date().toISOString(),
      };
    }
  },

  async getDigitalTwinStatus(): Promise<DigitalTwinStatus> {
    try {
      const meta = await twinApi.getMetadata();
      return {
        sensors_status: 'Online',
        ekf_status: 'Converged',
        forecast_status: 'Available',
        model_version: meta.model_version,
        data_source: 'Virtual Plant',
        latency_ms: 2.4,
        last_sync_timestamp: meta.last_update,
      };
    } catch (e) {
      console.warn('FastAPI backend unavailable for getDigitalTwinStatus, falling back to mock:', e);
      return {
        ...mockDigitalTwinStatus,
        last_sync_timestamp: new Date().toISOString(),
      };
    }
  },
};
