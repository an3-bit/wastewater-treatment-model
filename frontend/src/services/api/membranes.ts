/**
 * Membrane Health API Client
 */

import { apiClient } from './client';
import { MembraneElementListResponse, MembraneZoneListResponse } from '@/types/api';

export const membranesApi = {
  async getZones(): Promise<MembraneZoneListResponse> {
    return apiClient<MembraneZoneListResponse>('/membranes/zones');
  },

  async getElements(): Promise<MembraneElementListResponse> {
    return apiClient<MembraneElementListResponse>('/membranes/elements');
  },
};
