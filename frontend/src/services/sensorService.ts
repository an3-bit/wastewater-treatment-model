import { SensorReading, SensorSuiteSummary } from '@/types/sensors';
import { mockSensors, mockSensorSummary } from '@/mocks/mockSensors';
import { sensorsApi } from './api/sensors';

export const sensorService = {
  async getSensors(): Promise<SensorReading[]> {
    try {
      const res = await sensorsApi.getSensors();
      return res.sensors.map((s) => ({
        id: s.id,
        tag: s.id,
        name: s.name,
        symbol: s.id,
        current_value: s.value,
        unit: s.unit,
        status: 'Online',
        last_update: s.timestamp,
        range_min: s.min_range || 0.0,
        range_max: s.max_range || 100.0,
        noise_std: 0.02,
        location: 'Skid Header',
        history_sparkline: [s.value * 0.98, s.value * 0.99, s.value * 1.01, s.value],
        category: s.id.includes('Q') ? 'hydraulic' : (s.id.includes('C') ? 'quality' : (s.id.includes('T') ? 'thermal' : 'energy')),
      }));
    } catch (e) {
      console.warn('FastAPI backend unavailable for getSensors, falling back to mock:', e);
      return [...mockSensors];
    }
  },

  async getSensorSummary(): Promise<SensorSuiteSummary> {
    try {
      const sensors = await this.getSensors();
      return {
        total_sensors: sensors.length,
        online_count: sensors.length,
        warning_count: 0,
        offline_count: 0,
        last_scan_timestamp: new Date().toISOString(),
        sensors,
      };
    } catch (e) {
      console.warn('FastAPI backend unavailable for getSensorSummary, falling back to mock:', e);
      return {
        ...mockSensorSummary,
        last_scan_timestamp: new Date().toISOString(),
      };
    }
  },

  async getSensorById(id: string): Promise<SensorReading | undefined> {
    const sensors = await this.getSensors();
    return sensors.find((s) => s.id === id || s.tag.toLowerCase() === id.toLowerCase());
  },
};
