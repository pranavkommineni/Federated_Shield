import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
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
      <div className="p-8 text-center text-slate-500 text-xs">Loading organization telemetry...</div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Top Header */}
      <div>
        <button
          onClick={() => navigate('/admin')}
          className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 mb-3 transition-colors font-medium"
        >
          <ArrowLeft size={14} /> Back to Dashboard
        </button>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white border border-slate-200/90 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600">
              <Building2 size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900">{org.name}</h2>
                <StatusBadge status={org.status} />
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{org.description}</p>
            </div>
          </div>

          <div className="text-xs text-slate-400 font-mono">
            Node ID: #{org.id}
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Local Accuracy</span>
          <div className="text-2xl font-bold font-mono text-blue-600">{(org.localAccuracy * 100).toFixed(1)}%</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Rounds: {org.roundsParticipated}</span>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Edge Compute</span>
          <div className="text-2xl font-bold font-mono text-violet-600">
            {telemetry?.computeTelemetry.cpuUtilizationPercent || 18}% CPU
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Memory: {telemetry?.computeTelemetry.memoryUsageMb || 1200} MB
          </span>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Differential Privacy</span>
          <div className="text-2xl font-bold font-mono text-amber-600">σ = {telemetry?.edgePrivacyConfiguration.noiseMultiplierSigma || 1.15}</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Clip Norm: C = 1.0</span>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Private Records</span>
          <div className="text-2xl font-bold font-mono text-emerald-600">{telemetry?.localSamplesCount || 142}</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Zero Central Storage</span>
        </div>
      </div>

      {/* Connected Devices Table */}
      <Card
        title="Edge Client Workstations"
        subtitle="Active local hardware contributing to federated gradient computations"
        icon={<Server size={16} />}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold text-[10px]">
              <tr>
                <th className="p-3.5">Device Name</th>
                <th className="p-3.5">Type</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">CPU Usage</th>
                <th className="p-3.5">Memory</th>
                <th className="p-3.5">IP Address</th>
                <th className="p-3.5">Last Seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-slate-700">
              {org.devices && org.devices.length > 0 ? (
                org.devices.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/60">
                    <td className="p-3.5 font-bold text-slate-900">{d.name}</td>
                    <td className="p-3.5 text-slate-500 font-sans">{d.type}</td>
                    <td className="p-3.5"><StatusBadge status={d.status} /></td>
                    <td className="p-3.5 text-blue-600 font-bold">{d.cpuUsage}%</td>
                    <td className="p-3.5">{d.memoryMb} MB</td>
                    <td className="p-3.5 text-slate-500">{d.ipAddress}</td>
                    <td className="p-3.5 text-slate-400 font-sans">{d.lastSeen}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-400 font-sans">
                    No edge devices reported.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Users Assigned */}
      <Card
        title="Assigned Clinical Personnel"
        subtitle="Doctors and researchers registered under this hospital silo"
        icon={<Users size={16} />}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold text-[10px]">
              <tr>
                <th className="p-3.5">Full Name</th>
                <th className="p-3.5">Username</th>
                <th className="p-3.5">Role</th>
                <th className="p-3.5">Department</th>
                <th className="p-3.5">AI Chat Access</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/60">
                  <td className="p-3.5 font-bold text-slate-900">{u.fullName}</td>
                  <td className="p-3.5 font-mono text-slate-500">{u.username}</td>
                  <td className="p-3.5"><StatusBadge status={u.role} /></td>
                  <td className="p-3.5 text-slate-500">{u.department || 'Clinical'}</td>
                  <td className="p-3.5">
                    {u.hasChatAccess ? (
                      <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">Granted</span>
                    ) : (
                      <span className="text-rose-700 font-semibold bg-rose-50 px-2 py-0.5 rounded border border-rose-200">Revoked</span>
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
