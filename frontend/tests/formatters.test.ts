import { describe, it, expect } from 'vitest';
import {
  formatFlow,
  formatPressure,
  formatTDS,
  formatTemperature,
  formatSEC,
  formatPower,
  formatPercent,
  formatResistanceScientific,
  formatHours,
} from '../src/utils/formatters';

describe('Engineering Unit Formatters', () => {
  it('formats volumetric flow rate with m³/h unit', () => {
    expect(formatFlow(30.0)).toBe('30.00 m³/h');
    expect(formatFlow(21.074, 2)).toBe('21.07 m³/h');
  });

  it('formats hydraulic pressure with bar unit', () => {
    expect(formatPressure(16.06)).toBe('16.06 bar');
    expect(formatPressure(18.0, 1)).toBe('18.0 bar');
  });

  it('formats TDS salinity with mg/L unit', () => {
    expect(formatTDS(2041.0)).toBe('2041.0 mg/L');
    expect(formatTDS(7.21, 2)).toBe('7.21 mg/L');
  });

  it('formats temperature with °C unit', () => {
    expect(formatTemperature(25.0)).toBe('25.0 °C');
  });

  it('formats SEC with 4 decimal places and kWh/m³ unit', () => {
    expect(formatSEC(0.7269)).toBe('0.7269 kWh/m³');
    expect(formatSEC(0.771)).toBe('0.7710 kWh/m³');
  });

  it('formats electrical power with kW unit', () => {
    expect(formatPower(15.32)).toBe('15.32 kW');
  });

  it('formats percentages correctly', () => {
    expect(formatPercent(70.22)).toBe('70.22%');
    expect(formatPercent(29.99, 1)).toBe('30.0%');
  });

  it('formats fouling resistance into scientific notation with unicode superscripts', () => {
    expect(formatResistanceScientific(2.15e12)).toBe('2.15 × 10¹² m⁻¹');
    expect(formatResistanceScientific(9.87e13)).toBe('9.87 × 10¹³ m⁻¹');
    expect(formatResistanceScientific(0)).toBe('0 m⁻¹');
  });

  it('formats remaining hours correctly with null handling', () => {
    expect(formatHours(34.5)).toBe('34.5 h');
    expect(formatHours(null)).toBe('N/A');
    expect(formatHours(undefined)).toBe('N/A');
  });
});
