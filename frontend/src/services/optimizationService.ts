import { OperatingStrategy, OptimizationSummary } from '@/types/optimization';
import { mockStrategies } from '@/mocks/mockStrategies';
import { mockOptimizationSummary } from '@/mocks/mockPareto';
import { fetchWithMode } from './api';

let activeStrategyId = 'strategy_d';

export const optimizationService = {
  async getOptimizationSummary(): Promise<OptimizationSummary> {
    return fetchWithMode<OptimizationSummary>('/api/v1/optimization/summary', () => ({
      ...mockOptimizationSummary,
      strategies: mockStrategies.map((s) => ({
        ...s,
        is_active: s.id === activeStrategyId,
      })),
    }));
  },

  async getStrategies(): Promise<OperatingStrategy[]> {
    const summary = await this.getOptimizationSummary();
    return summary.strategies;
  },

  async setActiveStrategy(id: string): Promise<OperatingStrategy | undefined> {
    activeStrategyId = id;
    const strategies = await this.getStrategies();
    return strategies.find((s) => s.id === id);
  },
};
