import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Users,
  UserPlus,
  ArrowLeft,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { Card } from '../../components/shared/Card';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { fetchOrgUsers, inviteUser, toggleChatAccess } from '../../api/orgs';
import { User, InviteUserPayload } from '../../types/user';
import { useAuthStore } from '../../store/useAuthStore';

export const ManageUsers: React.FC = () => {
  const { orgId } = useParams<{ orgId: string }>();
  const navigate = useNavigate();
  const { selectedOrgId, selectedOrgName, toggleUserChatAccess } = useAuthStore();
  const currentId = Number(orgId) || selectedOrgId || 1;

  const [users, setUsers] = useState<User[]>([]);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [department, setDepartment] = useState('');
  const [grantChat, setGrantChat] = useState(true);

  const loadUsers = async () => {
    const data = await fetchOrgUsers(currentId);
    setUsers(data);
  };

  useEffect(() => {
    loadUsers();
  }, [currentId]);

  const handleToggleAccess = async (user: User) => {
    const newStatus = !user.hasChatAccess;
    await toggleChatAccess(currentId, user.id, newStatus);
    toggleUserChatAccess(user.id, newStatus);

    setUsers((prev) =>
      prev.map((u) => (u.id === user.id ? { ...u, hasChatAccess: newStatus } : u))
    );
  };

  const handleInviteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !username.trim() || !email.trim()) return;

    const payload: InviteUserPayload = {
      username: username.trim(),
      fullName: fullName.trim(),
      email: email.trim(),
      role: 'end_user',
      orgId: currentId,
      department: department.trim() || 'Clinical Practitioner',
      hasChatAccess: grantChat,
    };

    const created = await inviteUser(payload);
    setUsers((prev) => [...prev, created]);

    setFullName('');
    setUsername('');
    setEmail('');
    setDepartment('');
    setShowInviteModal(false);
  };

  return (
    <div className="space-y-8">
      {/* Back Button & Header */}
      <div>
        <button
          onClick={() => navigate(`/org/${currentId}`)}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-purple-400 mb-4 transition-colors"
        >
          <ArrowLeft size={16} /> Back to Node Overview
        </button>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-card/80 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/30 flex items-center justify-center">
              <Users size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">Manage End-Users & AI Chat Access</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Authorized practitioners under <strong>{selectedOrgName || 'Hospital Alpha'}</strong>
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowInviteModal(true)}
            className="btn-primary bg-purple-600 hover:bg-purple-500 text-slate-100 px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 shadow-glow-purple transition-all"
          >
            <UserPlus size={16} /> Invite / Add User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <Card
        title={`Registered Clinicians & Staff (${users.length})`}
        subtitle="Toggle AI chat permissions per user to control model usage"
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 uppercase font-mono">
              <tr>
                <th className="p-4">Full Name</th>
                <th className="p-4">Username</th>
                <th className="p-4">Email</th>
                <th className="p-4">Department</th>
                <th className="p-4">Role</th>
                <th className="p-4 text-center">AI Chat Access Status</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/30">
                  <td className="p-4 font-bold text-slate-100">{u.fullName}</td>
                  <td className="p-4 font-mono text-slate-400">{u.username}</td>
                  <td className="p-4 text-slate-400">{u.email}</td>
                  <td className="p-4">{u.department || 'General'}</td>
                  <td className="p-4">
                    <StatusBadge status={u.role} />
                  </td>
                  <td className="p-4 text-center">
                    {u.hasChatAccess ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 size={14} /> Enabled
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <XCircle size={14} /> Revoked
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => handleToggleAccess(u)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                        u.hasChatAccess
                          ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {u.hasChatAccess ? 'Revoke Access' : 'Grant Access'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Modal: Invite User */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100 mb-1">Add Healthcare Clinician</h3>
            <p className="text-xs text-slate-400 mb-4">
              Register an end-user under {selectedOrgName || 'Hospital Alpha'}.
            </p>

            <form onSubmit={handleInviteSubmit} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-semibold block mb-1">Full Name *</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Dr. Emily Watson"
                  required
                  className="w-full bg-surface-elevated border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-purple-400"
                />
              </div>

              <div>
                <label className="text-slate-300 font-semibold block mb-1">Username *</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. emily_w"
                  required
                  className="w-full bg-surface-elevated border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-purple-400"
                />
              </div>

              <div>
                <label className="text-slate-300 font-semibold block mb-1">Email Address *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. emily.watson@hospital.org"
                  required
                  className="w-full bg-surface-elevated border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-purple-400"
                />
              </div>

              <div>
                <label className="text-slate-300 font-semibold block mb-1">Department / Clinical Role</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. Pediatric Cardiology"
                  className="w-full bg-surface-elevated border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-purple-400"
                />
              </div>

              <div className="pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={grantChat}
                    onChange={(e) => setGrantChat(e.target.checked)}
                    className="rounded accent-purple-500"
                  />
                  <span className="text-slate-200">Grant AI Model Chat Access Immediately</span>
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-4 py-2 rounded-xl font-semibold text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary bg-purple-600 hover:bg-purple-500 text-slate-100 px-5 py-2 rounded-xl font-bold shadow-glow-purple"
                >
                  Add User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
