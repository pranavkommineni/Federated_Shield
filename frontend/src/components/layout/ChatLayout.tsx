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
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Header */}
      <header className="h-14 border-b border-slate-200 bg-white/90 px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
            <Bot size={18} />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              Federated Shield
              <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Clinical AI Assistant
              </span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 text-xs bg-slate-100 px-3 py-1 rounded-full border border-slate-200 text-slate-700">
            <ShieldCheck size={13} className="text-emerald-600" />
            <span>Org: <strong className="text-slate-900 font-semibold">{currentUser?.orgName || 'AIIMS New Delhi'}</strong></span>
          </div>

          <div className="text-xs text-slate-600 hidden md:block">
            {currentUser?.fullName}
          </div>

          {/* Quick Demo Switcher without emojis */}
          <div className="flex gap-1.5">
            <button
              onClick={() => {
                loginAs('admin');
                navigate('/admin');
              }}
              className="text-[11px] bg-white hover:bg-slate-100 text-blue-700 px-2.5 py-1 rounded-md border border-slate-200 shadow-sm font-medium"
            >
              Admin
            </button>
            <button
              onClick={() => {
                loginAs('org_admin');
                navigate('/org/1');
              }}
              className="text-[11px] bg-white hover:bg-slate-100 text-violet-700 px-2.5 py-1 rounded-md border border-slate-200 shadow-sm font-medium"
            >
              Org Portal
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1 text-xs text-rose-600 hover:bg-rose-50 px-2.5 py-1 rounded-md transition-colors font-medium"
          >
            <LogOut size={13} /> <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-6 flex flex-col justify-center">
        <Outlet />
      </main>
    </div>
  );
};
