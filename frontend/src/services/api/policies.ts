/**
 * Policies API Client
 */

import { apiClient } from './client';
import { PolicyComparisonResponse } from '@/types/api';

export const policiesApi = {
  async getPolicies(): Promise<PolicyComparisonResponse> {
    return apiClient<PolicyComparisonResponse>('/policies');
  },
};
