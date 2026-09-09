/**
 * Economics API Client
 */

import { apiClient } from './client';
import { EconomicScenariosResponse, EconomicSummaryResponse, ValueDecompositionResponse } from '@/types/api';

export const economicsApi = {
  async getSummary(): Promise<EconomicSummaryResponse> {
    return apiClient<EconomicSummaryResponse>('/economics/summary');
  },

  async getValueDecomposition(): Promise<ValueDecompositionResponse> {
    return apiClient<ValueDecompositionResponse>('/economics/value-decomposition');
  },

  async getScenarios(): Promise<EconomicScenariosResponse> {
    return apiClient<EconomicScenariosResponse>('/economics/scenarios');
  },
};
