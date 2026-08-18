import React from 'react';
import { OrgStatus } from '../../types/org';

interface StatusBadgeProps {
  status: OrgStatus | string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const normalized = status.toLowerCase();

  const getStyle = () => {
    switch (normalized) {
      case 'training':
      case 'running':
        return 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30 animate-pulse';
      case 'done':
      case 'completed':
      case 'online':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'idle':
        return 'bg-slate-500/15 text-slate-300 border-slate-500/30';
      case 'offline':
      case 'aborted':
      case 'failed':
      case 'revoked':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-700/30 text-slate-300 border-slate-600/30';
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${getStyle()} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
};
