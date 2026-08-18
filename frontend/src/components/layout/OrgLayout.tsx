import React from 'react';
import { Outlet, NavLink, useNavigate, useParams } from 'react-router-dom';
import {
  Building2,
  LayoutDashboard,
  Users,
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
    <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Org Sidebar */}
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col justify-between fixed inset-y-0 z-30">
        <div>
          {/* Org Brand */}
          <div className="p-5 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600">
                <Building2 size={18} />
              </div>
              <div className="overflow-hidden">
                <h1 className="text-xs font-bold text-slate-900 truncate">
                  {selectedOrgName || 'AIIMS New Delhi'}
                </h1>
                <span className="text-[10px] text-violet-600 font-semibold">
                  Organization Portal
                </span>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <NavLink
              to={`/org/${currentOrgId}`}
              end
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-violet-50 text-violet-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <LayoutDashboard size={16} />
              <span>Node Overview</span>
            </NavLink>

            <NavLink
              to={`/org/${currentOrgId}/users`}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-violet-50 text-violet-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <Users size={16} />
              <span>User & Chat Access</span>
            </NavLink>
          </nav>
        </div>

        {/* User Info & Switch Persona */}
        <div className="p-3 border-t border-slate-200 bg-slate-50">
          <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-sm mb-3">
            <div className="text-xs font-semibold text-slate-900 truncate">{currentUser?.fullName}</div>
            <div className="text-[11px] text-violet-600 truncate">{currentUser?.department || 'Lead Administrator'}</div>
          </div>

          {/* Quick Persona Switch without emojis */}
          <div className="grid grid-cols-2 gap-1.5 mb-2">
            <button
              onClick={() => {
                loginAs('admin');
                navigate('/admin');
              }}
              className="text-[11px] bg-white hover:bg-slate-100 text-slate-700 py-1.5 rounded-md font-medium text-center border border-slate-200 shadow-sm"
            >
              Admin
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
              Silo Isolation: <strong className="text-emerald-700 font-semibold">Active (Zero Raw Data Leakage)</strong>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-xs bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200 text-slate-700 font-medium">
              Silo: <span className="text-violet-700 font-semibold">{selectedOrgName || 'AIIMS New Delhi'}</span>
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
