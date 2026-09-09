/**
 * Scientific and UI Constants
 * Authoritative Model: RO_MODEL_VERSION = "2.0-pressure-corrected"
 */

export const APP_CONFIG = {
  NAME: 'WaterTwin AI',
  SUBTITLE: 'AI-Enabled Digital Twin for Industrial Water Reuse',
  MODEL_VERSION: 'Model V2.0',
  OPERATING_MODE: 'Virtual Plant',
  DISCLAIMER:
    'This digital twin is currently a virtual-plant research framework. Independent pilot or industrial validation is required before deployment.',
  MEMBRANE_SPEC: 'Toray TM720D-400 (37.0 m² area, 15 elements total in 3:2 staging)',
  STAGE_CONFIGURATION: '3 Vessels in Stage 1 (9 elements) : 2 Vessels in Stage 2 (6 elements)',
  NOMINAL_FEED_FLOW: 30.0, // m3/h
  NOMINAL_FEED_TDS: 2041.0, // mg/L
  NOMINAL_TEMP_C: 25.0, // degC
  INTRINSIC_MEMBRANE_RESISTANCE_RM: 9.8717e13, // m^-1
  MAX_ELEMENT_RECOVERY_LIMIT_PCT: 30.0,
  REFERENCE_CASE_PERMEATE_TDS_LIMIT_MG_L: 18.0,
};

export const SCIENTIFIC_GLOSSARY: Record<string, string> = {
  SEC: 'Specific Energy Consumption — electrical energy required per cubic metre of permeate produced (kWh/m³).',
  Rf: 'Estimated membrane fouling resistance (m⁻¹) inferred dynamically via the Stage 7 EKF virtual sensor.',
  EKF: 'Extended Kalman Filter — physics-informed nonlinear state estimator used to reconstruct unmeasured membrane fouling states.',
  t5: '5% Permeability Decline Analysis Threshold — research benchmark for monitoring gradual flux loss.',
  t10: '10% Permeability Decline Analysis Threshold — intermediate state marker for trajectory tracking.',
  t15: '15% Permeability Decline Analysis Threshold — research evaluation horizon (not an automated cleaning/CIP trigger).',
  NSGA2: 'Non-dominated Sorting Genetic Algorithm II — multi-objective evolutionary optimization algorithm.',
  Aw: 'Membrane pure water permeability coefficient (m/(Pa·s) or LMH/bar).',
  As: 'Membrane solute permeability coefficient (m/s).',
  ConcentrateStaging: 'Topology where Stage 1 concentrate feeds Stage 2 directly to maximize overall water recovery.',
  MaxElemRec: 'Maximum single-element recovery across all 15 elements. Safeguarded below 30% to prevent localized scaling.',
};

export const COLOR_TOKENS = {
  bgPrimary: '#ffffff',
  bgSecondary: '#f8fafc',
  bgCard: '#ffffff',
  textPrimary: '#0f172a',
  textSecondary: '#475569',
  textMuted: '#94a3b8',
  borderLight: '#e2e8f0',
  emeraldPrimary: '#10b981', // Sustainability / Health
  emeraldLight: '#ecfdf5',
  bluePrimary: '#0284c7', // Water / Hydraulic
  blueLight: '#f0f9ff',
  orangePrimary: '#f59e0b', // Warnings / Optimization
  orangeLight: '#fffbeb',
  redWarning: '#ef4444',
};
