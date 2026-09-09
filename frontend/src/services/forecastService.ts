import { ForecastResult } from '@/types/forecast';
import { mockForecastResult } from '@/mocks/mockForecast';
import { fetchWithMode } from './api';

export const forecastService = {
  async getForecast(): Promise<ForecastResult> {
    return fetchWithMode<ForecastResult>('/api/v1/forecast', () => ({
      ...mockForecastResult,
    }));
  },
};
