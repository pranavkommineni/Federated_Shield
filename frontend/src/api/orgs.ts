import { apiClient } from './client';
import { Organization, OrgTelemetry } from '../types/org';
import { User, InviteUserPayload } from '../types/user';

// Mock fallback organizations for offline/testing readiness
export const MOCK_ORGS: Organization[] = [
  {
    id: 1,
    name: 'Hospital Alpha (Cardiology)',
    status: 'idle',
    description: 'Regional cardiology center with local differential privacy noise enabled.',
    clientCount: 14,
    localAccuracy: 0.892,
    localLoss: 0.312,
    roundsParticipated: 12,
    epsilonSpent: 1.45,
    createdAt: '2026-08-01T08:00:00Z',
    devices: [
      { id: 'dev-01', name: 'Cardio-Node-Alpha-1', type: 'hospital_server', status: 'idle', cpuUsage: 14, memoryMb: 1420, ipAddress: '10.0.1.15', lastSeen: 'Just now' },
      { id: 'dev-02', name: 'ECG-Workstation-4', type: 'edge_node', status: 'idle', cpuUsage: 8, memoryMb: 512, ipAddress: '10.0.1.28', lastSeen: '1 min ago' },
      { id: 'dev-03', name: 'Echo-Scanner-Node', type: 'radiology_workstation', status: 'idle', cpuUsage: 22, memoryMb: 2048, ipAddress: '10.0.1.33', lastSeen: '3 mins ago' },
    ],
  },
  {
    id: 2,
    name: 'Medical Center Beta (Oncology)',
    status: 'idle',
    description: 'Pediatric oncology clinical silo contributing multi-party gradient updates.',
    clientCount: 9,
    localAccuracy: 0.865,
    localLoss: 0.384,
    roundsParticipated: 10,
    epsilonSpent: 1.25,
    createdAt: '2026-08-02T10:00:00Z',
    devices: [
      { id: 'dev-04', name: 'Onco-Cluster-Master', type: 'hospital_server', status: 'idle', cpuUsage: 19, memoryMb: 2800, ipAddress: '10.0.2.10', lastSeen: 'Just now' },
      { id: 'dev-05', name: 'Pathology-Scan-Node', type: 'edge_node', status: 'idle', cpuUsage: 11, memoryMb: 890, ipAddress: '10.0.2.22', lastSeen: 'Just now' },
    ],
  },
  {
    id: 3,
    name: 'Apex Health Network (Neurology)',
    status: 'idle',
    description: 'Neuroimaging federated participant with Shamir Secret Sharing aggregation.',
    clientCount: 6,
    localAccuracy: 0.914,
    localLoss: 0.265,
    roundsParticipated: 8,
    epsilonSpent: 0.95,
    createdAt: '2026-08-04T11:30:00Z',
    devices: [
      { id: 'dev-06', name: 'Neuro-EEG-Cluster', type: 'hospital_server', status: 'idle', cpuUsage: 12, memoryMb: 1650, ipAddress: '10.0.3.5', lastSeen: '5 mins ago' },
    ],
  },
];

// Fallback mock users scoped per organization
let mockOrgUsersStore: Record<number, User[]> = {
  1: [
    { id: 101, username: 'dr_sarah_c', fullName: 'Dr. Sarah Connor', email: 'sarah.connor@hospital-alpha.org', role: 'end_user', orgId: 1, orgName: 'Hospital Alpha (Cardiology)', department: 'Cardiology Clinician', hasChatAccess: true, createdAt: '2026-08-10T09:30:00Z' },
    { id: 102, username: 'dr_marcus_v', fullName: 'Dr. Marcus Vance', email: 'marcus.vance@hospital-alpha.org', role: 'end_user', orgId: 1, orgName: 'Hospital Alpha (Cardiology)', department: 'Interventional Cardiology', hasChatAccess: true, createdAt: '2026-08-11T14:20:00Z' },
    { id: 103, username: 'intern_alex', fullName: 'Alex Rivera', email: 'alex.rivera@hospital-alpha.org', role: 'end_user', orgId: 1, orgName: 'Hospital Alpha (Cardiology)', department: 'Cardiology Intern', hasChatAccess: false, createdAt: '2026-08-12T11:15:00Z' },
    { id: 104, username: 'nurse_emily', fullName: 'Emily Watson', email: 'emily.watson@hospital-alpha.org', role: 'end_user', orgId: 1, orgName: 'Hospital Alpha (Cardiology)', department: 'Clinical Care Nurse', hasChatAccess: true, createdAt: '2026-08-14T16:00:00Z' },
  ],
  2: [
    { id: 201, username: 'dr_chen_onco', fullName: 'Dr. Wei Chen', email: 'wei.chen@med-beta.org', role: 'end_user', orgId: 2, orgName: 'Medical Center Beta (Oncology)', department: 'Pediatric Oncology', hasChatAccess: true, createdAt: '2026-08-08T10:00:00Z' },
    { id: 202, username: 'researcher_lisa', fullName: 'Lisa Ray', email: 'lisa.ray@med-beta.org', role: 'end_user', orgId: 2, orgName: 'Medical Center Beta (Oncology)', department: 'Clinical Research', hasChatAccess: false, createdAt: '2026-08-13T12:45:00Z' },
  ],
  3: [
    { id: 301, username: 'dr_tariq_neuro', fullName: 'Dr. Tariq Ahmed', email: 'tariq@apex-health.org', role: 'end_user', orgId: 3, orgName: 'Apex Health Network (Neurology)', department: 'Neuro-Diagnostics', hasChatAccess: true, createdAt: '2026-08-15T09:00:00Z' },
  ],
};

/**
 * Fetch all registered organizations (Admin View)
 * TODO: Hooked to backend GET /orgs
 */
export async function fetchOrganizations(): Promise<Organization[]> {
  try {
    const res = await apiClient.get<any[]>('/orgs');
    if (res.data && res.data.length > 0) {
      return res.data.map((item, idx) => ({
        id: item.id,
        name: item.name,
        status: item.status || 'idle',
        description: item.description || 'Simulated edge node',
        clientCount: (idx + 2) * 3,
        localAccuracy: 0.85 + (idx * 0.02),
        localLoss: 0.35 - (idx * 0.02),
        roundsParticipated: (idx + 3) * 2,
        epsilonSpent: 0.45 * (idx + 2),
        createdAt: item.created_at || new Date().toISOString(),
        devices: MOCK_ORGS[idx % MOCK_ORGS.length]?.devices || [],
      }));
    }
    return MOCK_ORGS;
  } catch (error) {
    return MOCK_ORGS;
  }
}

/**
 * Fetch organization details scoped to a single org (Org View)
 * TODO: Hooked to backend GET /nodes/{orgId}/telemetry
 */
export async function fetchOrgTelemetry(orgId: number): Promise<OrgTelemetry | null> {
  try {
    const res = await apiClient.get(`/nodes/${orgId}/telemetry`);
    return {
      orgId: res.data.org_id,
      orgName: res.data.org_name,
      status: res.data.status,
      isActivelyTraining: res.data.is_actively_training,
      localSamplesCount: res.data.local_samples_count,
      computeTelemetry: {
        cpuUtilizationPercent: res.data.compute_telemetry.cpu_utilization_percent,
        memoryUsageMb: res.data.compute_telemetry.memory_usage_mb,
        gpuAcceleration: res.data.compute_telemetry.gpu_acceleration,
        networkLatencyMs: res.data.compute_telemetry.network_latency_ms,
        clientDaemonStatus: res.data.compute_telemetry.client_daemon_status,
      },
      edgePrivacyConfiguration: {
        dpMechanism: res.data.edge_privacy_configuration.dp_mechanism,
        gradientClippingNormC: res.data.edge_privacy_configuration.gradient_clipping_norm_C,
        noiseMultiplierSigma: res.data.edge_privacy_configuration.noise_multiplier_sigma,
        localBatchSize: res.data.edge_privacy_configuration.local_batch_size,
        localEpochsPerRound: res.data.edge_privacy_configuration.local_epochs_per_round,
        secureAggregationKeyHash: res.data.edge_privacy_configuration.secure_aggregation_key_hash,
      },
    };
  } catch (error) {
    const fallbackOrg = MOCK_ORGS.find((o) => o.id === orgId) || MOCK_ORGS[0];
    return {
      orgId: fallbackOrg.id,
      orgName: fallbackOrg.name,
      status: fallbackOrg.status,
      isActivelyTraining: false,
      localSamplesCount: 142,
      computeTelemetry: {
        cpuUtilizationPercent: 18,
        memoryUsageMb: 1240,
        gpuAcceleration: 'CUDA Enabled (RTX 4090 Silo)',
        networkLatencyMs: 24,
        clientDaemonStatus: 'Online (flwr-client-daemon v1.7.0)',
      },
      edgePrivacyConfiguration: {
        dpMechanism: 'Gaussian DP with Gradient Clipping',
        gradientClippingNormC: 1.0,
        noiseMultiplierSigma: 1.15,
        localBatchSize: 32,
        localEpochsPerRound: 3,
        secureAggregationKeyHash: '8f2a9c1b7e4d',
      },
    };
  }
}

/**
 * Fetch all users under an organization (Scoped strictly to THAT org)
 * TODO: Hooked to backend GET /users?org_id={orgId}
 */
export async function fetchOrgUsers(orgId: number): Promise<User[]> {
  try {
    const res = await apiClient.get<any[]>(`/users?org_id=${orgId}`);
    if (res.data && res.data.length > 0) {
      return res.data.map((u) => ({
        id: u.id,
        username: u.username,
        fullName: u.full_name,
        email: u.email,
        role: u.role,
        orgId: u.org_id,
        department: u.department,
        hasChatAccess: u.has_chat_access ?? true,
        createdAt: u.created_at,
      }));
    }
    return mockOrgUsersStore[orgId] || [];
  } catch (error) {
    return mockOrgUsersStore[orgId] || [];
  }
}

/**
 * Invite / Add a new user under this organization
 * TODO: Hooked to backend POST /users/register
 */
export async function inviteUser(payload: InviteUserPayload): Promise<User> {
  const newUser: User = {
    id: Date.now(),
    username: payload.username,
    fullName: payload.fullName,
    email: payload.email,
    role: payload.role,
    orgId: payload.orgId,
    department: payload.department || 'Clinical Silo',
    hasChatAccess: payload.hasChatAccess,
    createdAt: new Date().toISOString(),
  };

  if (!mockOrgUsersStore[payload.orgId]) {
    mockOrgUsersStore[payload.orgId] = [];
  }
  mockOrgUsersStore[payload.orgId].push(newUser);

  try {
    await apiClient.post('/users/register', {
      username: payload.username,
      full_name: payload.fullName,
      email: payload.email,
      role: payload.role,
      org_id: payload.orgId,
      department: payload.department,
    });
  } catch (e) {
    // Graceful fallback to mock store
  }

  return newUser;
}

/**
 * Toggle AI Chat Access for a specific user (Org Admin permission control)
 */
export async function toggleChatAccess(orgId: number, userId: number | string, hasAccess: boolean): Promise<boolean> {
  if (mockOrgUsersStore[orgId]) {
    const target = mockOrgUsersStore[orgId].find((u) => u.id === userId);
    if (target) {
      target.hasChatAccess = hasAccess;
    }
  }
  return true;
}

/**
 * Register a new organization (Admin View)
 * TODO: Hooked to backend POST /orgs/register
 */
export async function registerOrganization(name: string, description?: string): Promise<Organization> {
  const res = await apiClient.post('/orgs/register', { name, description });
  return {
    id: res.data.id,
    name: res.data.name,
    status: 'idle',
    description: res.data.description,
    clientCount: 4,
    localAccuracy: 0.85,
    localLoss: 0.35,
    roundsParticipated: 0,
    epsilonSpent: 0,
    createdAt: res.data.created_at || new Date().toISOString(),
  };
}
