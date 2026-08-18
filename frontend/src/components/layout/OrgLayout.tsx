import React from 'react';
import { Outlet, NavLink, useNavigate, useParams } from 'react-router-dom';
import {
  Building2,
  LayoutDashboard,
  Users,
  ShieldAlert,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';

export const OrgLayout: React.FC = () => {
  const { orgId } = useParams<{ orgId: string }>();
  const { currentUser, selectedOrgName, logout, loginAs } = useAuthStore();
  const navigate = useNavigate();
  const currentOrgId = orgId || '1';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-background text-slate-100">
      {/* Org Sidebar */}
      <aside className="w-64 bg-surface/90 border-r border-slate-800 flex flex-col justify-between backdrop-blur-xl fixed inset-y-0 z-30">
        <div>
          {/* Org Brand Logo */}
          <div className="p-6 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-slate-100 shadow-glow-purple">
                <Building2 size={22} />
              </div>
              <div className="overflow-hidden">
                <h1 className="text-sm font-extrabold text-slate-100 truncate">
                  {selectedOrgName || 'Hospital Alpha'}
                </h1>
                <span className="text-[10px] text-purple-400 font-bold uppercase tracking-wider bg-purple-500/10 px-1.5 py-0.5 rounded border border-purple-500/20">
                  Org Administrator
                </span>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            <NavLink
              to={`/org/${currentOrgId}`}
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-500/20 to-indigo-600/10 text-purple-300 border border-purple-500/30 shadow-glow-purple'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <LayoutDashboard size={18} />
              <span>Node Overview</span>
            </NavLink>

            <NavLink
              to={`/org/${currentOrgId}/users`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-500/20 to-indigo-600/10 text-purple-300 border border-purple-500/30 shadow-glow-purple'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <Users size={18} />
              <span>Manage Users & Chat</span>
            </NavLink>
          </nav>
        </div>

        {/* User Info & Switch Persona */}
        <div className="p-4 border-t border-slate-800/80 bg-surface-elevated/40">
          <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/60 mb-2">
            <div className="text-xs font-bold text-slate-200 truncate">{currentUser?.fullName}</div>
            <div className="text-[11px] text-purple-400 truncate">{currentUser?.department || 'Lead Administrator'}</div>
          </div>

          {/* Quick Role Switcher for Demo Testing */}
          <div className="grid grid-cols-2 gap-1.5 mb-2">
            <button
              onClick={() => {
                loginAs('admin');
                navigate('/admin');
              }}
              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 py-1.5 rounded-lg font-medium text-center border border-slate-700"
            >
              👑 Admin View
            </button>
            <button
              onClick={() => {
                loginAs('end_user');
                navigate('/chat');
              }}
              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 py-1.5 rounded-lg font-medium text-center border border-slate-700"
            >
              💬 User Chat
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
            <ShieldAlert size={16} className="text-purple-400" />
            <span className="text-xs font-mono text-slate-400">
              Data Silo Isolation: <strong className="text-emerald-400">Active (Zero Central Leak)</strong>
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-xs bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700 text-slate-300">
              Scoped to: <strong className="text-purple-400">{selectedOrgName || 'Hospital Alpha'}</strong>
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
