/**
 * Simulation API Client
 */

import { apiClient } from './client';
import { SimulationRequest, SimulationResult } from '@/types/api';

export const simulationApi = {
  async runSimulation(req: SimulationRequest): Promise<SimulationResult> {
    return apiClient<SimulationResult>('/simulation/run', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },
};
