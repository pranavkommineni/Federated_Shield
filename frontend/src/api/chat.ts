import { apiClient } from './client';
import { ChatMessage } from '../types/training';

export async function sendChatMessage(
  message: string,
  orgName: string = 'AIIMS New Delhi (Cardiology)',
  userName: string = 'Dr. Priya Nair'
): Promise<ChatMessage> {
  try {
    const res = await apiClient.post('/chat', {
      message,
      org_name: orgName,
      user_name: userName,
    });

    return {
      id: res.data.id || `msg-${Date.now()}`,
      sender: res.data.sender || 'assistant',
      content: res.data.content,
      timestamp: res.data.timestamp || new Date().toISOString(),
      privacyGuarantee: res.data.privacy_guarantee
        ? {
            epsilonBound: res.data.privacy_guarantee.epsilon_bound,
            mechanism: res.data.privacy_guarantee.mechanism,
            modelCheckpoint: res.data.privacy_guarantee.model_checkpoint,
            zkProofHash: res.data.privacy_guarantee.zk_proof_hash,
          }
        : undefined,
    };
  } catch (error) {
    throw error;
  }
}
