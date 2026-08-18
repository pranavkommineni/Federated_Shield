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
    username: 'admin_ananya',
    fullName: 'Dr. Ananya Sharma',
    email: 'ananya.sharma@federatedshield.gov.in',
    role: 'admin',
    department: 'National Medical AI Directorate',
    hasChatAccess: true,
    createdAt: '2026-08-01T10:00:00Z',
  },
  org_admin_alpha: {
    id: 2,
    username: 'lead_rajesh',
    fullName: 'Dr. Rajesh Varma',
    email: 'rajesh.varma@aiims.edu.in',
    role: 'org_admin',
    orgId: 1,
    orgName: 'AIIMS New Delhi (Cardiology)',
    department: 'Cardiology Division & Health Informatics',
    hasChatAccess: true,
    createdAt: '2026-08-05T12:00:00Z',
  },
  org_admin_beta: {
    id: 3,
    username: 'lead_vikram',
    fullName: 'Dr. Vikram Rao',
    email: 'vikram.rao@apollohospitals.com',
    role: 'org_admin',
    orgId: 2,
    orgName: 'Apollo Hospitals Chennai (Oncology)',
    department: 'Radiation Oncology Department',
    hasChatAccess: true,
    createdAt: '2026-08-06T14:00:00Z',
  },
  end_user_granted: {
    id: 4,
    username: 'dr_priya_nair',
    fullName: 'Dr. Priya Nair',
    email: 'priya.nair@aiims.edu.in',
    role: 'end_user',
    orgId: 1,
    orgName: 'AIIMS New Delhi (Cardiology)',
    department: 'Cardiovascular Diagnostics',
    hasChatAccess: true,
    createdAt: '2026-08-10T09:30:00Z',
  },
  end_user_revoked: {
    id: 5,
    username: 'intern_aarav',
    fullName: 'Aarav Patel (Access Revoked)',
    email: 'aarav.patel@aiims.edu.in',
    role: 'end_user',
    orgId: 1,
    orgName: 'AIIMS New Delhi (Cardiology)',
    department: 'Clinical Cardiology Intern Silo',
    hasChatAccess: false,
    createdAt: '2026-08-12T11:15:00Z',
  },
};

export const useAuthStore = create<AuthState>((set) => ({
  currentUser: null,
  isAuthenticated: false,
  selectedOrgId: 1,
  selectedOrgName: 'AIIMS New Delhi (Cardiology)',

  loginAs: (role: UserRole, customUser?: Partial<User>) => {
    let selectedMock: User;

    if (customUser && customUser.username) {
      selectedMock = {
        id: customUser.id || Date.now(),
        username: customUser.username,
        fullName: customUser.fullName || 'Test User',
        email: customUser.email || 'user@aiims.edu.in',
        role: role,
        orgId: customUser.orgId || 1,
        orgName: customUser.orgName || 'AIIMS New Delhi (Cardiology)',
        hasChatAccess: customUser.hasChatAccess ?? true,
        department: customUser.department || 'General Medicine',
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
      selectedOrgName: selectedMock.orgName || 'AIIMS New Delhi (Cardiology)',
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
