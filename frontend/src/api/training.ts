import { apiClient } from './client';
import { TrainingStatus, RoundMetric, StartTrainingPayload } from '../types/training';

export const MOCK_ROUNDS: RoundMetric[] = [
  { id: 1, runId: 'run_init', roundNumber: 1, totalRounds: 5, accuracy: 0.54, loss: 1.82, epsilonSpent: 0.44, cumulativeEpsilon: 0.44, participatingOrgs: ['AIIMS New Delhi (Cardiology)', 'Apollo Hospitals Chennai (Oncology)'], orgStatuses: {}, durationSeconds: 2.4, status: 'completed', timestamp: '2026-08-18T18:00:00Z' },
  { id: 2, runId: 'run_init', roundNumber: 2, totalRounds: 5, accuracy: 0.69, loss: 1.25, epsilonSpent: 0.45, cumulativeEpsilon: 0.89, participatingOrgs: ['AIIMS New Delhi (Cardiology)', 'Apollo Hospitals Chennai (Oncology)'], orgStatuses: {}, durationSeconds: 2.5, status: 'completed', timestamp: '2026-08-18T18:02:30Z' },
  { id: 3, runId: 'run_init', roundNumber: 3, totalRounds: 5, accuracy: 0.79, loss: 0.88, epsilonSpent: 0.46, cumulativeEpsilon: 1.35, participatingOrgs: ['AIIMS New Delhi (Cardiology)', 'Apollo Hospitals Chennai (Oncology)'], orgStatuses: {}, durationSeconds: 2.4, status: 'completed', timestamp: '2026-08-18T18:05:00Z' },
  { id: 4, runId: 'run_init', roundNumber: 4, totalRounds: 5, accuracy: 0.87, loss: 0.55, epsilonSpent: 0.45, cumulativeEpsilon: 1.80, participatingOrgs: ['AIIMS New Delhi (Cardiology)', 'Apollo Hospitals Chennai (Oncology)'], orgStatuses: {}, durationSeconds: 2.5, status: 'completed', timestamp: '2026-08-18T18:07:30Z' },
  { id: 5, runId: 'run_init', roundNumber: 5, totalRounds: 5, accuracy: 0.92, loss: 0.32, epsilonSpent: 0.44, cumulativeEpsilon: 2.24, participatingOrgs: ['AIIMS New Delhi (Cardiology)', 'Apollo Hospitals Chennai (Oncology)'], orgStatuses: {}, durationSeconds: 2.6, status: 'completed', timestamp: '2026-08-18T18:10:00Z' },
];

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
      runId: 'mock_run_1',
      currentRound: 5,
      totalRounds: 5,
      activeOrgs: ['AIIMS New Delhi (Cardiology)', 'Apollo Hospitals Chennai (Oncology)', 'Fortis Healthcare Bengaluru (Neurology)'],
      latestAccuracy: 0.924,
      latestLoss: 0.318,
      cumulativeEpsilon: 2.24,
    };
  }
}

export async function fetchTrainingHistory(): Promise<RoundMetric[]> {
  try {
    const res = await apiClient.get<any[]>('/training/history');
    if (res.data && res.data.length > 0) {
      return res.data.map((item) => ({
        id: item.id,
        runId: item.run_id,
        roundNumber: item.round_number,
        totalRounds: item.total_rounds,
        accuracy: item.accuracy,
        loss: item.loss,
        epsilonSpent: item.epsilon_spent,
        cumulativeEpsilon: item.cumulative_epsilon,
        participatingOrgs: item.participating_orgs || [],
        orgStatuses: item.org_statuses || {},
        durationSeconds: item.duration_seconds,
        status: item.status,
        timestamp: item.timestamp,
      }));
    }
    return MOCK_ROUNDS;
  } catch (error) {
    return MOCK_ROUNDS;
  }
}

export async function startTraining(payload: StartTrainingPayload): Promise<any> {
  const res = await apiClient.post('/training/start', {
    rounds: payload.rounds,
    target_accuracy: payload.targetAccuracy,
    max_epsilon: payload.maxEpsilon,
    org_names: payload.orgNames,
  });
  return res.data;
}

export async function stopTraining(): Promise<any> {
  const res = await apiClient.post('/training/stop');
  return res.data;
}
