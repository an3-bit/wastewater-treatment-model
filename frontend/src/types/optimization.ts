/**
 * NSGA-II Multi-Objective Optimization & Operating Strategy Types
 * Objectives: Max Recovery (f1), Min SEC (f2), Min Stress MaxElemRec (f3)
 */

export interface OperatingStrategy {
  id: 'baseline' | 'strategy_a' | 'strategy_b' | 'strategy_c' | 'strategy_d';
  code: string; // 'Baseline', 'Strategy A', 'Strategy B', 'Strategy C', 'Strategy D'
  name: string; // 'Industrial Baseline', 'Maximum Recovery', 'Minimum SEC', 'Minimum Stress', 'Balanced Knee'
  description: string;
  p1_bar: number;
  p2_bar: number;
  recovery_pct: number;
  sec_kwh_m3: number;
  max_element_recovery_pct: number;
  permeate_tds_mg_l: number;
  total_power_kw: number;
  status: 'PARETO OPTIMAL' | 'DOMINATED' | 'BOUNDARY FEASIBLE';
  is_active: boolean;
  delta_vs_baseline: {
    recovery_diff_pct: number;
    sec_reduction_pct: number;
    stress_reduction_pct: number;
  };
}

export interface ParetoPoint {
  id: number;
  p1_bar: number;
  p2_bar: number;
  recovery_pct: number; // Y-axis
  sec_kwh_m3: number; // X-axis
  max_element_recovery_pct: number; // Z / bubble size
  permeate_tds_mg_l: number;
  is_representative?: boolean;
  strategy_tag?: string; // 'A' | 'B' | 'C' | 'D' | 'Baseline'
}

export interface OptimizationSummary {
  total_pareto_points: number;
  hypervolume_mean: number;
  hypervolume_std: number;
  convergence_status: 'Converged (200 Gens, 5 Seeds)';
  surrogate_speedup: string; // "1,218x speedup"
  reference_point: string; // "[0% Rec, 2.0 kWh/m3, 35% Stress]"
  strategies: OperatingStrategy[];
  pareto_points: ParetoPoint[];
}
