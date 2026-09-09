/**
 * Forecast API Client
 */

import { apiClient } from './client';
import { ForecastResponse } from '@/types/api';

export const forecastApi = {
  async getForecast(hours: number = 24): Promise<ForecastResponse> {
    return apiClient<ForecastResponse>(`/forecast?hours=${hours}`);
  },
};
