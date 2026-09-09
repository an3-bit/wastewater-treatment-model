import { describe, it, expect } from 'vitest';
import { mockMembraneZones, mockPhysicalElements } from '../src/mocks/mockMembranes';

describe('Membrane 15-Element to 6-Zone Mapping Integrity', () => {
  it('contains exactly 6 axial membrane zones', () => {
    expect(mockMembraneZones).toHaveLength(6);
    const zoneIds = mockMembraneZones.map((z) => z.zone_id);
    expect(zoneIds).toEqual([
      'S1_Lead',
      'S1_Mid',
      'S1_Tail',
      'S2_Lead',
      'S2_Mid',
      'S2_Tail',
    ]);
  });

  it('maps exactly 15 physical elements across 2 stages (9 in S1, 6 in S2)', () => {
    expect(mockPhysicalElements).toHaveLength(15);
    const stage1Count = mockPhysicalElements.filter((e) => e.stage === 1).length;
    const stage2Count = mockPhysicalElements.filter((e) => e.stage === 2).length;

    expect(stage1Count).toBe(9); // 3 vessels x 3 elements
    expect(stage2Count).toBe(6); // 2 vessels x 3 elements
  });

  it('verifies that each physical element maps to a valid 6-zone axial state', () => {
    const validZoneIds = new Set(mockMembraneZones.map((z) => z.zone_id));

    mockPhysicalElements.forEach((element) => {
      expect(validZoneIds.has(element.zone_id)).toBe(true);
      expect(element.rf_m_inv).toBeGreaterThan(0);
      expect(element.permeability_decline_pct).toBeGreaterThanOrEqual(0);
    });
  });

  it('confirms Stage 1 parallel vessels have identical axial zone properties', () => {
    // S1 Vessel 1 Lead (idx 0), S1 Vessel 2 Lead (idx 3), S1 Vessel 3 Lead (idx 6)
    const v1Lead = mockPhysicalElements[0];
    const v2Lead = mockPhysicalElements[3];
    const v3Lead = mockPhysicalElements[6];

    expect(v1Lead.zone_id).toBe('S1_Lead');
    expect(v2Lead.zone_id).toBe('S1_Lead');
    expect(v3Lead.zone_id).toBe('S1_Lead');
    expect(v1Lead.rf_m_inv).toBe(v2Lead.rf_m_inv);
    expect(v2Lead.rf_m_inv).toBe(v3Lead.rf_m_inv);
  });
});
