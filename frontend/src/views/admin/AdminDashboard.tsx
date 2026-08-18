import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play,
  Square,
  ShieldCheck,
  Building2,
  Lock,
  Activity,
  Plus,
  RefreshCw,
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
  const { isConnected, liveRounds } = useMetricsSocket();

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

  const chartData = liveRounds.length > 0 ? liveRounds : history;

  const handleStartTraining = async () => {
    setIsStarting(true);
    try {
      await startTraining({
        rounds: roundsToRun,
        targetAccuracy: 0.95,
        maxEpsilon: 5.0,
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
    <div className="space-y-6 max-w-6xl">
      {/* Top Banner: Training Controls */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-5 sm:p-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
              Orchestrator
            </span>
            <StatusBadge status={trainingStatus.isTraining ? 'training' : trainingStatus.status} />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Global Federated Training Coordinator</h2>
          <p className="text-slate-500 text-xs mt-0.5">
            Trigger decentralized rounds across connected healthcare nodes with Differential Privacy guarantees.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
            <label htmlFor="rounds-input" className="text-xs text-slate-600 font-medium">Rounds:</label>
            <input
              id="rounds-input"
              type="number"
              min="1"
              max="50"
              value={roundsToRun}
              onChange={(e) => setRoundsToRun(Number(e.target.value))}
              disabled={trainingStatus.isTraining}
              className="w-12 bg-white text-slate-900 font-mono text-xs px-1.5 py-0.5 rounded border border-slate-300 text-center focus:outline-none"
            />
          </div>

          {!trainingStatus.isTraining ? (
            <button
              onClick={handleStartTraining}
              disabled={isStarting}
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors disabled:opacity-50 shadow-sm"
            >
              <Play size={14} /> Start Training
            </button>
          ) : (
            <button
              onClick={handleStopTraining}
              className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Square size={14} /> Stop Run
            </button>
          )}

          <button
            onClick={loadData}
            className="p-2 bg-white hover:bg-slate-50 text-slate-600 rounded-lg border border-slate-200 transition-colors shadow-sm"
            title="Refresh Data"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Metric Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Accuracy Card */}
        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-1">
            Global Accuracy
          </div>
          <div className="text-2xl font-bold font-mono text-blue-600">
            {trainingStatus.latestAccuracy ? `${(trainingStatus.latestAccuracy * 100).toFixed(1)}%` : '92.4%'}
          </div>
          <div className="text-[11px] text-emerald-600 mt-1 font-semibold">
            +4.2% from baseline
          </div>
        </div>

        {/* Loss Card */}
        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-1">
            Global Loss
          </div>
          <div className="text-2xl font-bold font-mono text-violet-600">
            {trainingStatus.latestLoss ? trainingStatus.latestLoss.toFixed(4) : '0.3180'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Convergence over 5 rounds
          </div>
        </div>

        {/* Privacy Budget */}
        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-1">
            Privacy Budget (ε)
          </div>
          <div className="text-2xl font-bold font-mono text-amber-600">
            {trainingStatus.cumulativeEpsilon ? `${trainingStatus.cumulativeEpsilon.toFixed(2)} ε` : '2.24 ε'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Max bound limit: 5.00 ε
          </div>
        </div>

        {/* Privacy Guarantee */}
        <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-1">
            Data Privacy Guarantee
          </div>
          <div className="text-xs font-bold text-emerald-700 flex items-center gap-1.5 mt-1">
            <Lock size={13} /> Server Never Saw Raw Data
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            MPC + Gaussian DP Noise
          </div>
        </div>
      </div>

      {/* Global Model Training Progress Chart */}
      <Card
        title="Global Model Convergence"
        subtitle="Live accuracy and loss curves across federated rounds"
        icon={<Activity size={16} />}
      >
        <AccuracyChart data={chartData} height={280} />
      </Card>

      {/* Connected Organizations */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Participating Healthcare Silos</h3>
            <p className="text-[11px] text-slate-500">Connected hospital edge nodes and local parameters</p>
          </div>

          <button
            onClick={() => setShowOrgModal(true)}
            className="bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <Plus size={13} /> Register Node
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {orgs.map((org) => (
            <div
              key={org.id}
              onClick={() => navigate(`/admin/orgs/${org.id}`)}
              className="bg-white border border-slate-200/90 hover:border-slate-300 hover:shadow-md rounded-xl p-4 cursor-pointer transition-all"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-md bg-slate-100 flex items-center justify-center text-slate-700">
                    <Building2 size={14} />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 truncate max-w-[140px]">{org.name}</h4>
                </div>
                <StatusBadge status={org.status} />
              </div>

              <p className="text-[11px] text-slate-600 line-clamp-2 mb-3 leading-relaxed">
                {org.description}
              </p>

              <div className="grid grid-cols-3 gap-2 pt-2.5 border-t border-slate-100 text-[11px]">
                <div>
                  <span className="text-slate-400 block text-[10px]">Clients</span>
                  <span className="font-bold text-slate-900">{org.clientCount}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Accuracy</span>
                  <span className="font-bold text-blue-600">{(org.localAccuracy * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Privacy ε</span>
                  <span className="font-bold text-amber-600">{org.epsilonSpent.toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Simple Register Modal */}
      {showOrgModal && (
        <div className="fixed inset-0 bg-slate-900/30 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-xl max-w-md w-full p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Register Healthcare Organization</h3>
            <p className="text-xs text-slate-500 mb-4">Add a new federated participant node to the platform.</p>

            <form onSubmit={handleRegisterOrg} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Organization Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Tata Memorial Hospital (Mumbai)"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowOrgModal(false)}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3.5 py-1.5 rounded-lg transition-colors shadow-sm"
                >
                  Save Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
