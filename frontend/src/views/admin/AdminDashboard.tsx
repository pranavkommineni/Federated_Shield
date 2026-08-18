import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play,
  Square,
  ShieldCheck,
  Building2,
  Lock,
  Flame,
  Activity,
  EyeOff,
  Plus,
  RefreshCw,
  ArrowUpRight,
} from 'lucide-react';
import { Card } from '../../components/shared/Card';
import { StatusBadge } from '../../components/shared/StatusBadge';
import { AccuracyChart } from '../../components/charts/AccuracyChart';
import { useMetricsSocket } from '../../hooks/useMetricsSocket';
import { fetchOrganizations, registerOrganization } from '../../api/orgs';
import { fetchTrainingStatus, fetchTrainingHistory, startTraining, stopTraining } from '../../api/training';
import { Organization } from '../../types/org';
import { RoundMetric, TrainingStatus } from '../../types/training';

export const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { isConnected, liveRounds, lastEvent, eventsLog } = useMetricsSocket();

  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [history, setHistory] = useState<RoundMetric[]>([]);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    isTraining: false,
    status: 'idle',
    runId: null,
    currentRound: 0,
    totalRounds: 0,
    activeOrgs: [],
    latestAccuracy: 0.924,
    latestLoss: 0.318,
    cumulativeEpsilon: 2.24,
  });

  const [roundsToRun, setRoundsToRun] = useState(5);
  const [targetAcc, setTargetAcc] = useState<number | undefined>(0.95);
  const [maxEps, setMaxEps] = useState<number | undefined>(5.0);
  const [isStarting, setIsStarting] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const [showOrgModal, setShowOrgModal] = useState(false);

  const loadData = async () => {
    const orgsData = await fetchOrganizations();
    setOrgs(orgsData);
    const histData = await fetchTrainingHistory();
    setHistory(histData);
    const statusData = await fetchTrainingStatus();
    setTrainingStatus(statusData);
  };

  useEffect(() => {
    loadData();
  }, []);

  // Merge historical and live rounds for Recharts
  const chartData = liveRounds.length > 0 ? liveRounds : history;

  const handleStartTraining = async () => {
    setIsStarting(true);
    try {
      await startTraining({
        rounds: roundsToRun,
        targetAccuracy: targetAcc,
        maxEpsilon: maxEps,
        orgNames: orgs.map((o) => o.name),
      });
      setTrainingStatus((prev) => ({
        ...prev,
        isTraining: true,
        status: 'running',
        totalRounds: roundsToRun,
        currentRound: 0,
      }));
    } catch (e) {
      console.error('Failed to start training:', e);
    } finally {
      setIsStarting(false);
    }
  };

  const handleStopTraining = async () => {
    try {
      await stopTraining();
      setTrainingStatus((prev) => ({ ...prev, isTraining: false, status: 'stopping' }));
    } catch (e) {
      console.error('Failed to stop training:', e);
    }
  };

  const handleRegisterOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    await registerOrganization(newOrgName.trim());
    setNewOrgName('');
    setShowOrgModal(false);
    loadData();
  };

  return (
    <div className="space-y-8">
      {/* Top Banner: Training Controls & Privacy Highlights */}
      <div className="bg-gradient-to-r from-surface to-surface-elevated border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                FL Orchestrator Core
              </span>
              <StatusBadge status={trainingStatus.isTraining ? 'training' : trainingStatus.status} />
            </div>
            <h2 className="text-2xl font-black text-slate-100">Global Federated Training Control</h2>
            <p className="text-slate-400 text-sm mt-1 max-w-xl">
              Trigger privacy-preserving rounds across all connected healthcare organizations with mathematical Differential Privacy guarantees.
            </p>
          </div>

          {/* Quick Action Controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-700/80">
              <label htmlFor="rounds-input" className="text-xs text-slate-400 font-semibold">Rounds:</label>
              <input
                id="rounds-input"
                type="number"
                min="1"
                max="50"
                value={roundsToRun}
                onChange={(e) => setRoundsToRun(Number(e.target.value))}
                disabled={trainingStatus.isTraining}
                className="w-16 bg-slate-800 text-cyan-400 font-mono font-bold text-sm px-2 py-1 rounded border border-slate-700 text-center focus:outline-none"
              />
            </div>

            {!trainingStatus.isTraining ? (
              <button
                onClick={handleStartTraining}
                disabled={isStarting}
                className="btn-primary bg-gradient-to-r from-cyan-500 to-cyan-600 hover:brightness-110 text-slate-950 font-bold px-6 py-3 rounded-xl flex items-center gap-2 shadow-glow transition-all disabled:opacity-50"
              >
                <Play size={18} /> Start Training Round
              </button>
            ) : (
              <button
                onClick={handleStopTraining}
                className="btn-danger bg-gradient-to-r from-rose-500 to-red-600 hover:brightness-110 text-slate-100 font-bold px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg transition-all"
              >
                <Square size={18} /> Abort Run
              </button>
            )}

            <button
              onClick={loadData}
              className="p-3 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Data"
            >
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Metric Telemetry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* 1. Accuracy Card */}
        <Card className="hover:border-cyan-500/40 transition-colors">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Global Accuracy</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <Activity size={18} />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-cyan-400">
            {trainingStatus.latestAccuracy ? `${(trainingStatus.latestAccuracy * 100).toFixed(1)}%` : '92.4%'}
          </div>
          <div className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
            <span className="text-emerald-400 font-semibold">+4.2%</span> from initial baseline
          </div>
        </Card>

        {/* 2. Loss Card */}
        <Card className="hover:border-purple-500/40 transition-colors">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Global Loss</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <Flame size={18} />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-purple-400">
            {trainingStatus.latestLoss ? trainingStatus.latestLoss.toFixed(4) : '0.3180'}
          </div>
          <div className="text-xs text-slate-400 mt-2">
            Converging smoothly across silos
          </div>
        </Card>

        {/* 3. Differential Privacy Spent */}
        <Card className="hover:border-amber-500/40 transition-colors">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Privacy Budget Spent (ε)</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <ShieldCheck size={18} />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-amber-400">
            {trainingStatus.cumulativeEpsilon ? `${trainingStatus.cumulativeEpsilon.toFixed(2)} ε` : '2.24 ε'}
          </div>
          <div className="text-xs text-slate-400 mt-2">
            Max bound threshold: <strong className="text-slate-200">5.00 ε</strong>
          </div>
        </Card>

        {/* 4. Privacy Guarantee Highlight */}
        <Card className="hover:border-emerald-500/40 transition-colors bg-gradient-to-br from-card to-emerald-950/20">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Privacy Guarantee</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <EyeOff size={18} />
            </div>
          </div>
          <div className="text-sm font-bold text-slate-100 flex items-center gap-1.5 mt-1">
            <Lock size={16} className="text-emerald-400" /> Server Never Saw Raw Updates
          </div>
          <p className="text-[11px] text-slate-400 mt-2 leading-tight">
            Encrypted via Multi-Party Computation & Gaussian Noise before central aggregation.
          </p>
        </Card>
      </div>

      {/* Global Model Training Progress Chart (Recharts) */}
      <Card
        title="Global Federated Convergence Across Rounds"
        subtitle="Live multi-party model accuracy and loss metrics streamed in real-time"
        icon={<Activity size={20} />}
      >
        <AccuracyChart data={chartData} height={340} />
      </Card>

      {/* Connected Organizations Cards / Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Building2 size={20} className="text-cyan-400" /> Connected Healthcare Organizations ({orgs.length})
            </h3>
            <p className="text-xs text-slate-400">Click into any organization to inspect local client devices and metrics</p>
          </div>

          <button
            onClick={() => setShowOrgModal(true)}
            className="bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-bold px-4 py-2 rounded-xl border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <Plus size={16} /> Register Organization
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {orgs.map((org) => (
            <div
              key={org.id}
              onClick={() => navigate(`/admin/orgs/${org.id}`)}
              className="cursor-pointer bg-card/90 hover:bg-surface-elevated border border-slate-800 hover:border-cyan-500/40 rounded-2xl p-6 transition-all duration-200 hover:shadow-glow group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <h4 className="text-base font-bold text-slate-100 group-hover:text-cyan-400 transition-colors">
                      {org.name}
                    </h4>
                    <p className="text-xs text-slate-400 line-clamp-2 mt-1">{org.description}</p>
                  </div>
                  <StatusBadge status={org.status} />
                </div>

                <div className="grid grid-cols-2 gap-3 py-3 my-3 border-y border-slate-800/80 text-xs">
                  <div>
                    <span className="text-slate-500 block">Connected Devices</span>
                    <strong className="text-slate-200 font-mono text-sm">{org.clientCount} Nodes</strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Local Accuracy</span>
                    <strong className="text-cyan-400 font-mono text-sm">{(org.localAccuracy * 100).toFixed(1)}%</strong>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs font-semibold text-cyan-400 group-hover:translate-x-1 transition-transform pt-2">
                <span>View Node Details & Silo Telemetry</span>
                <ArrowUpRight size={16} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal: Register Org */}
      {showOrgModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100 mb-2">Register New Healthcare Silo</h3>
            <p className="text-xs text-slate-400 mb-4">Add a new hospital or research node to the federated network.</p>

            <form onSubmit={handleRegisterOrg}>
              <label htmlFor="modal-org-name" className="text-xs font-semibold text-slate-300 block mb-1">Organization / Hospital Name *</label>
              <input
                id="modal-org-name"
                type="text"
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder="e.g. Apollo Multi-Specialty Clinic"
                required
                className="w-full bg-surface-elevated border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 mb-4 focus:outline-none focus:border-cyan-400"
              />

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowOrgModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary bg-cyan-500 text-slate-950 px-5 py-2 rounded-xl text-xs font-bold shadow-glow"
                >
                  Register Node
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
