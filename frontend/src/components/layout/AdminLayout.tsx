import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  Shield,
  LayoutDashboard,
  Building2,
  LogOut,
  Radio,
  ExternalLink,
} from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';

export const AdminLayout: React.FC = () => {
  const { currentUser, logout, loginAs } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-background text-slate-100">
      {/* Admin Sidebar */}
      <aside className="w-64 bg-surface/90 border-r border-slate-800 flex flex-col justify-between backdrop-blur-xl fixed inset-y-0 z-30">
        <div>
          {/* Brand Logo */}
          <div className="p-6 border-b border-slate-800/80 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 shadow-glow">
              <Shield size={22} />
            </div>
            <div>
              <h1 className="text-base font-extrabold tracking-tight">
                FEDERATED<span className="text-cyan-400">SHIELD</span>
              </h1>
              <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20">
                Platform Admin
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            <NavLink
              to="/admin"
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-purple-600/10 text-cyan-400 border border-cyan-500/30 shadow-glow'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <LayoutDashboard size={18} />
              <span>Global Dashboard</span>
            </NavLink>

            <NavLink
              to="/admin/orgs/1"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-purple-600/10 text-cyan-400 border border-cyan-500/30 shadow-glow'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <Building2 size={18} />
              <span>Hospital Node Alpha</span>
            </NavLink>
          </nav>
        </div>

        {/* User Info & Switch Persona */}
        <div className="p-4 border-t border-slate-800/80 bg-surface-elevated/40">
          <div className="flex items-center justify-between mb-3 px-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs text-slate-400">FL Server Online</span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-[11px] text-cyan-400 hover:underline flex items-center gap-1"
            >
              Docs <ExternalLink size={10} />
            </a>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/60 mb-2">
            <div className="text-xs font-bold text-slate-200 truncate">{currentUser?.fullName}</div>
            <div className="text-[11px] text-slate-400 truncate">{currentUser?.email}</div>
          </div>

          {/* Quick Role Switcher for Demo Testing */}
          <div className="grid grid-cols-2 gap-1.5 mb-2">
            <button
              onClick={() => {
                loginAs('org_admin');
                navigate('/org/1');
              }}
              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 py-1.5 rounded-lg font-medium text-center border border-slate-700"
            >
              🏥 Org View
            </button>
            <button
              onClick={() => {
                loginAs('end_user');
                navigate('/chat');
              }}
              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 py-1.5 rounded-lg font-medium text-center border border-slate-700"
            >
              💬 Chat View
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors border border-rose-500/20"
          >
            <LogOut size={14} /> Switch Persona / Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 ml-64 min-h-screen flex flex-col">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 bg-surface/70 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <Radio size={16} className="text-cyan-400 animate-pulse" />
            <span className="text-xs font-mono text-slate-400">
              Live WebSocket Stream: <strong className="text-emerald-400">Connected</strong>
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-xs bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700 text-slate-300">
              Role: <strong className="text-cyan-400 uppercase">Platform Admin</strong>
            </div>
          </div>
        </header>

        {/* Page Views */}
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
