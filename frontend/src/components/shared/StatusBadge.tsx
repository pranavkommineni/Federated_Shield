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
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'done':
      case 'completed':
      case 'online':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'idle':
        return 'bg-slate-100 text-slate-600 border-slate-200';
      case 'offline':
      case 'aborted':
      case 'failed':
      case 'revoked':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide border ${getStyle()} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
};
