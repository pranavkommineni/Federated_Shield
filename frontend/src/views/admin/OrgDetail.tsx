import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  ShieldCheck,
  Server,
  Users,
} from 'lucide-react';
import { Card } from '../../components/shared/Card';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { fetchOrganizations, fetchOrgTelemetry, fetchOrgUsers } from '../../api/orgs';
import { Organization, OrgTelemetry } from '../../types/org';
import { User } from '../../types/user';

export const OrgDetail: React.FC = () => {
  const { orgId } = useParams<{ orgId: string }>();
  const navigate = useNavigate();
  const idNum = Number(orgId) || 1;

  const [org, setOrg] = useState<Organization | null>(null);
  const [telemetry, setTelemetry] = useState<OrgTelemetry | null>(null);
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const load = async () => {
      const orgs = await fetchOrganizations();
      const target = orgs.find((o) => o.id === idNum) || orgs[0];
      setOrg(target);

      const telem = await fetchOrgTelemetry(idNum);
      setTelemetry(telem);

      const orgUsers = await fetchOrgUsers(idNum);
      setUsers(orgUsers);
    };
    load();
  }, [idNum]);

  if (!org) {
    return (
      <div className="p-8 text-center text-slate-400">Loading organization telemetry...</div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb & Header */}
      <div>
        <button
          onClick={() => navigate('/admin')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-cyan-400 mb-4 transition-colors"
        >
          <ArrowLeft size={16} /> Back to Global Dashboard
        </button>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-card/80 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 shadow-glow">
              <Building2 size={28} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-slate-100">{org.name}</h2>
                <StatusBadge status={org.status} />
              </div>
              <p className="text-xs text-slate-400 mt-1">{org.description}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">Node ID: #{org.id}</span>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <Card>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Local Accuracy</span>
          <div className="text-2xl font-black font-mono text-cyan-400">{(org.localAccuracy * 100).toFixed(1)}%</div>
          <span className="text-xs text-slate-400 mt-1 block">Rounds Participated: {org.roundsParticipated}</span>
        </Card>

        <Card>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Edge Compute</span>
          <div className="text-2xl font-black font-mono text-purple-400">
            {telemetry?.computeTelemetry.cpuUtilizationPercent || 18}% CPU
          </div>
          <span className="text-xs text-slate-400 mt-1 block">
            Memory: {telemetry?.computeTelemetry.memoryUsageMb || 1200} MB
          </span>
        </Card>

        <Card>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Differential Privacy</span>
          <div className="text-2xl font-black font-mono text-amber-400">σ = {telemetry?.edgePrivacyConfiguration.noiseMultiplierSigma || 1.15}</div>
          <span className="text-xs text-slate-400 mt-1 block">Clipping Norm: C = 1.0</span>
        </Card>

        <Card>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Private Records</span>
          <div className="text-2xl font-black font-mono text-emerald-400">{telemetry?.localSamplesCount || 142}</div>
          <span className="text-xs text-slate-400 mt-1 block">Zero Central Storage</span>
        </Card>
      </div>

      {/* Connected Devices Table */}
      <Card
        title="Connected Client Devices & Workstations"
        subtitle="Active edge machines contributing local model gradient computations"
        icon={<Server size={20} />}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 uppercase font-mono">
              <tr>
                <th className="p-4">Device Name</th>
                <th className="p-4">Type</th>
                <th className="p-4">Status</th>
                <th className="p-4">CPU Usage</th>
                <th className="p-4">Memory</th>
                <th className="p-4">IP Address</th>
                <th className="p-4">Last Ping</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {org.devices && org.devices.length > 0 ? (
                org.devices.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-800/30">
                    <td className="p-4 font-bold text-slate-100">{d.name}</td>
                    <td className="p-4 text-slate-400">{d.type}</td>
                    <td className="p-4"><StatusBadge status={d.status} /></td>
                    <td className="p-4 text-cyan-400">{d.cpuUsage}%</td>
                    <td className="p-4">{d.memoryMb} MB</td>
                    <td className="p-4 text-slate-400">{d.ipAddress}</td>
                    <td className="p-4 text-slate-500">{d.lastSeen}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No individual edge devices reported.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Users Assigned */}
      <Card
        title="Assigned Organization Personnel"
        subtitle="Doctors and researchers registered under this hospital silo"
        icon={<Users size={20} />}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 uppercase">
              <tr>
                <th className="p-4">Full Name</th>
                <th className="p-4">Username</th>
                <th className="p-4">Role</th>
                <th className="p-4">Department</th>
                <th className="p-4">AI Chat Access</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/30">
                  <td className="p-4 font-bold text-slate-100">{u.fullName}</td>
                  <td className="p-4 font-mono text-slate-400">{u.username}</td>
                  <td className="p-4"><StatusBadge status={u.role} /></td>
                  <td className="p-4">{u.department || 'Clinical'}</td>
                  <td className="p-4">
                    {u.hasChatAccess ? (
                      <span className="text-emerald-400 font-semibold">✓ Granted</span>
                    ) : (
                      <span className="text-rose-400 font-semibold">✗ Revoked</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
