import { apiClient } from './client';
import { RoundMetric, TrainingStatus, TrainingStartPayload } from '../types/training';

export const MOCK_HISTORY: RoundMetric[] = [
  { id: 1, runId: 'run_init', roundNumber: 1, totalRounds: 5, accuracy: 0.54, loss: 1.82, epsilonSpent: 0.44, cumulativeEpsilon: 0.44, participatingOrgs: ['Hospital Alpha (Cardiology)', 'Medical Center Beta (Oncology)'], orgStatuses: {}, durationSeconds: 2.4, status: 'completed', timestamp: '2026-08-18T18:00:00Z' },
  { id: 2, runId: 'run_init', roundNumber: 2, totalRounds: 5, accuracy: 0.69, loss: 1.25, epsilonSpent: 0.45, cumulativeEpsilon: 0.89, participatingOrgs: ['Hospital Alpha (Cardiology)', 'Medical Center Beta (Oncology)'], orgStatuses: {}, durationSeconds: 2.5, status: 'completed', timestamp: '2026-08-18T18:02:30Z' },
  { id: 3, runId: 'run_init', roundNumber: 3, totalRounds: 5, accuracy: 0.79, loss: 0.88, epsilonSpent: 0.46, cumulativeEpsilon: 1.35, participatingOrgs: ['Hospital Alpha (Cardiology)', 'Medical Center Beta (Oncology)'], orgStatuses: {}, durationSeconds: 2.4, status: 'completed', timestamp: '2026-08-18T18:05:00Z' },
  { id: 4, runId: 'run_init', roundNumber: 4, totalRounds: 5, accuracy: 0.87, loss: 0.55, epsilonSpent: 0.45, cumulativeEpsilon: 1.80, participatingOrgs: ['Hospital Alpha (Cardiology)', 'Medical Center Beta (Oncology)'], orgStatuses: {}, durationSeconds: 2.5, status: 'completed', timestamp: '2026-08-18T18:07:30Z' },
  { id: 5, runId: 'run_init', roundNumber: 5, totalRounds: 5, accuracy: 0.92, loss: 0.32, epsilonSpent: 0.44, cumulativeEpsilon: 2.24, participatingOrgs: ['Hospital Alpha (Cardiology)', 'Medical Center Beta (Oncology)'], orgStatuses: {}, durationSeconds: 2.6, status: 'completed', timestamp: '2026-08-18T18:10:00Z' },
];

/**
 * Start a new federated learning training run (Admin View)
 * TODO: Hooked to backend POST /training/start
 */
export async function startTraining(payload: TrainingStartPayload): Promise<any> {
  const res = await apiClient.post('/training/start', {
    rounds: payload.rounds,
    org_names: payload.orgNames,
    target_accuracy: payload.targetAccuracy,
    max_epsilon: payload.maxEpsilon,
  });
  return res.data;
}

/**
 * Stop active training run (Admin View)
 * TODO: Hooked to backend POST /training/stop
 */
export async function stopTraining(): Promise<any> {
  const res = await apiClient.post('/training/stop');
  return res.data;
}

/**
 * Fetch current training coordinator status
 * TODO: Hooked to backend GET /training/status
 */
export async function fetchTrainingStatus(): Promise<TrainingStatus> {
  try {
    const res = await apiClient.get('/training/status');
    return {
      isTraining: res.data.is_training,
      status: res.data.status,
      runId: res.data.run_id,
      currentRound: res.data.current_round,
      totalRounds: res.data.total_rounds,
      activeOrgs: res.data.active_orgs || [],
      latestAccuracy: res.data.latest_accuracy,
      latestLoss: res.data.latest_loss,
      cumulativeEpsilon: res.data.cumulative_epsilon,
    };
  } catch (error) {
    return {
      isTraining: false,
      status: 'idle',
      runId: null,
      currentRound: 0,
      totalRounds: 0,
      activeOrgs: [],
      latestAccuracy: 0.92,
      latestLoss: 0.32,
      cumulativeEpsilon: 2.24,
    };
  }
}

/**
 * Fetch historical training rounds from SQLite
 * TODO: Hooked to backend GET /training/history
 */
export async function fetchTrainingHistory(): Promise<RoundMetric[]> {
  try {
    const res = await apiClient.get<any[]>('/training/history?limit=30');
    if (res.data && res.data.length > 0) {
      return res.data.map((r) => ({
        id: r.id,
        runId: r.run_id,
        roundNumber: r.round_number,
        totalRounds: r.total_rounds,
        accuracy: r.accuracy,
        loss: r.loss,
        epsilonSpent: r.epsilon_spent,
        cumulativeEpsilon: r.cumulative_epsilon,
        participatingOrgs: r.participating_orgs || [],
        orgStatuses: r.org_statuses || {},
        durationSeconds: r.duration_seconds,
        status: r.status,
        timestamp: r.timestamp,
      }));
    }
    return MOCK_HISTORY;
  } catch (error) {
    return MOCK_HISTORY;
  }
}
