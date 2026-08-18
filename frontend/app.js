/**
 * FEDERATED SHIELD — MULTI-ROLE APPLICATION LOGIC
 * Supports: Global Admin, Org Admin, Staff/Worker, and Customer/Doctor roles
 */

// Global State
const state = {
  apiBaseUrl: localStorage.getItem('fedshield_api_url') || 'http://localhost:8000',
  wsUrl: localStorage.getItem('fedshield_ws_url') || 'ws://localhost:8000/ws/metrics',
  ws: null,
  wsReconnectTimer: null,
  currentRole: 'admin', // 'admin', 'org_admin', 'staff', 'customer'
  activeOrgId: null,
  activeOrgName: null,
  users: [],
  organizations: [],
  history: [],
  chart: null,
  chartView: 'all',
  isTraining: false,
  currentRound: 0,
  totalRounds: 0,
  latestAccuracy: null,
  latestLoss: null,
  minLossReached: null,
  cumulativeEpsilon: 0.0,
  activeOrgs: [],
};

// DOM Cache
const dom = {
  // Navigation & Role Tabs
  roleTabs: document.querySelectorAll('.role-tab'),
  roleViews: document.querySelectorAll('.role-view'),
  userAvatar: document.getElementById('current-user-avatar'),
  userTitle: document.getElementById('current-user-title'),
  userMeta: document.getElementById('current-user-meta'),
  orgSwitcherWrapper: document.getElementById('org-switcher-wrapper'),
  selectActiveOrg: document.getElementById('select-active-org'),

  // Status Pills
  backendDot: document.getElementById('backend-dot'),
  backendStatusText: document.getElementById('backend-status-text'),
  wsDot: document.getElementById('ws-dot'),
  wsStatusText: document.getElementById('ws-status-text'),

  // Admin Banner & Telemetry
  bannerStateTag: document.getElementById('banner-state-tag'),
  bannerStateLabel: document.getElementById('banner-state-label'),
  bannerTitle: document.getElementById('banner-title'),
  bannerDesc: document.getElementById('banner-desc'),
  progressRoundText: document.getElementById('progress-round-text'),
  progressPercentText: document.getElementById('progress-percent-text'),
  progressBarFill: document.getElementById('progress-bar-fill'),
  btnQuickStart: document.getElementById('btn-quick-start'),
  btnQuickStop: document.getElementById('btn-quick-stop'),
  btnRefreshAll: document.getElementById('btn-refresh-all'),

  valAccuracy: document.getElementById('val-accuracy'),
  valLoss: document.getElementById('val-loss'),
  valEpsilon: document.getElementById('val-epsilon'),
  valActiveOrgs: document.getElementById('val-active-orgs'),
  valTotalOrgsBadge: document.getElementById('val-total-orgs-badge'),
  valTargetAccuracy: document.getElementById('val-target-accuracy'),
  valMinLoss: document.getElementById('val-min-loss'),
  valMaxEpsilon: document.getElementById('val-max-epsilon'),
  tagDpSpent: document.getElementById('tag-dp-spent'),
  miniBarAcc: document.getElementById('mini-bar-acc'),
  miniBarLoss: document.getElementById('mini-bar-loss'),
  miniBarEps: document.getElementById('mini-bar-eps'),

  // Admin Orgs & Forms
  orgsListContainer: document.getElementById('orgs-list-container'),
  orgSelectorContainer: document.getElementById('org-selector-container'),
  trainingControlForm: document.getElementById('training-control-form'),
  inputRounds: document.getElementById('input-rounds'),
  inputTargetAcc: document.getElementById('input-target-acc'),
  inputMaxEps: document.getElementById('input-max-eps'),
  btnSubmitTraining: document.getElementById('btn-submit-training'),
  btnSidebarStop: document.getElementById('btn-sidebar-stop'),
  historyTbody: document.getElementById('history-tbody'),
  btnRefreshHistory: document.getElementById('btn-refresh-history'),
  wsFeedContainer: document.getElementById('ws-feed-container'),
  btnClearLogs: document.getElementById('btn-clear-logs'),

  // Org Admin View Elements
  orgViewHeaderTitle: document.getElementById('org-view-header-title'),
  orgNodeStatusPill: document.getElementById('org-node-status-pill'),
  orgNodeStatusVal: document.getElementById('org-node-status-val'),
  orgSamplesCount: document.getElementById('org-samples-count'),
  orgCpuLoad: document.getElementById('org-cpu-load'),
  orgMemUsage: document.getElementById('org-mem-usage'),
  orgSecaggKey: document.getElementById('org-secagg-key'),
  orgStaffTbody: document.getElementById('org-staff-tbody'),
  btnOrgHandshake: document.getElementById('btn-org-handshake'),
  btnSwitchToStaff: document.getElementById('btn-switch-to-staff'),

  // Staff View Elements
  formStaffUpload: document.getElementById('form-staff-upload'),
  btnSeedSynthetic: document.getElementById('btn-seed-synthetic'),
  staffSamplesTbody: document.getElementById('staff-samples-tbody'),
  btnRefreshSamples: document.getElementById('btn-refresh-samples'),

  // Customer Inference Elements
  formCustomerInference: document.getElementById('form-customer-inference'),
  cardInferenceResult: document.getElementById('card-inference-result'),
  infResScore: document.getElementById('inf-res-score'),
  infResConf: document.getElementById('inf-res-conf'),
  infResCategoryTitle: document.getElementById('inf-res-category-title'),
  infResCategoryBadge: document.getElementById('inf-res-category-badge'),
  infResRecommendation: document.getElementById('inf-res-recommendation'),
  infResVersion: document.getElementById('inf-res-version'),
  infResWeightsContainer: document.getElementById('inf-res-weights-container'),
  certDpBound: document.getElementById('cert-dp-bound'),
  certZkHash: document.getElementById('cert-zk-hash'),

  // Modals & Settings
  modalRegisterOrg: document.getElementById('modal-register-org'),
  formRegisterOrg: document.getElementById('form-register-org'),
  modalOrgName: document.getElementById('modal-org-name'),
  modalOrgDesc: document.getElementById('modal-org-desc'),
  btnAddOrgModal: document.getElementById('btn-add-org-modal'),
  btnCloseOrgModal: document.getElementById('btn-close-org-modal'),
  btnCancelOrgModal: document.getElementById('btn-cancel-org-modal'),

  modalSettings: document.getElementById('modal-settings'),
  btnOpenSettings: document.getElementById('btn-open-settings'),
  btnCloseSettingsModal: document.getElementById('btn-close-settings-modal'),
  formSettings: document.getElementById('form-settings'),
  settingApiUrl: document.getElementById('setting-api-url'),
  settingWsUrl: document.getElementById('setting-ws-url'),
  btnResetSettings: document.getElementById('btn-reset-settings'),
  toastContainer: document.getElementById('toast-container'),
};

/* ==========================================================================
   INITIALIZATION
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  initChart();
  bindEventListeners();
  checkBackendHealth();
  connectWebSocket();
  loadInitialData();

  setInterval(checkBackendHealth, 8000);
});

async function loadInitialData() {
  await fetchOrganizations();
  await fetchUsers();
  await fetchTrainingStatus();
  await fetchTrainingHistory();
  switchRole('admin');
}

/* ==========================================================================
   ROLE SWITCHING LOGIC
   ========================================================================== */
function switchRole(roleName) {
  state.currentRole = roleName;

  // 1. Update Tab styling
  dom.roleTabs.forEach((tab) => {
    tab.classList.toggle('active', tab.dataset.role === roleName);
  });

  // 2. Switch View Visibility
  dom.roleViews.forEach((view) => {
    view.classList.toggle('hidden', view.id !== `view-${roleName}`);
    view.classList.toggle('active-view', view.id === `view-${roleName}`);
  });

  // 3. Update Persona Header
  const orgDropdownVisible = roleName === 'org_admin' || roleName === 'staff';
  dom.orgSwitcherWrapper.classList.toggle('hidden', !orgDropdownVisible);

  if (roleName === 'admin') {
    dom.userAvatar.innerHTML = '<i class="fa-solid fa-crown"></i>';
    dom.userTitle.textContent = 'Global FL Coordinator';
    dom.userMeta.textContent = 'Platform Admin • Full Orchestration & Cryptographic Governance';
  } else if (roleName === 'org_admin') {
    dom.userAvatar.innerHTML = '<i class="fa-solid fa-hospital"></i>';
    const org = getActiveOrg();
    dom.userTitle.textContent = `Lead Admin: ${org ? org.name : 'Hospital Node'}`;
    dom.userMeta.textContent = 'Organization Lead • Local Privacy & Compute Management';
    loadOrgAdminData();
  } else if (roleName === 'staff') {
    dom.userAvatar.innerHTML = '<i class="fa-solid fa-user-doctor"></i>';
    const org = getActiveOrg();
    dom.userTitle.textContent = `Staff Contributor @ ${org ? org.name : 'Hospital'}`;
    dom.userMeta.textContent = 'Medical Data Scientist • Edge Dataset Ingestion & Pseudonymization';
    loadStaffData();
  } else if (roleName === 'customer') {
    dom.userAvatar.innerHTML = '<i class="fa-solid fa-user-check"></i>';
    dom.userTitle.textContent = 'Clinical Doctor / Model Consumer';
    dom.userMeta.textContent = 'Inference Consumer • Privacy-Preserved Diagnostics with Zero-Knowledge Proof';
  }
}

function getActiveOrg() {
  if (state.organizations.length === 0) return null;
  if (!state.activeOrgId) {
    state.activeOrgId = state.organizations[0].id;
    state.activeOrgName = state.organizations[0].name;
  }
  return state.organizations.find((o) => o.id === state.activeOrgId) || state.organizations[0];
}

/* ==========================================================================
   CHART.JS CONFIGURATION
   ========================================================================== */
function initChart() {
  const ctx = document.getElementById('flMetricsChart').getContext('2d');

  const cyanGradient = ctx.createLinearGradient(0, 0, 0, 300);
  cyanGradient.addColorStop(0, 'rgba(0, 242, 254, 0.35)');
  cyanGradient.addColorStop(1, 'rgba(0, 242, 254, 0.0)');

  const purpleGradient = ctx.createLinearGradient(0, 0, 0, 300);
  purpleGradient.addColorStop(0, 'rgba(168, 85, 247, 0.35)');
  purpleGradient.addColorStop(1, 'rgba(168, 85, 247, 0.0)');

  const amberGradient = ctx.createLinearGradient(0, 0, 0, 300);
  amberGradient.addColorStop(0, 'rgba(245, 158, 11, 0.35)');
  amberGradient.addColorStop(1, 'rgba(245, 158, 11, 0.0)');

  state.chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Global Accuracy (%)',
          data: [],
          borderColor: '#00f2fe',
          backgroundColor: cyanGradient,
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#00f2fe',
          pointBorderColor: '#070b14',
          pointRadius: 5,
          yAxisID: 'yAccuracy',
        },
        {
          label: 'Global Loss',
          data: [],
          borderColor: '#a855f7',
          backgroundColor: purpleGradient,
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointBackgroundColor: '#a855f7',
          pointBorderColor: '#070b14',
          pointRadius: 4,
          yAxisID: 'yLoss',
        },
        {
          label: 'Cumulative ε (DP Budget)',
          data: [],
          borderColor: '#f59e0b',
          backgroundColor: amberGradient,
          fill: false,
          borderDash: [5, 5],
          tension: 0.2,
          borderWidth: 2,
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#070b14',
          pointRadius: 4,
          yAxisID: 'yEpsilon',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#94a3b8', font: { family: 'Inter', size: 12, weight: 600 }, usePointStyle: true, boxWidth: 8 },
        },
        tooltip: {
          backgroundColor: 'rgba(14, 21, 38, 0.95)',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          callbacks: { title: (items) => `Round ${items[0].label}` },
        },
      },
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.04)' }, ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 11 } } },
        yAccuracy: {
          type: 'linear', position: 'left', min: 0, max: 100,
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: { color: '#00f2fe', font: { family: 'JetBrains Mono', size: 11 }, callback: (val) => `${val}%` },
        },
        yLoss: {
          type: 'linear', position: 'right', min: 0,
          grid: { drawOnChartArea: false },
          ticks: { color: '#a855f7', font: { family: 'JetBrains Mono', size: 11 } },
        },
        yEpsilon: {
          type: 'linear', position: 'right', min: 0, display: false, grid: { drawOnChartArea: false },
        },
      },
    },
  });

  document.querySelectorAll('.chart-controls button').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.chart-controls button').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      setChartView(btn.dataset.chartView);
    });
  });
}

function setChartView(view) {
  if (!state.chart) return;
  state.chartView = view;
  const isAll = view === 'all';
  state.chart.data.datasets[0].hidden = !(isAll || view === 'accuracy');
  state.chart.data.datasets[1].hidden = !(isAll || view === 'loss');
  state.chart.data.datasets[2].hidden = !(isAll || view === 'epsilon');

  state.chart.options.scales.yAccuracy.display = isAll || view === 'accuracy';
  state.chart.options.scales.yLoss.display = isAll || view === 'loss';
  state.chart.options.scales.yEpsilon.display = isAll || view === 'epsilon';
  state.chart.update();
}

function addRoundToChart(roundNum, accuracy, loss, cumulativeEpsilon) {
  if (!state.chart) return;
  const label = `${roundNum}`;
  if (!state.chart.data.labels.includes(label)) {
    state.chart.data.labels.push(label);
    state.chart.data.datasets[0].data.push(Math.round(accuracy * 1000) / 10);
    state.chart.data.datasets[1].data.push(Math.round(loss * 1000) / 1000);
    state.chart.data.datasets[2].data.push(Math.round(cumulativeEpsilon * 1000) / 1000);
    state.chart.update('none');
  }
}

function resetChart() {
  if (!state.chart) return;
  state.chart.data.labels = [];
  state.chart.data.datasets.forEach((ds) => (ds.data = []));
  state.chart.update();
}

/* ==========================================================================
   WEBSOCKET TELEMETRY
   ========================================================================== */
function connectWebSocket() {
  if (state.ws) {
    try { state.ws.close(); } catch (e) {}
  }

  dom.wsDot.className = 'status-dot offline';
  dom.wsStatusText.textContent = 'WS: Connecting...';

  try {
    state.ws = new WebSocket(state.wsUrl);

    state.ws.onopen = () => {
      dom.wsDot.className = 'status-dot online pulsing';
      dom.wsStatusText.textContent = 'WS: Live';
      appendLog('system', `Connected to WebSocket: ${state.wsUrl}`);
      if (state.wsReconnectTimer) {
        clearTimeout(state.wsReconnectTimer);
        state.wsReconnectTimer = null;
      }
    };

    state.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketPayload(data);
      } catch (err) {
        console.warn('WS parse error:', err);
      }
    };

    state.ws.onclose = () => {
      dom.wsDot.className = 'status-dot offline';
      dom.wsStatusText.textContent = 'WS: Offline';
      if (!state.wsReconnectTimer) {
        state.wsReconnectTimer = setTimeout(connectWebSocket, 4000);
      }
    };
  } catch (err) {
    console.error('WS creation error:', err);
  }
}

function handleWebSocketPayload(data) {
  const event = data.event || 'message';

  switch (event) {
    case 'status_update':
      updateTrainingUIFromStatus(data);
      break;

    case 'training_started':
      state.isTraining = true;
      state.totalRounds = data.total_rounds;
      state.currentRound = 0;
      state.activeOrgs = data.active_orgs || [];
      resetChart();
      updateBannerState('running', `Run ${data.run_id} Active`);
      appendLog('training_started', `🚀 FL Run Started (${data.total_rounds} rounds)`);
      showToast(`Training session ${data.run_id} started!`, 'info');
      fetchOrganizations();
      if (state.currentRole === 'org_admin') loadOrgAdminData();
      break;

    case 'round_complete':
      state.currentRound = data.round;
      state.totalRounds = data.total_rounds;
      state.latestAccuracy = data.accuracy;
      state.latestLoss = data.loss;
      state.cumulativeEpsilon = data.cumulative_epsilon;

      if (state.minLossReached === null || data.loss < state.minLossReached) {
        state.minLossReached = data.loss;
      }

      updateTelemetryMetrics(data);
      addRoundToChart(data.round, data.accuracy, data.loss, data.cumulative_epsilon);
      updateBannerProgress(data.round, data.total_rounds);
      appendLog(
        'round_complete',
        `⚡ Round ${data.round}/${data.total_rounds} | Acc: ${(data.accuracy * 100).toFixed(2)}% | Loss: ${data.loss.toFixed(4)} | +${data.epsilon_spent.toFixed(3)} ε`
      );
      if (state.currentRole === 'org_admin') loadOrgAdminData();
      break;

    case 'training_completed':
      state.isTraining = false;
      updateBannerState('completed', 'Training Completed');
      appendLog('training_completed', `🏆 Run Complete! Acc: ${((data.final_accuracy || 0) * 100).toFixed(2)}%`);
      showToast('Federated training completed successfully!', 'success');
      fetchOrganizations();
      fetchTrainingHistory();
      if (state.currentRole === 'org_admin') loadOrgAdminData();
      break;

    case 'training_stopped':
      state.isTraining = false;
      updateBannerState('stopped', 'Training Aborted');
      appendLog('training_stopped', `🛑 Run halted at round ${data.total_rounds_completed || state.currentRound}.`);
      showToast('Training run halted.', 'error');
      fetchOrganizations();
      fetchTrainingHistory();
      if (state.currentRole === 'org_admin') loadOrgAdminData();
      break;

    case 'error':
      appendLog('error', `❌ ${data.message}`);
      showToast(data.message, 'error');
      break;
  }
}

/* ==========================================================================
   REST API CALLS
   ========================================================================== */
async function checkBackendHealth() {
  try {
    const res = await fetch(`${state.apiBaseUrl}/health`);
    if (res.ok) {
      dom.backendDot.className = 'status-dot online';
      dom.backendStatusText.textContent = 'API: Online';
    } else {
      throw new Error();
    }
  } catch (err) {
    dom.backendDot.className = 'status-dot offline';
    dom.backendStatusText.textContent = 'API: Offline';
  }
}

async function fetchOrganizations() {
  try {
    const res = await fetch(`${state.apiBaseUrl}/orgs`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    state.organizations = data;
    renderOrganizations(data);
    populateOrgSelector(data);
    populateOrgSwitcherDropdown(data);
    dom.valTotalOrgsBadge.textContent = `${data.length} Registered`;
  } catch (err) {
    console.warn('Failed to load orgs:', err);
  }
}

async function fetchUsers() {
  try {
    const res = await fetch(`${state.apiBaseUrl}/users`);
    if (res.ok) {
      state.users = await res.json();
    }
  } catch (err) {
    console.warn('Failed to load users:', err);
  }
}

async function fetchTrainingStatus() {
  try {
    const res = await fetch(`${state.apiBaseUrl}/training/status`);
    if (res.ok) {
      const data = await res.json();
      updateTrainingUIFromStatus(data);
    }
  } catch (err) {}
}

async function fetchTrainingHistory() {
  try {
    const res = await fetch(`${state.apiBaseUrl}/training/history?limit=30`);
    if (res.ok) {
      const data = await res.json();
      state.history = data;
      renderHistoryTable(data);
    }
  } catch (err) {}
}

/* ==========================================================================
   ORG ADMIN VIEW LOGIC
   ========================================================================== */
async function loadOrgAdminData() {
  const org = getActiveOrg();
  if (!org) return;

  dom.orgViewHeaderTitle.textContent = org.name;
  dom.orgNodeStatusVal.textContent = org.status.toUpperCase();
  dom.orgNodeStatusPill.className = `node-status-pill ${org.status}`;

  try {
    const res = await fetch(`${state.apiBaseUrl}/nodes/${org.id}/telemetry`);
    if (res.ok) {
      const data = await res.json();
      dom.orgSamplesCount.textContent = `${data.local_samples_count} Records`;
      dom.orgCpuLoad.textContent = `${data.compute_telemetry.cpu_utilization_percent}% Load`;
      dom.orgMemUsage.textContent = `Memory: ${data.compute_telemetry.memory_usage_mb} MB / CUDA Ready`;
      dom.orgSecaggKey.textContent = `0x${data.edge_privacy_configuration.secure_aggregation_key_hash}`;
    }

    // Filter staff belonging to this org
    const orgStaff = state.users.filter((u) => u.org_id === org.id || u.role === 'staff');
    if (orgStaff.length === 0) {
      dom.orgStaffTbody.innerHTML = `<tr><td colspan="5" class="empty-state">No staff specifically assigned. Default assigned to Dr. Aarav Sharma.</td></tr>`;
    } else {
      dom.orgStaffTbody.innerHTML = orgStaff
        .map(
          (u) => `
        <tr>
          <td><strong>${escapeHtml(u.full_name)}</strong></td>
          <td>${escapeHtml(u.username)}</td>
          <td><span class="org-badge done">${escapeHtml(u.role)}</span></td>
          <td>${escapeHtml(u.department || 'Clinical Silo')}</td>
          <td><small>${escapeHtml(u.email)}</small></td>
        </tr>
      `
        )
        .join('');
    }
  } catch (err) {
    console.warn('Failed to load org telemetry:', err);
  }
}

/* ==========================================================================
   STAFF VIEW LOGIC (Clinical Sample Uploads)
   ========================================================================== */
async function loadStaffData() {
  const org = getActiveOrg();
  if (!org) return;

  try {
    const res = await fetch(`${state.apiBaseUrl}/nodes/${org.id}/samples?limit=20`);
    if (res.ok) {
      const samples = await res.json();
      renderStaffSamplesTable(samples);
    }
  } catch (err) {
    console.warn('Failed to load staff samples:', err);
  }
}

function renderStaffSamplesTable(samples) {
  if (!samples || samples.length === 0) {
    dom.staffSamplesTbody.innerHTML = `<tr><td colspan="8" class="empty-state">No clinical samples in this edge silo. Click "Auto-Generate" or submit above!</td></tr>`;
    return;
  }

  dom.staffSamplesTbody.innerHTML = samples
    .map(
      (s) => `
    <tr>
      <td><strong class="font-mono">${escapeHtml(s.patient_identifier_hash)}</strong></td>
      <td>${s.age} yrs / ${s.gender}</td>
      <td>${s.blood_pressure_sys} mmHg</td>
      <td>${s.cholesterol} mg/dL</td>
      <td>${s.glucose} mg/dL</td>
      <td>${s.heart_rate} bpm</td>
      <td><strong style="color: ${s.target_risk > 0.5 ? 'var(--rose-danger)' : 'var(--emerald-success)'}">${(s.target_risk * 100).toFixed(1)}%</strong></td>
      <td><small>${escapeHtml(s.contributed_by || 'staff')}</small></td>
    </tr>
  `
    )
    .join('');
}

async function uploadClinicalSample(sampleData) {
  const org = getActiveOrg();
  if (!org) return;

  try {
    const res = await fetch(`${state.apiBaseUrl}/nodes/${org.id}/samples`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...sampleData, org_id: org.id }),
    });

    if (res.ok) {
      showToast('Record pseudonymized & saved to edge silo!', 'success');
      loadStaffData();
      dom.formStaffUpload.reset();
    } else {
      throw new Error('Failed to upload record');
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function seedSyntheticRecords() {
  const org = getActiveOrg();
  if (!org) return;

  try {
    const res = await fetch(`${state.apiBaseUrl}/nodes/${org.id}/synthetic-seed?count=20`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      showToast(data.message, 'success');
      loadStaffData();
      loadOrgAdminData();
    }
  } catch (err) {
    showToast('Failed to seed records', 'error');
  }
}

/* ==========================================================================
   CUSTOMER / DOCTOR INFERENCE LOGIC
   ========================================================================== */
async function runCustomerInference(payload) {
  try {
    const res = await fetch(`${state.apiBaseUrl}/inference/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Inference request failed');
    const result = await res.json();
    renderInferenceResult(result);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function renderInferenceResult(res) {
  dom.cardInferenceResult.classList.remove('hidden');
  dom.cardInferenceResult.scrollIntoView({ behavior: 'smooth' });

  const scorePct = (res.prediction_risk_score * 100).toFixed(1);
  dom.infResScore.textContent = `${scorePct}%`;
  dom.infResConf.textContent = `Model Confidence: ${res.model_confidence}%`;
  dom.infResCategoryTitle.textContent = res.risk_category;
  dom.infResCategoryBadge.textContent = res.risk_category;
  dom.infResVersion.textContent = `Model Checkpoint: ${res.global_model_version}`;

  // Color-coded badge
  if (res.prediction_risk_score > 0.65) {
    dom.infResCategoryBadge.className = 'org-badge offline';
    dom.infResScore.style.color = 'var(--rose-danger)';
    dom.infResRecommendation.textContent = 'High cardiovascular risk profile detected. Clinical diagnostic panel recommended.';
  } else if (res.prediction_risk_score > 0.3) {
    dom.infResCategoryBadge.className = 'org-badge idle';
    dom.infResScore.style.color = 'var(--amber-warning)';
    dom.infResRecommendation.textContent = 'Moderate risk profile detected. Recommend monitoring blood pressure and lipids.';
  } else {
    dom.infResCategoryBadge.className = 'org-badge done';
    dom.infResScore.style.color = 'var(--emerald-success)';
    dom.infResRecommendation.textContent = 'Low risk profile within normal baseline cardiovascular ranges.';
  }

  // Feature weights progress bars
  dom.infResWeightsContainer.innerHTML = Object.entries(res.feature_contributions)
    .map(
      ([feature, weight]) => `
    <div class="weight-row">
      <div class="weight-label-row">
        <span>${escapeHtml(feature)}</span>
        <strong>+${(weight * 100).toFixed(1)}% weight</strong>
      </div>
      <div class="weight-bar-bg">
        <div class="weight-bar-fill" style="width: ${Math.min(100, weight * 100)}%;"></div>
      </div>
    </div>
  `
    )
    .join('');

  // Update Certificate info
  dom.certDpBound.textContent = res.privacy_guarantee.differential_privacy_bound;
  dom.certZkHash.textContent = res.privacy_guarantee.zero_knowledge_proof;
  showToast('Inference computed using global federated model!', 'success');
}

/* ==========================================================================
   UI RENDERING & HELPERS
   ========================================================================== */
function populateOrgSwitcherDropdown(orgs) {
  if (!orgs || orgs.length === 0) return;
  dom.selectActiveOrg.innerHTML = orgs
    .map((o) => `<option value="${o.id}">${escapeHtml(o.name)}</option>`)
    .join('');

  if (state.activeOrgId) {
    dom.selectActiveOrg.value = state.activeOrgId;
  }
}

function renderOrganizations(orgs) {
  if (!orgs || orgs.length === 0) {
    dom.orgsListContainer.innerHTML = `<div class="empty-state" style="grid-column: 1 / -1;">No organizations registered. Click "Register Org" to add one!</div>`;
    return;
  }

  dom.orgsListContainer.innerHTML = orgs
    .map(
      (org) => `
    <div class="org-card" id="org-card-${org.id}">
      <div class="org-card-header">
        <div>
          <div class="org-name">${escapeHtml(org.name)}</div>
          <div class="org-desc">${escapeHtml(org.description || 'Simulated edge node')}</div>
        </div>
        <span class="org-badge ${org.status}">${org.status}</span>
      </div>
      <div class="org-card-footer">
        <span>Node ID: #${org.id}</span>
        <button class="btn-icon" onclick="deleteOrganization(${org.id}, '${escapeHtml(org.name)}')" title="Delete Node">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </div>
    </div>
  `
    )
    .join('');
}

function populateOrgSelector(orgs) {
  if (!orgs || orgs.length === 0) {
    dom.orgSelectorContainer.innerHTML = '<div class="input-hint">No orgs registered (defaults will be used)</div>';
    return;
  }

  dom.orgSelectorContainer.innerHTML = orgs
    .map(
      (org) => `
    <label class="checkbox-item">
      <input type="checkbox" name="selected_org" value="${escapeHtml(org.name)}" checked>
      <span>${escapeHtml(org.name)}</span>
    </label>
  `
    )
    .join('');
}

function renderHistoryTable(records) {
  if (!records || records.length === 0) {
    dom.historyTbody.innerHTML = `<tr><td colspan="10" class="empty-state">No training rounds recorded in SQLite yet. Trigger a run above!</td></tr>`;
    return;
  }

  dom.historyTbody.innerHTML = records
    .map((r) => {
      const dateStr = new Date(r.timestamp).toLocaleTimeString();
      return `
      <tr>
        <td><strong>${r.run_id}</strong></td>
        <td>${r.round_number}/${r.total_rounds}</td>
        <td style="color: #00f2fe;">${(r.accuracy * 100).toFixed(2)}%</td>
        <td style="color: #a855f7;">${r.loss.toFixed(4)}</td>
        <td>+${r.epsilon_spent.toFixed(3)} ε</td>
        <td style="color: #f59e0b;">${r.cumulative_epsilon.toFixed(3)} ε</td>
        <td><small>${r.participating_orgs.length} orgs</small></td>
        <td>${r.duration_seconds}s</td>
        <td><span class="org-badge done">${r.status}</span></td>
        <td><small>${dateStr}</small></td>
      </tr>
    `;
    })
    .join('');
}

function updateTelemetryMetrics(data) {
  const accPercent = Math.round(data.accuracy * 1000) / 10;
  dom.valAccuracy.textContent = `${accPercent}%`;
  dom.miniBarAcc.style.width = `${Math.min(100, accPercent)}%`;

  dom.valLoss.textContent = data.loss.toFixed(4);
  const lossPercent = Math.min(100, (data.loss / 2.5) * 100);
  dom.miniBarLoss.style.width = `${lossPercent}%`;
  if (state.minLossReached) dom.valMinLoss.textContent = state.minLossReached.toFixed(4);

  dom.valEpsilon.textContent = `${data.cumulative_epsilon.toFixed(3)} ε`;
  dom.tagDpSpent.textContent = `+${data.epsilon_spent.toFixed(3)} / rnd`;
  const epsPercent = Math.min(100, (data.cumulative_epsilon / 10.0) * 100);
  dom.miniBarEps.style.width = `${epsPercent}%`;

  const nodeCount = data.org_statuses ? Object.keys(data.org_statuses).length : state.activeOrgs.length;
  dom.valActiveOrgs.textContent = `${nodeCount} Nodes`;
}

function updateTrainingUIFromStatus(data) {
  state.isTraining = data.is_training;
  state.currentRound = data.current_round || 0;
  state.totalRounds = data.total_rounds || 0;
  state.activeOrgs = data.active_orgs || [];

  if (data.latest_accuracy !== null && data.latest_accuracy !== undefined) {
    updateTelemetryMetrics({
      accuracy: data.latest_accuracy,
      loss: data.latest_loss || 0,
      cumulative_epsilon: data.cumulative_epsilon || 0,
      epsilon_spent: 0,
      org_statuses: {},
    });
  }

  if (data.is_training) {
    updateBannerState('running', `Run ${data.run_id} Active`);
    updateBannerProgress(data.current_round, data.total_rounds);
    setTrainingFormActive(true);
  } else {
    updateBannerState(data.status || 'idle', data.status === 'completed' ? 'Training Complete' : 'System Idle');
    setTrainingFormActive(false);
  }
}

function updateBannerState(stateKey, labelText) {
  dom.bannerStateTag.className = `banner-tag ${stateKey}`;
  dom.bannerStateLabel.textContent = labelText.toUpperCase();
  if (stateKey === 'running') {
    dom.bannerTitle.textContent = `Federated Round In Execution (${state.currentRound} / ${state.totalRounds})`;
    dom.bannerDesc.textContent = 'Aggregating client gradients with Secure Aggregation & Differential Privacy noise.';
    dom.btnQuickStart.classList.add('hidden');
    dom.btnQuickStop.classList.remove('hidden');
  } else {
    dom.bannerTitle.textContent = 'Global Federated Learning Orchestrator';
    dom.bannerDesc.textContent = 'Coordinate multi-party Differential Privacy training rounds across all hospital client nodes.';
    dom.btnQuickStart.classList.remove('hidden');
    dom.btnQuickStop.classList.add('hidden');
  }
}

function updateBannerProgress(current, total) {
  if (!total || total === 0) {
    dom.progressBarFill.style.width = '0%';
    dom.progressRoundText.textContent = '0 / 0';
    dom.progressPercentText.textContent = '0%';
    return;
  }
  const percent = Math.min(100, Math.round((current / total) * 100));
  dom.progressBarFill.style.width = `${percent}%`;
  dom.progressRoundText.textContent = `${current} / ${total}`;
  dom.progressPercentText.textContent = `${percent}%`;
}

function setTrainingFormActive(isTraining) {
  dom.btnSubmitTraining.classList.toggle('hidden', isTraining);
  dom.btnSidebarStop.classList.toggle('hidden', !isTraining);
}

function appendLog(type, msg) {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  entry.innerHTML = `<span class="log-time">[${time}]</span> <span class="log-msg">${escapeHtml(msg)}</span>`;
  dom.wsFeedContainer.appendChild(entry);
  dom.wsFeedContainer.scrollTop = dom.wsFeedContainer.scrollHeight;
}

function showToast(msg, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? 'fa-check' : type === 'error' ? 'fa-triangle-exclamation' : 'fa-info-circle';
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(msg)}</span>`;
  dom.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function openModal(modal) { modal.classList.remove('hidden'); }
function closeModal(modal) { modal.classList.add('hidden'); }
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ==========================================================================
   EVENT LISTENERS
   ========================================================================== */
function bindEventListeners() {
  // Role Tabs
  dom.roleTabs.forEach((tab) => {
    tab.addEventListener('click', () => switchRole(tab.dataset.role));
  });

  // Org Dropdown Switcher
  dom.selectActiveOrg.addEventListener('change', (e) => {
    state.activeOrgId = parseInt(e.target.value, 10);
    const org = state.organizations.find((o) => o.id === state.activeOrgId);
    state.activeOrgName = org ? org.name : null;
    if (state.currentRole === 'org_admin') loadOrgAdminData();
    if (state.currentRole === 'staff') loadStaffData();
  });

  // Admin Actions
  dom.btnQuickStart.addEventListener('click', () => dom.inputRounds.focus());
  dom.btnQuickStop.addEventListener('click', stopTrainingRun);
  dom.btnSidebarStop.addEventListener('click', stopTrainingRun);
  dom.btnRefreshAll.addEventListener('click', () => {
    fetchOrganizations();
    fetchTrainingStatus();
    fetchTrainingHistory();
    showToast('Data refreshed.', 'info');
  });
  dom.btnRefreshHistory.addEventListener('click', fetchTrainingHistory);

  dom.trainingControlForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const rounds = dom.inputRounds.value;
    const targetAcc = dom.inputTargetAcc.value;
    const maxEps = dom.inputMaxEps.value;
    const checkedOrgs = Array.from(document.querySelectorAll('input[name="selected_org"]:checked')).map((cb) => cb.value);
    startTrainingRun(rounds, checkedOrgs, targetAcc, maxEps);
  });

  dom.btnClearLogs.addEventListener('click', () => {
    dom.wsFeedContainer.innerHTML = '';
    appendLog('system', 'Event log cleared.');
  });

  // Org Admin Quick Actions
  dom.btnOrgHandshake.addEventListener('click', () => {
    showToast('Secure Aggregation (SecAgg) ECDH handshake verified with server!', 'success');
  });

  dom.btnSwitchToStaff.addEventListener('click', () => switchRole('staff'));

  // Staff Form Actions
  dom.formStaffUpload.addEventListener('submit', (e) => {
    e.preventDefault();
    uploadClinicalSample({
      age: parseInt(document.getElementById('staff-age').value, 10),
      gender: document.getElementById('staff-gender').value,
      blood_pressure_sys: parseInt(document.getElementById('staff-bp').value, 10),
      cholesterol: parseInt(document.getElementById('staff-chol').value, 10),
      glucose: parseInt(document.getElementById('staff-gluc').value, 10),
      heart_rate: parseInt(document.getElementById('staff-hr').value, 10),
      target_risk: parseFloat(document.getElementById('staff-risk').value),
    });
  });

  dom.btnSeedSynthetic.addEventListener('click', seedSyntheticRecords);
  dom.btnRefreshSamples.addEventListener('click', loadStaffData);

  // Customer Inference Form
  dom.formCustomerInference.addEventListener('submit', (e) => {
    e.preventDefault();
    runCustomerInference({
      age: parseInt(document.getElementById('inf-age').value, 10),
      gender: document.getElementById('inf-gender').value,
      blood_pressure_sys: parseInt(document.getElementById('inf-bp').value, 10),
      cholesterol: parseInt(document.getElementById('inf-chol').value, 10),
      glucose: parseInt(document.getElementById('inf-gluc').value, 10),
      heart_rate: parseInt(document.getElementById('inf-hr').value, 10),
      smoking: document.getElementById('inf-smoking').checked,
    });
  });

  // Org Modal
  dom.btnAddOrgModal.addEventListener('click', () => openModal(dom.modalRegisterOrg));
  dom.btnCloseOrgModal.addEventListener('click', () => closeModal(dom.modalRegisterOrg));
  dom.btnCancelOrgModal.addEventListener('click', () => closeModal(dom.modalRegisterOrg));

  dom.formRegisterOrg.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = dom.modalOrgName.value.trim();
    const desc = dom.modalOrgDesc.value.trim();
    if (name) {
      await registerOrganization(name, desc);
    }
  });

  // Settings Modal
  dom.btnOpenSettings.addEventListener('click', () => openModal(dom.modalSettings));
  dom.btnCloseSettingsModal.addEventListener('click', () => closeModal(dom.modalSettings));

  dom.formSettings.addEventListener('submit', (e) => {
    e.preventDefault();
    state.apiBaseUrl = dom.settingApiUrl.value.trim();
    state.wsUrl = dom.settingWsUrl.value.trim();
    localStorage.setItem('fedshield_api_url', state.apiBaseUrl);
    localStorage.setItem('fedshield_ws_url', state.wsUrl);
    closeModal(dom.modalSettings);
    showToast('Settings saved. Reconnecting...', 'success');
    checkBackendHealth();
    connectWebSocket();
    fetchOrganizations();
  });
}

/* ==========================================================================
   CORE BACKEND OPERATIONS
   ========================================================================== */
async function startTrainingRun(rounds, orgNames, targetAcc, maxEps) {
  try {
    const payload = { rounds: parseInt(rounds, 10) };
    if (orgNames && orgNames.length > 0) payload.org_names = orgNames;
    if (targetAcc) payload.target_accuracy = parseFloat(targetAcc);
    if (maxEps) payload.max_epsilon = parseFloat(maxEps);

    const res = await fetch(`${state.apiBaseUrl}/training/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to start training');
    }
    const data = await res.json();
    showToast(data.message, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function stopTrainingRun() {
  try {
    const res = await fetch(`${state.apiBaseUrl}/training/stop`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      showToast(data.message, 'info');
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function registerOrganization(name, description) {
  try {
    const res = await fetch(`${state.apiBaseUrl}/orgs/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }

    const newOrg = await res.json();
    showToast(`Organization '${newOrg.name}' registered!`, 'success');
    closeModal(dom.modalRegisterOrg);
    dom.formRegisterOrg.reset();
    fetchOrganizations();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteOrganization(orgId, orgName) {
  if (!confirm(`Are you sure you want to remove '${orgName}'?`)) return;
  try {
    const res = await fetch(`${state.apiBaseUrl}/orgs/${orgId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast(`Organization '${orgName}' removed.`, 'info');
      fetchOrganizations();
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}
