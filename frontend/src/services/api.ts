/**
 * Base API Client & Environment Configuration
 * Handles seamless switching between 'mock' and 'api' data modes
 */

export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  DATA_MODE: (process.env.NEXT_PUBLIC_DATA_MODE || 'mock') as 'mock' | 'api',
  SIMULATION_LATENCY_MS: 300,
};

export function isMockMode(): boolean {
  if (typeof window !== 'undefined') {
    const localOverride = localStorage.getItem('WT_DATA_MODE');
    if (localOverride === 'mock' || localOverride === 'api') {
      return localOverride === 'mock';
    }
  }
  return API_CONFIG.DATA_MODE === 'mock';
}

export function setDataMode(mode: 'mock' | 'api'): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('WT_DATA_MODE', mode);
    window.dispatchEvent(new Event('wt-mode-change'));
  }
}

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const localUrl = localStorage.getItem('WT_API_URL');
    if (localUrl) return localUrl;
  }
  return API_CONFIG.BASE_URL;
}

export function setApiBaseUrl(url: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('WT_API_URL', url);
  }
}

export async function fetchWithMode<T>(
  endpoint: string,
  mockFallback: () => Promise<T> | T,
  options?: RequestInit
): Promise<T> {
  if (isMockMode()) {
    // Simulate brief network delay for realism if desired
    return await Promise.resolve(mockFallback());
  }

  try {
    const res = await fetch(`${getApiBaseUrl()}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    if (!res.ok) {
      console.warn(`API call to ${endpoint} failed with status ${res.status}. Falling back to mock data.`);
      return await Promise.resolve(mockFallback());
    }

    return (await res.json()) as T;
  } catch (err) {
    console.warn(`Network error reaching ${getApiBaseUrl()}${endpoint}. Falling back to mock data:`, err);
    return await Promise.resolve(mockFallback());
  }
}
