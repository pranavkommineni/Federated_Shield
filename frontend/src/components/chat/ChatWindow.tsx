import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, ShieldCheck, Lock } from 'lucide-react';
import { ChatMessage } from '../../types/training';
import { MessageBubble } from './MessageBubble';
import { sendChatMessage } from '../../api/chat';

interface ChatWindowProps {
  orgName?: string;
  userName?: string;
  hasAccess: boolean;
}

const QUICK_PROMPTS = [
  'What is the recommended threshold for cardiovascular risk?',
  'Explain how Differential Privacy protects patient data',
  'What is the latest global model accuracy?',
  'Show telemetry status for our edge node',
];

export const ChatWindow: React.FC<ChatWindowProps> = ({
  orgName = 'Hospital Alpha (Cardiology)',
  userName = 'Dr. Sarah Connor',
  hasAccess,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      content: `Hello ${userName}! 👋 I am your AI clinical assistant powered by the Privacy-Preserving Federated Model aggregated from **${orgName}** and collaborative silos. How can I assist you with clinical intelligence today?`,
      timestamp: new Date().toISOString(),
      privacyGuarantee: {
        epsilonBound: 'ε = 1.350, δ = 1e-5',
        mechanism: 'Rényi DP Gaussian Mechanism',
        modelCheckpoint: 'FL-Global-Qwen2.5',
        zkProofHash: 'zk-INIT-8942',
      },
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading || !hasAccess) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(text, orgName, userName);
      setMessages((prev) => [...prev, response]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          content: 'Unable to reach the federated model endpoint. Please ensure the backend is running.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!hasAccess) {
    return (
      <div className="h-[600px] flex flex-col items-center justify-center text-center p-8 bg-card/60 rounded-2xl border border-rose-900/30">
        <div className="w-16 h-16 rounded-2xl bg-rose-500/10 text-rose-400 flex items-center justify-center mb-4 border border-rose-500/30">
          <Lock size={32} />
        </div>
        <h3 className="text-xl font-bold text-slate-100">AI Chat Access Restricted</h3>
        <p className="text-sm text-slate-400 max-w-md mt-2">
          Your organization administrator at <strong>{orgName}</strong> has disabled AI chat permissions for your account. Please contact your organization lead to grant access.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[650px] bg-card/90 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-surface/60">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 shadow-glow">
            <Sparkles size={18} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Privacy-Preserved Clinical AI Model
              <span className="text-[10px] bg-emerald-500/15 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30">
                Active
              </span>
            </h3>
            <p className="text-xs text-slate-400">Scoped to {orgName} edge node</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <ShieldCheck size={16} className="text-cyan-400" />
          <span className="hidden sm:inline">Zero Raw Data Leakage Guaranteed</span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex gap-3 mb-4 items-center text-xs text-slate-400">
            <div className="w-8 h-8 rounded-lg bg-surface-elevated flex items-center justify-center animate-pulse">
              <Sparkles size={14} className="text-cyan-400" />
            </div>
            <span>Evaluating query with ai-core model & differential privacy tools...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="px-6 py-2 border-t border-slate-800/60 bg-surface/30 flex gap-2 overflow-x-auto">
        {QUICK_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="text-xs bg-slate-800/70 hover:bg-slate-750 text-slate-300 hover:text-cyan-300 px-3 py-1.5 rounded-full border border-slate-700 whitespace-nowrap transition-colors flex-shrink-0"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-800 bg-surface/70">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about clinical risk models, parameters, or privacy..."
            className="flex-1 bg-surface-elevated border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-primary bg-gradient-to-r from-cyan-500 to-cyan-600 hover:brightness-110 text-slate-950 font-bold px-5 rounded-xl flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-glow"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};
