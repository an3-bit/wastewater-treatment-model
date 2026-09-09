import { SensorReading, SensorSuiteSummary } from '@/types/sensors';
import { mockSensors, mockSensorSummary } from '@/mocks/mockSensors';
import { fetchWithMode } from './api';

export const sensorService = {
  async getSensors(): Promise<SensorReading[]> {
    return fetchWithMode<SensorReading[]>('/api/v1/sensors', () => [...mockSensors]);
  },

  async getSensorSummary(): Promise<SensorSuiteSummary> {
    return fetchWithMode<SensorSuiteSummary>('/api/v1/sensors/summary', () => ({
      ...mockSensorSummary,
      last_scan_timestamp: new Date().toISOString(),
    }));
  },

  async getSensorById(id: string): Promise<SensorReading | undefined> {
    const sensors = await this.getSensors();
    return sensors.find((s) => s.id === id || s.tag.toLowerCase() === id.toLowerCase());
  },
};
