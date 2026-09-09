import { describe, it, expect } from 'vitest';
import { cleaningService } from '../src/services/cleaningService';
import { calculateCleaningSimulation, mockCIPProtocols } from '../src/mocks/mockCleaning';

describe('Chemical Cleaning-In-Place (CIP) & Maintenance Advisor Physics', () => {
  it('retrieves all 4 authoritative CIP chemical protocols', async () => {
    const protocols = await cleaningService.getCIPProtocols();
    expect(protocols).toHaveLength(4);
    const ids = protocols.map((p) => p.id);
    expect(ids).toContain('alkaline_organic');
    expect(ids).toContain('acid_inorganic');
    expect(ids).toContain('combined_two_step');
    expect(ids).toContain('enzymatic_bio');
  });

  it('correctly reduces membrane fouling resistance by (1 - eta)', () => {
    const res = calculateCleaningSimulation({
      cleaning_efficiency: 0.90,
      protocol_id: 'alkaline_organic',
      target_stages: 'both',
    });

    expect(res.efficiency_pct).toBe(90.0);
    expect(res.restored_global_rf_m_inv).toBeLessThan(res.initial_global_rf_m_inv);
    expect(res.restored_flux_decline_pct).toBeLessThan(res.initial_flux_decline_pct);
    expect(res.sec_savings_kwh_m3).toBeGreaterThan(0.0);
    expect(res.extended_operating_life_hours).toBeGreaterThan(0.0);
  });

  it('restores only Stage 1 when target_stages is stage1_only', () => {
    const res = calculateCleaningSimulation({
      cleaning_efficiency: 0.95,
      protocol_id: 'alkaline_organic',
      target_stages: 'stage1_only',
    });

    const s1Zone = res.zone_restorations.find((z) => z.zone_id === 'S1_Lead')!;
    const s2Zone = res.zone_restorations.find((z) => z.zone_id === 'S2_Tail')!;

    expect(s1Zone.restored_rf_e12).toBeLessThan(s1Zone.initial_rf_e12);
    expect(s2Zone.restored_rf_e12).toBe(s2Zone.initial_rf_e12);
  });

  it('restores only Stage 2 when target_stages is stage2_only', () => {
    const res = calculateCleaningSimulation({
      cleaning_efficiency: 0.95,
      protocol_id: 'acid_inorganic',
      target_stages: 'stage2_only',
    });

    const s1Zone = res.zone_restorations.find((z) => z.zone_id === 'S1_Lead')!;
    const s2Zone = res.zone_restorations.find((z) => z.zone_id === 'S2_Tail')!;

    expect(s1Zone.restored_rf_e12).toBe(s1Zone.initial_rf_e12);
    expect(s2Zone.restored_rf_e12).toBeLessThan(s2Zone.initial_rf_e12);
  });
});
