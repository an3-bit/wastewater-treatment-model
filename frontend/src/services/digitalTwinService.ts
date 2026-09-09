import { PlantState, DigitalTwinStatus } from '@/types/digitalTwin';
import { mockPlantState, mockDigitalTwinStatus } from '@/mocks/mockTwinState';
import { fetchWithMode } from './api';

export const digitalTwinService = {
  async getPlantState(): Promise<PlantState> {
    return fetchWithMode<PlantState>('/api/v1/twin/state', () => ({
      ...mockPlantState,
      timestamp: new Date().toISOString(),
    }));
  },

  async getDigitalTwinStatus(): Promise<DigitalTwinStatus> {
    return fetchWithMode<DigitalTwinStatus>('/api/v1/twin/status', () => ({
      ...mockDigitalTwinStatus,
      last_sync_timestamp: new Date().toISOString(),
    }));
  },
};
