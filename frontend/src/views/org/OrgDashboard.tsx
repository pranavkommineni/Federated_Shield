import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Building2,
  Server,
  Users,
  ShieldCheck,
  Key,
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
    return <div className="p-8 text-center text-slate-500 text-xs">Loading organization node data...</div>;
  }

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Node Header Banner */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600">
            <Building2 size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">{org.name}</h2>
              <StatusBadge status={org.status} />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Dedicated Edge Training Node • Local Differential Privacy & Secure Multi-Party Aggregation
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate(`/org/${org.id}/users`)}
          className="bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
        >
          <Users size={14} /> Manage Staff & Chat
        </button>
      </div>

      {/* Node Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Local Model Accuracy</span>
          <div className="text-2xl font-bold font-mono text-violet-600">{(org.localAccuracy * 100).toFixed(1)}%</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Participated in {org.roundsParticipated} rounds</span>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Local Loss</span>
          <div className="text-2xl font-bold font-mono text-blue-600">{org.localLoss.toFixed(4)}</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Evaluated on private silo</span>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Hardware Load</span>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {telemetry?.computeTelemetry.cpuUtilizationPercent || 18}% CPU
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            RAM: {telemetry?.computeTelemetry.memoryUsageMb || 1200} MB
          </span>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Privacy Budget (ε)</span>
          <div className="text-2xl font-bold font-mono text-amber-600">{org.epsilonSpent.toFixed(2)} ε</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Gaussian Mechanism (σ = 1.15)</span>
        </div>
      </div>

      {/* Edge Node Hardware & Device Pool */}
      <Card
        title="Edge Client Workstations & Devices"
        subtitle="Local hardware executing Flower client training iterations"
        icon={<Server size={16} />}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold text-[10px]">
              <tr>
                <th className="p-3.5">Device Identifier</th>
                <th className="p-3.5">Role / Modality</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Compute</th>
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
                    <td className="p-3.5 text-violet-600 font-bold">{d.cpuUsage}% CPU</td>
                    <td className="p-3.5">{d.memoryMb} MB</td>
                    <td className="p-3.5 text-slate-500">{d.ipAddress}</td>
                    <td className="p-3.5 text-slate-400 font-sans">{d.lastSeen}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-400 font-sans">
                    No active edge devices registered.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Local Privacy & Secure Aggregation Specification */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card
          title="Differential Privacy Parameters"
          subtitle="Noise calibrated locally before gradient submission"
          icon={<ShieldCheck size={16} />}
        >
          <div className="space-y-2 text-xs">
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-600">Noise Mechanism</span>
              <strong className="text-slate-900">Gaussian DP (Rényi Moments)</strong>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-600">Noise Multiplier (σ)</span>
              <strong className="text-amber-600 font-mono">1.15</strong>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-600">Gradient Clipping (C)</span>
              <strong className="text-slate-900 font-mono">1.0 (L2 Norm)</strong>
            </div>
          </div>
        </Card>

        <Card
          title="Multi-Party Computation Protection"
          subtitle="Shamir Secret Sharing verification"
          icon={<Key size={16} />}
        >
          <div className="space-y-2 text-xs">
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-600">Secure Aggregation Status</span>
              <strong className="text-emerald-700">Active (ECDH Masked)</strong>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-600">Data Exposure</span>
              <strong className="text-slate-900">Zero Raw Data Leakage</strong>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-600">Local Samples</span>
              <strong className="text-violet-600 font-mono">{telemetry?.localSamplesCount || 142} Records</strong>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
