import React from 'react';
import { Bot, User as UserIcon } from 'lucide-react';
import { ChatMessage } from '../../types/training';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 flex-shrink-0 mt-0.5">
          <Bot size={16} />
        </div>
      )}

      <div className="max-w-[78%]">
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-xs shadow-sm font-normal'
              : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs shadow-sm'
          }`}
        >
          <div className="whitespace-pre-line">{message.content}</div>
        </div>

        <div
          className={`text-[10px] text-slate-400 mt-1 px-1 ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-600 flex-shrink-0 mt-0.5">
          <UserIcon size={16} />
        </div>
      )}
    </div>
  );
};
