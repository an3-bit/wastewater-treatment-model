/**
 * User & Authentication Types for Wastewater RO Digital Twin Control System
 */

export type UserRole =
  | 'plant_engineer'
  | 'ro_operator'
  | 'optimization_scientist'
  | 'guest_auditor';

export interface UserSession {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  roleTitle: string;
  plantName: string;
  avatarInitials: string;
  accessLevel: 'full_control' | 'operational' | 'analytics_only' | 'read_only';
  token: string;
  loginTime: string;
}

export const PRESET_USERS: Record<UserRole, UserSession> = {
  plant_engineer: {
    id: 'usr-eng-01',
    name: 'Dr. Elena Vance',
    email: 'e.vance@textilewater.org',
    role: 'plant_engineer',
    roleTitle: 'Chief Process Engineer',
    plantName: 'Textile RO Skid Alpha-1 (3:2 Staging)',
    avatarInitials: 'EV',
    accessLevel: 'full_control',
    token: 'jwt_eng_stage7_full_control_token',
    loginTime: new Date().toISOString(),
  },
  ro_operator: {
    id: 'usr-op-02',
    name: 'Marcus Chen',
    email: 'm.chen@textilewater.org',
    role: 'ro_operator',
    roleTitle: 'Senior RO Skid Operator',
    plantName: 'Textile RO Skid Alpha-1 (3:2 Staging)',
    avatarInitials: 'MC',
    accessLevel: 'operational',
    token: 'jwt_op_stage7_telemetry_token',
    loginTime: new Date().toISOString(),
  },
  optimization_scientist: {
    id: 'usr-sci-03',
    name: 'Dr. Amina Al-Mansoor',
    email: 'a.mansoor@textilewater.org',
    role: 'optimization_scientist',
    roleTitle: 'Lead AI & Physics Scientist',
    plantName: 'Digital Twin Simulation Environment',
    avatarInitials: 'AA',
    accessLevel: 'analytics_only',
    token: 'jwt_sci_stage7_surrogate_token',
    loginTime: new Date().toISOString(),
  },
  guest_auditor: {
    id: 'usr-gst-04',
    name: 'Guest Industrial Auditor',
    email: 'auditor@compliance-standard.org',
    role: 'guest_auditor',
    roleTitle: 'Independent Environmental Auditor',
    plantName: 'Textile Water Reuse Demo Plant',
    avatarInitials: 'GA',
    accessLevel: 'read_only',
    token: 'jwt_guest_demo_token',
    loginTime: new Date().toISOString(),
  },
};
