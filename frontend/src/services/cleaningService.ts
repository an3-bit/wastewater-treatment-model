import { CIPProtocol, CleaningSimulationInput, CleaningSimulationResult } from '@/types/cleaning';
import { mockCIPProtocols, calculateCleaningSimulation } from '@/mocks/mockCleaning';
import { fetchWithMode } from './api';

export const cleaningService = {
  async getCIPProtocols(): Promise<CIPProtocol[]> {
    return fetchWithMode<CIPProtocol[]>('/api/v1/cleaning/protocols', () => mockCIPProtocols);
  },

  async runCleaningSimulation(input: CleaningSimulationInput): Promise<CleaningSimulationResult> {
    return fetchWithMode<CleaningSimulationResult>(
      '/api/v1/cleaning/simulate',
      () => calculateCleaningSimulation(input),
      {
        method: 'POST',
        body: JSON.stringify(input),
      }
    );
  },
};
