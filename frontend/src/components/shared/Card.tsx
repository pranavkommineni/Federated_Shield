import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  icon,
  action,
  children,
  className = '',
  noPadding = false,
}) => {
  return (
    <div className={`bg-card/90 backdrop-blur-md border border-slate-800 rounded-2xl shadow-xl overflow-hidden ${className}`}>
      {(title || action) && (
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {icon && <div className="text-cyan-400 text-lg">{icon}</div>}
            <div>
              {title && <h3 className="text-base font-bold text-slate-100">{title}</h3>}
              {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
            </div>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'p-6'}>{children}</div>
    </div>
  );
};
