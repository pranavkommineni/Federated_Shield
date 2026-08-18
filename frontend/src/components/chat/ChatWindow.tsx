import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Lock } from 'lucide-react';
import { ChatMessage } from '../../types/training';
import { MessageBubble } from './MessageBubble';
import { sendChatMessage } from '../../api/chat';

interface ChatWindowProps {
  orgName?: string;
  userName?: string;
  hasAccess: boolean;
}

const QUICK_PROMPTS = [
  'What is the threshold for cardiovascular risk?',
  'How does Differential Privacy protect data?',
  'What is the current model accuracy?',
];

export const ChatWindow: React.FC<ChatWindowProps> = ({
  orgName = 'AIIMS New Delhi (Cardiology)',
  userName = 'Dr. Priya Nair',
  hasAccess,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      content: `Hello ${userName}! How can I assist you with clinical guidelines, patient risk analysis, or privacy metrics today?`,
      timestamp: new Date().toISOString(),
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
          content: 'Unable to reach the assistant right now. Please check if the backend server is running.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!hasAccess) {
    return (
      <div className="h-[550px] flex flex-col items-center justify-center text-center p-8 bg-white rounded-2xl border border-rose-200 shadow-sm">
        <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mb-3 border border-rose-100">
          <Lock size={22} />
        </div>
        <h3 className="text-base font-bold text-slate-900">AI Chat Access Restricted</h3>
        <p className="text-xs text-slate-600 max-w-sm mt-1 leading-relaxed">
          Your organization administrator at <strong>{orgName}</strong> has disabled AI chat permissions for your account. Please contact your organization lead.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
            <Bot size={18} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900">
              Clinical Assistant
            </h3>
            <p className="text-xs text-slate-500">Connected to {orgName}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Online</span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-5 bg-slate-50/40">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex gap-2.5 mb-3 items-center text-xs text-slate-500 pl-1">
            <div className="w-6 h-6 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
              <Bot size={13} />
            </div>
            <span>Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="px-4 py-2 border-t border-slate-100 bg-white flex gap-2 overflow-x-auto">
        {QUICK_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-1.5 rounded-full border border-slate-200/80 whitespace-nowrap transition-colors flex-shrink-0 font-medium"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-3.5 border-t border-slate-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 rounded-xl flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
};
