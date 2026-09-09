/**
 * Standard 10-Sensor Skid Telemetry Types
 * Reference: Stage 7 Standard Instrumentation Case 2
 */

export type SensorStatus = 'Online' | 'Warning' | 'Offline' | 'Calibrating';

export interface SensorReading {
  id: string;
  tag: string;
  name: string;
  symbol: string;
  current_value: number;
  unit: string;
  status: SensorStatus;
  last_update: string;
  range_min: number;
  range_max: number;
  noise_std: number;
  location: string;
  history_sparkline: number[];
  category: 'hydraulic' | 'quality' | 'thermal' | 'energy';
}

export interface SensorSuiteSummary {
  total_sensors: number;
  online_count: number;
  warning_count: number;
  offline_count: number;
  last_scan_timestamp: string;
  sensors: SensorReading[];
}
