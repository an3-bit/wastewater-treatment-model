/**
 * Engineering Unit and Display Formatters
 */

export function formatFlow(val: number, precision: number = 2): string {
  return `${val.toFixed(precision)} m³/h`;
}

export function formatPressure(val: number, precision: number = 2): string {
  return `${val.toFixed(precision)} bar`;
}

export function formatTDS(val: number, precision: number = 1): string {
  return `${val.toFixed(precision)} mg/L`;
}

export function formatTemperature(val: number, precision: number = 1): string {
  return `${val.toFixed(precision)} °C`;
}

export function formatSEC(val: number, precision: number = 4): string {
  return `${val.toFixed(precision)} kWh/m³`;
}

export function formatPower(val: number, precision: number = 2): string {
  return `${val.toFixed(precision)} kW`;
}

export function formatPercent(val: number, precision: number = 2): string {
  return `${val.toFixed(precision)}%`;
}

export function formatResistanceScientific(val: number): string {
  if (val === 0) return '0 m⁻¹';
  const exponent = Math.floor(Math.log10(Math.abs(val)));
  const mantissa = val / Math.pow(10, exponent);
  return `${mantissa.toFixed(2)} × 10${toSuperscript(exponent)} m⁻¹`;
}

export function formatHours(val: number | null | undefined, precision: number = 1): string {
  if (val === null || val === undefined) return 'N/A';
  return `${val.toFixed(precision)} h`;
}

function toSuperscript(num: number): string {
  const map: Record<string, string> = {
    '-': '⁻',
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
  };
  return num
    .toString()
    .split('')
    .map((c) => map[c] || c)
    .join('');
}
