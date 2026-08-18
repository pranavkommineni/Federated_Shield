# 🛡️ Federated Shield — React + TypeScript + Vite Dashboard

A multi-role Privacy-Preserving Federated Learning web platform built with **React 18**, **TypeScript**, **Vite**, **TailwindCSS**, **Zustand**, and **Recharts**.

---

## 🎭 3 Role-Based Scoped Views

1. **👑 ADMIN VIEW (`/admin`, `/admin/orgs/:orgId`)**
   - See all connected healthcare organizations & client devices.
   - Global model convergence live area chart across training rounds (accuracy % & loss).
   - Differential privacy telemetry ($\epsilon$ budget spent) and "Server Never Saw Raw Updates" indicator.
   - Start / Stop federated training rounds.
   - Click into any organization to inspect device and privacy details.

2. **🏥 ORGANIZATION VIEW (`/org/:orgId`, `/org/:orgId/users`)**
   - Scoped strictly to that hospital's data silo.
   - Live hardware telemetry of local edge devices (CPU %, Memory MB, IP).
   - Contribution metrics: local accuracy, loss, and rounds participated.
   - Manage end-users: invite clinicians and toggle AI chat access permissions (`hasChatAccess`).

3. **💬 END-USER VIEW (`/chat`)**
   - Clean conversational chat interface with the global federated AI model.
   - Gated by organization permissions — restricted if org admin revokes access.
   - Zero visibility into other organizations or training internals.

---

## 📂 File Structure

```
frontend/
├── index.html                   # HTML template
├── package.json                 # Dependencies & scripts
├── tsconfig.json                # TypeScript configuration
├── vite.config.ts               # Vite configuration (port 5173)
├── tailwind.config.js           # Tailwind dark theme & neon colors
├── src/
│   ├── main.tsx                 # React DOM mount
│   ├── App.tsx                  # Router with RoleRouteGuard
│   ├── api/
│   │   ├── client.ts            # Axios instance (base URL: http://localhost:8000)
│   │   ├── orgs.ts              # Org and user management API calls
│   │   ├── training.ts          # Start/stop and round history API calls
│   │   └── chat.ts              # AI chat inference calls
│   ├── store/
│   │   └── useAuthStore.ts      # Zustand auth state & mock personas
│   ├── types/
│   │   ├── org.ts               # Organization & device types
│   │   ├── user.ts              # User & role types
│   │   └── training.ts          # Metrics & WebSocket types
│   ├── hooks/
│   │   └── useMetricsSocket.ts  # Native WebSocket hook (ws://localhost:8000/ws/metrics)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AdminLayout.tsx  # Admin sidebar & header
│   │   │   ├── OrgLayout.tsx    # Org admin sidebar & header
│   │   │   └── ChatLayout.tsx   # End-user chat header
│   │   ├── charts/
│   │   │   └── AccuracyChart.tsx # Recharts area/line convergence chart
│   │   ├── shared/
│   │   │   ├── StatusBadge.tsx  # Glowing status badge
│   │   │   └── Card.tsx         # Glassmorphic card container
│   │   └── chat/
│   │       ├── ChatWindow.tsx   # Interactive chat box
│   │       └── MessageBubble.tsx # Message bubble with DP zk-proof badge
│   ├── views/
│   │   ├── admin/
│   │   │   ├── AdminDashboard.tsx
│   │   │   └── OrgDetail.tsx
│   │   ├── org/
│   │   │   ├── OrgDashboard.tsx
│   │   │   └── ManageUsers.tsx
│   │   ├── chat/
│   │   │   └── UserChat.tsx
│   │   └── auth/
│   │       └── Login.tsx        # 1-Click mock persona selector
│   ├── routes/
│   │   └── routeGuards.tsx      # RoleRouteGuard protection
│   └── styles/
│       └── index.css            # Tailwind directives
└── README.md
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd c:\Users\Asus\Desktop\FedAi-SIH\Federated_Shield\frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🔌 Where to Wire Up Real Backend API Calls

All network interactions are cleanly isolated in the `src/api/` folder:

| Module | File | Method / Endpoint |
|---|---|---|
| **Organizations** | `src/api/orgs.ts` | `GET /orgs`, `POST /orgs/register`, `GET /nodes/{id}/telemetry` |
| **Users & Permissions** | `src/api/orgs.ts` | `GET /users?org_id={id}`, `POST /users/register` |
| **Training Lifecycle** | `src/api/training.ts` | `POST /training/start`, `POST /training/stop`, `GET /training/status` |
| **Live Telemetry** | `src/hooks/useMetricsSocket.ts` | `ws://localhost:8000/ws/metrics` |
| **AI Inference** | `src/api/chat.ts` | `POST /inference/predict` |
