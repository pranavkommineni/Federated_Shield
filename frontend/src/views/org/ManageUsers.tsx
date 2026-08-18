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
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate(`/org/${currentId}`)}
          className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 mb-3 transition-colors font-medium"
        >
          <ArrowLeft size={14} /> Back to Overview
        </button>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white border border-slate-200/90 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600">
              <Users size={20} />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Staff Management & AI Permissions</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Authorized practitioners under <strong>{selectedOrgName || 'AIIMS New Delhi (Cardiology)'}</strong>
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowInviteModal(true)}
            className="bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <UserPlus size={14} /> Add User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <Card
        title={`Registered Clinicians (${users.length})`}
        subtitle="Toggle AI chat permissions per user to control model usage"
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold text-[10px]">
              <tr>
                <th className="p-3.5">Full Name</th>
                <th className="p-3.5">Username</th>
                <th className="p-3.5">Email</th>
                <th className="p-3.5">Department</th>
                <th className="p-3.5">Role</th>
                <th className="p-3.5 text-center">Chat Permission</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/60">
                  <td className="p-3.5 font-bold text-slate-900">{u.fullName}</td>
                  <td className="p-3.5 font-mono text-slate-500">{u.username}</td>
                  <td className="p-3.5 text-slate-500">{u.email}</td>
                  <td className="p-3.5 text-slate-600">{u.department || 'General'}</td>
                  <td className="p-3.5">
                    <StatusBadge status={u.role} />
                  </td>
                  <td className="p-3.5 text-center">
                    {u.hasChatAccess ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 size={12} /> Enabled
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        <XCircle size={12} /> Revoked
                      </span>
                    )}
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => handleToggleAccess(u)}
                      className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-colors shadow-sm ${
                        u.hasChatAccess
                          ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200'
                          : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200'
                      }`}
                    >
                      {u.hasChatAccess ? 'Revoke' : 'Grant'}
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
        <div className="fixed inset-0 z-50 bg-slate-900/30 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-xl max-w-md w-full p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Add Healthcare Clinician</h3>
            <p className="text-xs text-slate-500 mb-4">
              Register an end-user under {selectedOrgName || 'AIIMS New Delhi (Cardiology)'}.
            </p>

            <form onSubmit={handleInviteSubmit} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Dr. Kavita Krishnan"
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-violet-500 focus:bg-white"
                />
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. dr_kavita"
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-violet-500 focus:bg-white"
                />
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. kavita.krishnan@aiims.edu.in"
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-violet-500 focus:bg-white"
                />
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">Department</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. Pediatric Cardiology"
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-violet-500 focus:bg-white"
                />
              </div>

              <div className="pt-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={grantChat}
                    onChange={(e) => setGrantChat(e.target.checked)}
                    className="rounded accent-violet-600"
                  />
                  <span className="text-slate-700 font-medium">Enable AI Model Chat Access Immediately</span>
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-sm"
                >
                  Save User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
