import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Building2,
  Server,
  Users,
  ShieldCheck,
  Key,
  Flame,
} from 'lucide-react';
import { Card } from '../../components/shared/Card';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { fetchOrganizations, fetchOrgTelemetry } from '../../api/orgs';
import { Organization, OrgTelemetry } from '../../types/org';
import { useAuthStore } from '../../store/useAuthStore';

export const OrgDashboard: React.FC = () => {
  const { orgId } = useParams<{ orgId: string }>();
  const navigate = useNavigate();
  const { selectedOrgId } = useAuthStore();
  const currentId = Number(orgId) || selectedOrgId || 1;

  const [org, setOrg] = useState<Organization | null>(null);
  const [telemetry, setTelemetry] = useState<OrgTelemetry | null>(null);

  useEffect(() => {
    const load = async () => {
      const allOrgs = await fetchOrganizations();
      const target = allOrgs.find((o) => o.id === currentId) || allOrgs[0];
      setOrg(target);

      const telem = await fetchOrgTelemetry(currentId);
      setTelemetry(telem);
    };
    load();
  }, [currentId]);

  if (!org) {
    return <div className="p-8 text-center text-slate-400">Loading organization node data...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Node Header Banner */}
      <div className="bg-gradient-to-r from-surface to-surface-elevated border border-purple-900/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-slate-100 shadow-glow-purple">
              <Building2 size={28} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-2xl font-black text-slate-100">{org.name}</h2>
                <StatusBadge status={org.status} />
              </div>
              <p className="text-xs text-slate-400 mt-1 max-w-xl">
                Dedicated Edge Training Node • Client Silo with Local Differential Privacy and Secure Aggregation
              </p>
            </div>
          </div>

          <button
            onClick={() => navigate(`/org/${org.id}/users`)}
            className="btn-primary bg-purple-600 hover:bg-purple-500 text-slate-100 px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 shadow-glow-purple transition-all"
          >
            <Users size={16} /> Manage End-Users & Chat Access
          </button>
        </div>
      </div>

      {/* Node Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <Card className="hover:border-purple-500/40 transition-colors">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Local Model Accuracy</span>
          <div className="text-3xl font-black font-mono text-purple-400">{(org.localAccuracy * 100).toFixed(1)}%</div>
          <span className="text-xs text-slate-400 mt-2 block">Participated in {org.roundsParticipated} global rounds</span>
        </Card>

        <Card className="hover:border-purple-500/40 transition-colors">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Local Model Loss</span>
          <div className="text-3xl font-black font-mono text-cyan-400">{org.localLoss.toFixed(4)}</div>
          <span className="text-xs text-slate-400 mt-2 block">Evaluated on private validation silo</span>
        </Card>

        <Card className="hover:border-purple-500/40 transition-colors">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Edge Hardware Load</span>
          <div className="text-3xl font-black font-mono text-slate-100">
            {telemetry?.computeTelemetry.cpuUtilizationPercent || 18}% CPU
          </div>
          <span className="text-xs text-slate-400 mt-2 block">
            Memory: {telemetry?.computeTelemetry.memoryUsageMb || 1200} MB
          </span>
        </Card>

        <Card className="hover:border-purple-500/40 transition-colors">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Privacy Budget Used</span>
          <div className="text-3xl font-black font-mono text-amber-400">{org.epsilonSpent.toFixed(2)} ε</div>
          <span className="text-xs text-slate-400 mt-2 block">Gaussian Mechanism (σ = 1.15)</span>
        </Card>
      </div>

      {/* Edge Node Hardware & Device Pool */}
      <Card
        title="Edge Client Workstations & Devices"
        subtitle="Machines in this hospital node executing local Flower client iterations"
        icon={<Server size={20} />}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 uppercase font-mono">
              <tr>
                <th className="p-4">Device Identifier</th>
                <th className="p-4">Role / Modality</th>
                <th className="p-4">Status</th>
                <th className="p-4">Compute Utilization</th>
                <th className="p-4">Memory</th>
                <th className="p-4">Internal IP</th>
                <th className="p-4">Heartbeat</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {org.devices && org.devices.length > 0 ? (
                org.devices.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-800/30">
                    <td className="p-4 font-bold text-slate-100">{d.name}</td>
                    <td className="p-4 text-slate-400">{d.type}</td>
                    <td className="p-4"><StatusBadge status={d.status} /></td>
                    <td className="p-4 text-purple-400">{d.cpuUsage}% CPU</td>
                    <td className="p-4">{d.memoryMb} MB</td>
                    <td className="p-4 text-slate-400">{d.ipAddress}</td>
                    <td className="p-4 text-slate-500">{d.lastSeen}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No active edge devices registered.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Local Privacy & Secure Aggregation Specification */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card
          title="Local Differential Privacy Parameters"
          subtitle="Noise calibrated locally before gradient submission"
          icon={<ShieldCheck size={20} />}
        >
          <div className="space-y-3 text-xs">
            <div className="flex justify-between p-3 bg-surface-elevated/60 rounded-xl border border-slate-800">
              <span className="text-slate-400">DP Noise Mechanism</span>
              <strong className="text-slate-200">Gaussian DP (Rényi Moments)</strong>
            </div>
            <div className="flex justify-between p-3 bg-surface-elevated/60 rounded-xl border border-slate-800">
              <span className="text-slate-400">Noise Multiplier (σ)</span>
              <strong className="text-amber-400 font-mono">1.15</strong>
            </div>
            <div className="flex justify-between p-3 bg-surface-elevated/60 rounded-xl border border-slate-800">
              <span className="text-slate-400">Gradient Clipping Bound (C)</span>
              <strong className="text-slate-200 font-mono">1.0 (L2 Norm)</strong>
            </div>
          </div>
        </Card>

        <Card
          title="Cryptographic Multi-Party Protection"
          subtitle="Shamir Secret Sharing verification"
          icon={<Key size={20} />}
        >
          <div className="space-y-3 text-xs">
            <div className="flex justify-between p-3 bg-surface-elevated/60 rounded-xl border border-slate-800">
              <span className="text-slate-400">Secure Aggregation Status</span>
              <strong className="text-emerald-400">Active (ECDH Masked)</strong>
            </div>
            <div className="flex justify-between p-3 bg-surface-elevated/60 rounded-xl border border-slate-800">
              <span className="text-slate-400">Local Silo Privacy</span>
              <strong className="text-slate-200">Zero Raw Data Leakage</strong>
            </div>
            <div className="flex justify-between p-3 bg-surface-elevated/60 rounded-xl border border-slate-800">
              <span className="text-slate-400">Local Samples In Silo</span>
              <strong className="text-purple-400 font-mono">{telemetry?.localSamplesCount || 142} Records</strong>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
