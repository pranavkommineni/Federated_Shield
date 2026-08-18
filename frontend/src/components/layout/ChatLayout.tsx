import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Bot, LogOut, ShieldCheck } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';

export const ChatLayout: React.FC = () => {
  const { currentUser, logout, loginAs } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col">
      {/* Top Header */}
      <header className="h-16 border-b border-slate-800 bg-surface/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-30 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 shadow-glow">
            <Bot size={20} />
          </div>
          <div>
            <h1 className="text-sm font-extrabold text-slate-100 flex items-center gap-2">
              FEDERATED<span className="text-cyan-400">SHIELD</span>
              <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
                End-User AI Portal
              </span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700">
            <ShieldCheck size={14} className="text-emerald-400" />
            <span className="text-slate-300">
              Org: <strong className="text-slate-100">{currentUser?.orgName || 'Hospital Alpha'}</strong>
            </span>
          </div>

          <div className="text-xs text-slate-400 hidden sm:block">
            Logged in as: <strong className="text-slate-200">{currentUser?.fullName}</strong>
          </div>

          {/* Quick Switch for Judges/Demo */}
          <div className="flex gap-1.5">
            <button
              onClick={() => {
                loginAs('admin');
                navigate('/admin');
              }}
              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2.5 py-1.5 rounded-lg border border-slate-700 font-medium"
            >
              👑 Admin
            </button>
            <button
              onClick={() => {
                loginAs('org_admin');
                navigate('/org/1');
              }}
              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-purple-400 px-2.5 py-1.5 rounded-lg border border-slate-700 font-medium"
            >
              🏥 Org Admin
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-xs text-rose-400 hover:bg-rose-500/10 px-3 py-1.5 rounded-lg border border-rose-500/20 transition-colors"
          >
            <LogOut size={14} /> <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 flex flex-col justify-center">
        <Outlet />
      </main>
    </div>
  );
};
