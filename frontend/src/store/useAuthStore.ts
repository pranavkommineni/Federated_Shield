import { create } from 'zustand';
import { User, UserRole } from '../types/user';

interface AuthState {
  currentUser: User | null;
  isAuthenticated: boolean;
  selectedOrgId: number;
  selectedOrgName: string;
  loginAs: (role: UserRole, customUser?: Partial<User>) => void;
  logout: () => void;
  setSelectedOrg: (orgId: number, orgName: string) => void;
  toggleUserChatAccess: (userId: number | string, hasAccess: boolean) => void;
}

// Default mock personas for 1-click testing
export const MOCK_USERS: Record<string, User> = {
  admin: {
    id: 1,
    username: 'admin_evelyn',
    fullName: 'Dr. Evelyn Vance',
    email: 'admin@federix.shield',
    role: 'admin',
    department: 'Global FL Core Governance',
    hasChatAccess: true,
    createdAt: '2026-08-01T10:00:00Z',
  },
  org_admin_alpha: {
    id: 2,
    username: 'lead_rajesh',
    fullName: 'Dr. Rajesh Varma',
    email: 'varma@hospital-alpha.org',
    role: 'org_admin',
    orgId: 1,
    orgName: 'Hospital Alpha (Cardiology)',
    department: 'Cardiology Division',
    hasChatAccess: true,
    createdAt: '2026-08-05T12:00:00Z',
  },
  org_admin_beta: {
    id: 3,
    username: 'lead_elena',
    fullName: 'Dr. Elena Rostova',
    email: 'elena@med-beta.org',
    role: 'org_admin',
    orgId: 2,
    orgName: 'Medical Center Beta (Oncology)',
    department: 'Oncology Division',
    hasChatAccess: true,
    createdAt: '2026-08-06T14:00:00Z',
  },
  end_user_granted: {
    id: 4,
    username: 'dr_sarah_c',
    fullName: 'Dr. Sarah Connor',
    email: 'sarah.connor@hospital-alpha.org',
    role: 'end_user',
    orgId: 1,
    orgName: 'Hospital Alpha (Cardiology)',
    department: 'Cardiovascular Diagnostics',
    hasChatAccess: true,
    createdAt: '2026-08-10T09:30:00Z',
  },
  end_user_revoked: {
    id: 5,
    username: 'intern_alex',
    fullName: 'Alex Rivera (Access Revoked)',
    email: 'alex.rivera@hospital-alpha.org',
    role: 'end_user',
    orgId: 1,
    orgName: 'Hospital Alpha (Cardiology)',
    department: 'Cardiology Intern Silo',
    hasChatAccess: false,
    createdAt: '2026-08-12T11:15:00Z',
  },
};

export const useAuthStore = create<AuthState>((set) => ({
  // Start unauthenticated so user sees the Login page
  currentUser: null,
  isAuthenticated: false,
  selectedOrgId: 1,
  selectedOrgName: 'Hospital Alpha (Cardiology)',

  loginAs: (role: UserRole, customUser?: Partial<User>) => {
    let selectedMock: User;

    if (customUser && customUser.username) {
      selectedMock = {
        id: customUser.id || Date.now(),
        username: customUser.username,
        fullName: customUser.fullName || 'Test User',
        email: customUser.email || 'user@example.com',
        role: role,
        orgId: customUser.orgId || 1,
        orgName: customUser.orgName || 'Hospital Alpha (Cardiology)',
        hasChatAccess: customUser.hasChatAccess ?? true,
        department: customUser.department || 'General',
        createdAt: customUser.createdAt || new Date().toISOString(),
      };
    } else {
      if (role === 'admin') selectedMock = MOCK_USERS.admin;
      else if (role === 'org_admin') selectedMock = MOCK_USERS.org_admin_alpha;
      else selectedMock = MOCK_USERS.end_user_granted;
    }

    set({
      currentUser: selectedMock,
      isAuthenticated: true,
      selectedOrgId: selectedMock.orgId || 1,
      selectedOrgName: selectedMock.orgName || 'Hospital Alpha (Cardiology)',
    });
  },

  logout: () => {
    set({
      currentUser: null,
      isAuthenticated: false,
    });
  },

  setSelectedOrg: (orgId: number, orgName: string) => {
    set((state) => ({
      selectedOrgId: orgId,
      selectedOrgName: orgName,
      currentUser: state.currentUser
        ? { ...state.currentUser, orgId, orgName }
        : null,
    }));
  },

  toggleUserChatAccess: (userId: number | string, hasAccess: boolean) => {
    set((state) => {
      if (state.currentUser && state.currentUser.id === userId) {
        return {
          currentUser: {
            ...state.currentUser,
            hasChatAccess: hasAccess,
          },
        };
      }
      return state;
    });
  },
}));
