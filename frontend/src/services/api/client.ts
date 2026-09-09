/**
 * Centralized API Client
 * Manages HTTP communication with FastAPI backend with graceful fallback.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const override = localStorage.getItem('WT_API_URL');
    if (override) return override;
  }
  return API_BASE_URL;
}

export function getDataMode(): 'api' | 'mock' {
  if (typeof window !== 'undefined') {
    const local = localStorage.getItem('WT_DATA_MODE');
    if (local === 'api' || local === 'mock') return local;
  }
  return (process.env.NEXT_PUBLIC_DATA_MODE as 'api' | 'mock') || 'api';
}

export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit,
  mockFallback?: () => Promise<T> | T
): Promise<T> {
  const mode = getDataMode();
  const url = `${getApiBaseUrl()}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  if (mode === 'mock' && mockFallback) {
    return await Promise.resolve(mockFallback());
  }

  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!res.ok) {
      const errorBody = await res.text();
      console.warn(`API Error [${res.status}] at ${url}:`, errorBody);
      if (mockFallback) {
        return await Promise.resolve(mockFallback());
      }
      throw new Error(`API call failed with status ${res.status}: ${errorBody}`);
    }

    return (await res.json()) as T;
  } catch (err) {
    console.warn(`Network failure connecting to ${url}. Falling back if available.`, err);
    if (mockFallback) {
      return await Promise.resolve(mockFallback());
    }
    throw err;
  }
}
