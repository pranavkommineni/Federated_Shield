import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  Shield,
  LayoutDashboard,
  Building2,
  LogOut,
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
    <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Admin Sidebar */}
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col justify-between fixed inset-y-0 z-30">
        <div>
          {/* Brand */}
          <div className="p-5 border-b border-slate-100 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <Shield size={18} />
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-900 tracking-tight">
                Federated Shield
              </h1>
              <span className="text-[10px] text-blue-600 font-semibold">
                Admin Console
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <NavLink
              to="/admin"
              end
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <LayoutDashboard size={16} />
              <span>Global Training</span>
            </NavLink>

            <NavLink
              to="/admin/orgs/1"
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <Building2 size={16} />
              <span>AIIMS New Delhi Node</span>
            </NavLink>
          </nav>
        </div>

        {/* User Info & Switch Persona */}
        <div className="p-3 border-t border-slate-200 bg-slate-50">
          <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-sm mb-3">
            <div className="text-xs font-semibold text-slate-900 truncate">{currentUser?.fullName}</div>
            <div className="text-[11px] text-slate-500 truncate">{currentUser?.email}</div>
          </div>

          {/* Quick Persona Switch without emojis */}
          <div className="grid grid-cols-2 gap-1.5 mb-2">
            <button
              onClick={() => {
                loginAs('org_admin');
                navigate('/org/1');
              }}
              className="text-[11px] bg-white hover:bg-slate-100 text-slate-700 py-1.5 rounded-md font-medium text-center border border-slate-200 shadow-sm"
            >
              Org Portal
            </button>
            <button
              onClick={() => {
                loginAs('end_user');
                navigate('/chat');
              }}
              className="text-[11px] bg-white hover:bg-slate-100 text-slate-700 py-1.5 rounded-md font-medium text-center border border-slate-200 shadow-sm"
            >
              AI Chat
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-1.5 py-1.5 text-xs text-rose-600 hover:bg-rose-50 rounded-md transition-colors font-medium"
          >
            <LogOut size={13} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 ml-60 min-h-screen flex flex-col bg-slate-50">
        {/* Header */}
        <header className="h-14 border-b border-slate-200 bg-white/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-xs text-slate-600">
              Coordinator Server: <strong className="text-emerald-700 font-semibold">Online</strong>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1"
            >
              API Docs <ExternalLink size={12} />
            </a>
            <div className="text-xs bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200 text-slate-700 font-medium">
              Role: <span className="text-blue-600 font-semibold">Platform Owner</span>
            </div>
          </div>
        </header>

        {/* Page Views */}
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
