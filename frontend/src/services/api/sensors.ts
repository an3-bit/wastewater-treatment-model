/**
 * Sensors API Client
 */

import { apiClient } from './client';
import { SensorHistoryResponse, SensorListResponse } from '@/types/api';

export const sensorsApi = {
  async getSensors(): Promise<SensorListResponse> {
    return apiClient<SensorListResponse>('/sensors');
  },

  async getHistory(sensorId: string = 'Qf', hours: number = 24): Promise<SensorHistoryResponse> {
    return apiClient<SensorHistoryResponse>(`/sensors/history?sensor_id=${encodeURIComponent(sensorId)}&hours=${hours}`);
  },
};
