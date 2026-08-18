export type OrgStatus = 'idle' | 'training' | 'done' | 'offline';

export interface OrgDevice {
  id: string;
  name: string;
  type: 'hospital_server' | 'edge_node' | 'radiology_workstation';
  status: OrgStatus;
  cpuUsage: number;
  memoryMb: number;
  ipAddress: string;
  lastSeen: string;
}

export interface Organization {
  id: number;
  name: string;
  status: OrgStatus;
  description?: string;
  clientCount: number;
  localAccuracy: number;
  localLoss: number;
  roundsParticipated: number;
  epsilonSpent: number;
  createdAt: string;
  devices?: OrgDevice[];
}

export interface OrgTelemetry {
  orgId: number;
  orgName: string;
  status: OrgStatus;
  isActivelyTraining: boolean;
  localSamplesCount: number;
  computeTelemetry: {
    cpuUtilizationPercent: number;
    memoryUsageMb: number;
    gpuAcceleration: string;
    networkLatencyMs: number;
    clientDaemonStatus: string;
  };
  edgePrivacyConfiguration: {
    dpMechanism: string;
    gradientClippingNormC: number;
    noiseMultiplierSigma: number;
    localBatchSize: number;
    localEpochsPerRound: number;
    secureAggregationKeyHash: string;
  };
}
