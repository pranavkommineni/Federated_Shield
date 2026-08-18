import React from 'react';
import { ShieldCheck, Bot, User as UserIcon } from 'lucide-react';
import { ChatMessage } from '../../types/training';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 flex-shrink-0 mt-1 shadow-glow">
          <Bot size={18} />
        </div>
      )}

      <div
        className={`max-w-[78%] rounded-2xl p-4 text-sm leading-relaxed ${
          isUser
            ? 'bg-gradient-to-r from-cyan-500 to-cyan-600 text-slate-950 font-medium rounded-tr-none shadow-md'
            : 'bg-surface-elevated/90 border border-slate-800 text-slate-200 rounded-tl-none backdrop-blur-md'
        }`}
      >
        <div className="whitespace-pre-line">{message.content}</div>

        {/* Cryptographic Privacy Guarantee Footer for AI responses */}
        {!isUser && message.privacyGuarantee && (
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <ShieldCheck size={13} />
              <span>Differential Privacy Guaranteed ({message.privacyGuarantee.epsilonBound})</span>
            </div>
            <div className="font-mono text-[10px] text-slate-500 flex justify-between">
              <span>{message.privacyGuarantee.modelCheckpoint}</span>
              <span>{message.privacyGuarantee.zkProofHash}</span>
            </div>
          </div>
        )}

        <div className={`text-[10px] mt-1.5 text-right ${isUser ? 'text-slate-900/70' : 'text-slate-500'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center text-slate-200 flex-shrink-0 mt-1">
          <UserIcon size={18} />
        </div>
      )}
    </div>
  );
};
