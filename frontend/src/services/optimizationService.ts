import { OperatingStrategy, OptimizationSummary } from '@/types/optimization';
import { mockStrategies } from '@/mocks/mockStrategies';
import { mockOptimizationSummary } from '@/mocks/mockPareto';
import { policiesApi } from './api/policies';

let activeStrategyId = 'strategy_d';

export const optimizationService = {
  async getOptimizationSummary(): Promise<OptimizationSummary> {
    try {
      const res = await policiesApi.getPolicies();
      // Map API policies to frontend strategies if available
      const mappedStrategies: OperatingStrategy[] = res.policies.map((p) => {
        let codeId: 'baseline' | 'strategy_a' | 'strategy_b' | 'strategy_c' | 'strategy_d' = 'strategy_d';
        let codeName = 'Strategy D';
        if (p.policy_code === 'CASE_A') {
          codeId = 'baseline';
          codeName = 'Baseline';
        } else if (p.policy_code === 'CASE_B') {
          codeId = 'strategy_a';
          codeName = 'Strategy A (Max Recovery)';
        } else if (p.policy_code === 'CASE_C') {
          codeId = 'strategy_b';
          codeName = 'Strategy B (Min SEC)';
        } else if (p.policy_code === 'CASE_D') {
          codeId = 'strategy_c';
          codeName = 'Strategy C (Min Stress)';
        } else if (p.policy_code === 'CASE_E') {
          codeId = 'strategy_d';
          codeName = 'Strategy D (Predictive Knee)';
        }

        return {
          id: codeId,
          code: codeName,
          name: p.policy_name,
          description: p.architecture,
          p1_bar: p.p1_bar,
          p2_bar: p.p2_bar,
          recovery_pct: p.effective_recovery_pct,
          sec_kwh_m3: p.sec_kwh_m3,
          max_element_recovery_pct: +(p.effective_recovery_pct * 0.42).toFixed(2),
          permeate_tds_mg_l: 85.4,
          total_power_kw: +(p.total_energy_kwh / 8000.0).toFixed(2),
          status: p.policy_code === 'CASE_A' ? 'DOMINATED' : 'PARETO OPTIMAL',
          is_active: codeId === activeStrategyId,
          delta_vs_baseline: {
            recovery_diff_pct: +(p.effective_recovery_pct - 27.19).toFixed(2),
            sec_reduction_pct: +(((0.9965 - p.sec_kwh_m3) / 0.9965) * 100).toFixed(2),
            stress_reduction_pct: 12.5,
          },
        };
      });

      return {
        ...mockOptimizationSummary,
        strategies: mappedStrategies.length > 0 ? mappedStrategies : mockStrategies.map((s) => ({
          ...s,
          is_active: s.id === activeStrategyId,
        })),
      };
    } catch (e) {
      console.warn('FastAPI backend unavailable for getOptimizationSummary, falling back to mock:', e);
      return {
        ...mockOptimizationSummary,
        strategies: mockStrategies.map((s) => ({
          ...s,
          is_active: s.id === activeStrategyId,
        })),
      };
    }
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
