export interface RoundMetric {
  id: number;
  runId: string;
  roundNumber: number;
  totalRounds: number;
  accuracy: number;
  loss: number;
  epsilonSpent: number;
  cumulativeEpsilon: number;
  participatingOrgs: string[];
  orgStatuses: Record<string, string>;
  durationSeconds: number;
  status: 'completed' | 'aborted' | 'failed';
  timestamp: string;
}

export interface TrainingStatus {
  isTraining: boolean;
  status: 'idle' | 'running' | 'stopping' | 'completed' | 'aborted';
  runId: string | null;
  currentRound: number;
  totalRounds: number;
  activeOrgs: string[];
  latestAccuracy: number | null;
  latestLoss: number | null;
  cumulativeEpsilon: number | null;
}

export interface TrainingStartPayload {
  rounds: number;
  orgNames?: string[];
  targetAccuracy?: number;
  maxEpsilon?: number;
}

export interface WebSocketMetricEvent {
  event: 'status_update' | 'training_started' | 'round_complete' | 'training_completed' | 'training_stopped' | 'error' | 'pong';
  run_id?: string;
  round?: number;
  total_rounds?: number;
  accuracy?: number;
  loss?: number;
  epsilon_spent?: number;
  cumulative_epsilon?: number;
  org_statuses?: Record<string, string>;
  duration_seconds?: number;
  timestamp?: string;
  message?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  privacyGuarantee?: {
    epsilonBound: string;
    mechanism: string;
    modelCheckpoint: string;
    zkProofHash: string;
  };
}
