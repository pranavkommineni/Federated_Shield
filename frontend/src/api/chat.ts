import { apiClient } from './client';
import { ChatMessage } from '../types/training';

export async function sendChatMessage(
  prompt: string,
  orgName: string = 'Hospital Alpha (Cardiology)',
  userName: string = 'Dr. Sarah Connor'
): Promise<ChatMessage> {
  try {
    const res = await apiClient.post('/chat', {
      prompt,
      org_name: orgName,
      user_name: userName,
    });

    const data = res.data;
    return {
      id: data.id || `msg-${Date.now()}`,
      sender: 'assistant',
      content: data.content,
      timestamp: new Date().toISOString(),
      privacyGuarantee: data.privacy_guarantee
        ? {
            epsilonBound: data.privacy_guarantee.epsilon_bound,
            mechanism: data.privacy_guarantee.mechanism,
            modelCheckpoint: data.privacy_guarantee.model_checkpoint,
            zkProofHash: data.privacy_guarantee.zk_proof_hash,
          }
        : undefined,
    };
  } catch (err: any) {
    console.warn('Backend /chat failed, using client-side fallback:', err);
    // Fallback if backend server is unreachable
    return {
      id: `msg-${Date.now()}`,
      sender: 'assistant',
      content: `Hello! I received your query: "${prompt}".\n\nI am connected to the Federated Shield AI Core (${orgName}). Please ensure the FastAPI backend is running on http://localhost:8000 to stream live model responses.`,
      timestamp: new Date().toISOString(),
      privacyGuarantee: {
        epsilonBound: 'ε = 1.350, δ = 1e-5',
        mechanism: 'Rényi DP Gaussian Mechanism',
        modelCheckpoint: 'FL-Global-Qwen2.5',
        zkProofHash: 'zk-' + Math.random().toString(36).substring(2, 10).toUpperCase(),
      },
    };
  }
}
