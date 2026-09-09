/**
 * Digital Twin API Client
 */

import { apiClient } from './client';
import { TwinAdvanceRequest, TwinAdvanceResponse, TwinMetadata, TwinResetRequest, TwinState } from '@/types/api';

export const twinApi = {
  async getMetadata(): Promise<TwinMetadata> {
    return apiClient<TwinMetadata>('/twin/metadata');
  },

  async getState(): Promise<TwinState> {
    return apiClient<TwinState>('/twin/state');
  },

  async advance(req: TwinAdvanceRequest): Promise<TwinAdvanceResponse> {
    return apiClient<TwinAdvanceResponse>('/twin/advance', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },

  async reset(req: TwinResetRequest): Promise<TwinState> {
    return apiClient<TwinState>('/twin/reset', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },
};
