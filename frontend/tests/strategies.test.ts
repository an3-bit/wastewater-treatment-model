import { describe, it, expect } from 'vitest';
import { mockStrategies } from '../src/mocks/mockStrategies';

describe('Authoritative Operating Strategies & Dominance Verification', () => {
  it('contains all 5 authoritative operating strategies', () => {
    expect(mockStrategies).toHaveLength(5);
    const codes = mockStrategies.map((s) => s.code);
    expect(codes).toContain('Baseline');
    expect(codes).toContain('Strategy A');
    expect(codes).toContain('Strategy B');
    expect(codes).toContain('Strategy C');
    expect(codes).toContain('Strategy D');
  });

  it('validates Baseline strategy values (13/18 bar, dominated)', () => {
    const baseline = mockStrategies.find((s) => s.id === 'baseline');
    expect(baseline).toBeDefined();
    expect(baseline?.p1_bar).toBe(13.0);
    expect(baseline?.p2_bar).toBe(18.0);
    expect(baseline?.status).toBe('DOMINATED');
  });

  it('validates Strategy A (Maximum Recovery)', () => {
    const stratA = mockStrategies.find((s) => s.id === 'strategy_a');
    expect(stratA?.p1_bar).toBe(20.0);
    expect(stratA?.p2_bar).toBe(20.25);
    expect(stratA?.recovery_pct).toBeGreaterThan(85.0);
    expect(stratA?.max_element_recovery_pct).toBeLessThanOrEqual(30.0);
  });

  it('validates Strategy B (Minimum SEC)', () => {
    const stratB = mockStrategies.find((s) => s.id === 'strategy_b');
    expect(stratB?.p1_bar).toBe(15.8);
    expect(stratB?.p2_bar).toBe(15.8);
    expect(stratB?.sec_kwh_m3).toBeLessThan(0.725);
  });

  it('validates Strategy C (Minimum Stress)', () => {
    const stratC = mockStrategies.find((s) => s.id === 'strategy_c');
    expect(stratC?.p1_bar).toBe(10.0);
    expect(stratC?.p2_bar).toBe(14.0);
    expect(stratC?.max_element_recovery_pct).toBeLessThan(15.0);
  });

  it('proves that Strategy D strictly dominates the Baseline', () => {
    const baseline = mockStrategies.find((s) => s.id === 'baseline')!;
    const stratD = mockStrategies.find((s) => s.id === 'strategy_d')!;

    expect(stratD.recovery_pct).toBeGreaterThan(baseline.recovery_pct); // 70.22% vs 69.36%
    expect(stratD.sec_kwh_m3).toBeLessThan(baseline.sec_kwh_m3); // 0.7269 vs 0.7710 kWh/m3
    expect(stratD.max_element_recovery_pct).toBeLessThan(baseline.max_element_recovery_pct); // 20.10% vs 23.69%
    expect(stratD.status).toBe('PARETO OPTIMAL');
  });
});
