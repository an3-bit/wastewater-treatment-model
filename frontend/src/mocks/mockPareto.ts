import { ParetoPoint, OptimizationSummary } from '@/types/optimization';
import { mockStrategies } from './mockStrategies';

// Generate 60 Pareto points along the non-dominated curve
const generateParetoPoints = (): ParetoPoint[] => {
  const points: ParetoPoint[] = [];

  // Curve from lowest recovery (51.68%) to highest recovery (85.08%)
  for (let i = 0; i <= 50; i++) {
    const fraction = i / 50;
    const recovery = 51.68 + fraction * (85.08 - 51.68);
    // SEC curve has a minimum around recovery ~70% (SEC ~0.722), higher at low and high recoveries
    const sec = Number((0.722 + 0.10 * Math.pow((recovery - 69.8) / 18.0, 2)).toFixed(4));
    const p1 = Number((10.0 + fraction * 10.0).toFixed(2));
    const p2 = Number((14.0 + fraction * 6.25).toFixed(2));
    const maxElemRec = Number((13.99 + fraction * (29.99 - 13.99)).toFixed(2));
    const permeateTds = Number((4.8 + fraction * 4.2).toFixed(2));

    points.push({
      id: i + 1,
      p1_bar: p1,
      p2_bar: p2,
      recovery_pct: Number(recovery.toFixed(2)),
      sec_kwh_m3: sec,
      max_element_recovery_pct: maxElemRec,
      permeate_tds_mg_l: permeateTds,
      is_representative: false,
    });
  }

  // Add the 5 highlighted strategies
  points.push({
    id: 101,
    p1_bar: 13.0,
    p2_bar: 18.0,
    recovery_pct: 69.36,
    sec_kwh_m3: 0.771,
    max_element_recovery_pct: 23.69,
    permeate_tds_mg_l: 7.24,
    is_representative: true,
    strategy_tag: 'Baseline',
  });
  points.push({
    id: 102,
    p1_bar: 20.0,
    p2_bar: 20.25,
    recovery_pct: 85.08,
    sec_kwh_m3: 0.7561,
    max_element_recovery_pct: 29.99,
    permeate_tds_mg_l: 8.92,
    is_representative: true,
    strategy_tag: 'A',
  });
  points.push({
    id: 103,
    p1_bar: 15.8,
    p2_bar: 15.8,
    recovery_pct: 69.82,
    sec_kwh_m3: 0.7224,
    max_element_recovery_pct: 20.63,
    permeate_tds_mg_l: 6.85,
    is_representative: true,
    strategy_tag: 'B',
  });
  points.push({
    id: 104,
    p1_bar: 10.0,
    p2_bar: 14.0,
    recovery_pct: 51.68,
    sec_kwh_m3: 0.8239,
    max_element_recovery_pct: 13.99,
    permeate_tds_mg_l: 4.89,
    is_representative: true,
    strategy_tag: 'C',
  });
  points.push({
    id: 105,
    p1_bar: 16.06,
    p2_bar: 16.41,
    recovery_pct: 70.22,
    sec_kwh_m3: 0.7269,
    max_element_recovery_pct: 20.1,
    permeate_tds_mg_l: 7.21,
    is_representative: true,
    strategy_tag: 'D',
  });

  return points;
};

export const mockOptimizationSummary: OptimizationSummary = {
  total_pareto_points: 424,
  hypervolume_mean: 2002.955,
  hypervolume_std: 0.758,
  convergence_status: 'Converged (200 Gens, 5 Seeds)',
  surrogate_speedup: '1,218× speedup (27,685 evals/s)',
  reference_point: 'r_ref = [0.0% Rec, 2.0 kWh/m³, 35.0% Stress]',
  strategies: mockStrategies,
  pareto_points: generateParetoPoints(),
};
