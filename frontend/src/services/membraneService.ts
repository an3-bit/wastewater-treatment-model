import {
  MembraneZoneState,
  PhysicalElementMapping,
  AxialFoulingPoint,
  EKFEstimatorStatus,
} from '@/types/membrane';
import {
  mockMembraneZones,
  mockPhysicalElements,
  mockAxialFoulingData,
  mockEKFStatus,
} from '@/mocks/mockMembranes';
import { fetchWithMode } from './api';

export const membraneService = {
  async getMembraneZones(): Promise<MembraneZoneState[]> {
    return fetchWithMode<MembraneZoneState[]>('/api/v1/membranes/zones', () => [
      ...mockMembraneZones,
    ]);
  },

  async getPhysicalElements(): Promise<PhysicalElementMapping[]> {
    return fetchWithMode<PhysicalElementMapping[]>('/api/v1/membranes/elements', () => [
      ...mockPhysicalElements,
    ]);
  },

  async getAxialFoulingProfile(): Promise<AxialFoulingPoint[]> {
    return fetchWithMode<AxialFoulingPoint[]>('/api/v1/membranes/axial-profile', () => [
      ...mockAxialFoulingData,
    ]);
  },

  async getEKFStatus(): Promise<EKFEstimatorStatus> {
    return fetchWithMode<EKFEstimatorStatus>('/api/v1/membranes/ekf-status', () => ({
      ...mockEKFStatus,
      last_update_timestamp: new Date().toISOString(),
    }));
  },
};
