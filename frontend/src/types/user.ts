export type UserRole = 'admin' | 'org_admin' | 'end_user';

export interface User {
  id: number | string;
  username: string;
  fullName: string;
  email: string;
  role: UserRole;
  orgId?: number;
  orgName?: string;
  department?: string;
  hasChatAccess: boolean; // Org Admin toggle for AI chat access
  createdAt?: string;
}

export interface InviteUserPayload {
  username: string;
  fullName: string;
  email: string;
  role: 'org_admin' | 'end_user';
  orgId: number;
  department?: string;
  hasChatAccess: boolean;
}
