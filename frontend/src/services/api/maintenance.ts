/**
 * Maintenance API Client
 */

import { apiClient } from './client';
import { MaintenanceHistoryResponse, MaintenanceRecommendationResponse } from '@/types/api';

export const maintenanceApi = {
  async getRecommendation(): Promise<MaintenanceRecommendationResponse> {
    return apiClient<MaintenanceRecommendationResponse>('/maintenance/recommendation');
  },

  async getHistory(): Promise<MaintenanceHistoryResponse> {
    return apiClient<MaintenanceHistoryResponse>('/maintenance/history');
  },
};
