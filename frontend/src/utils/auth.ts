import { UserRole, UserSession, PRESET_USERS } from '@/types/auth';

const AUTH_STORAGE_KEY = 'WT_USER_SESSION';

export function getActiveSession(): UserSession {
  if (typeof window === 'undefined') {
    return PRESET_USERS.plant_engineer;
  }

  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch {
    // ignore json error
  }

  return PRESET_USERS.plant_engineer;
}

export function saveSession(session: UserSession): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
  }
}

export function loginAsRole(role: UserRole): UserSession {
  const session = {
    ...PRESET_USERS[role],
    loginTime: new Date().toISOString(),
  };
  saveSession(session);
  return session;
}

export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_STORAGE_KEY);
  }
}

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return true;
  return !!localStorage.getItem(AUTH_STORAGE_KEY);
}
