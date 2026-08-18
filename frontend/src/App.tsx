import React, { Component, ErrorInfo, ReactNode } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './views/auth/Login';
import { AdminLayout } from './components/layout/AdminLayout';
import { AdminDashboard } from './views/admin/AdminDashboard';
import { OrgDetail } from './views/admin/OrgDetail';
import { OrgLayout } from './components/layout/OrgLayout';
import { OrgDashboard } from './views/org/OrgDashboard';
import { ManageUsers } from './views/org/ManageUsers';
import { ChatLayout } from './components/layout/ChatLayout';
import { UserChat } from './views/chat/UserChat';
import { RoleRouteGuard } from './routes/routeGuards';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class AppErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in App:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{
          backgroundColor: '#f8fafc',
          color: '#dc2626',
          padding: '40px',
          fontFamily: 'system-ui, sans-serif',
          minHeight: '100vh',
        }}>
          <h2 style={{ color: '#0f172a', fontSize: '20px', fontWeight: 'bold', marginBottom: '12px' }}>
            Federated Shield UI Notice
          </h2>
          <p style={{ color: '#475569', fontSize: '14px', marginBottom: '12px' }}>
            {this.state.error?.message}
          </p>
          <pre style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            padding: '16px',
            borderRadius: '8px',
            color: '#64748b',
            overflowX: 'auto',
            fontSize: '12px',
          }}>
            {this.state.error?.stack}
          </pre>
          <button
            onClick={() => window.location.href = '/login'}
            style={{
              marginTop: '20px',
              backgroundColor: '#2563eb',
              color: '#ffffff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            Return to Login
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export function App() {
  return (
    <AppErrorBoundary>
      <BrowserRouter>
        <Routes>
          {/* Public Login Route */}
          <Route path="/login" element={<Login />} />

          {/* 1. Global Admin Protected Routes */}
          <Route element={<RoleRouteGuard allowedRoles={['admin']} />}>
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<AdminDashboard />} />
              <Route path="orgs/:orgId" element={<OrgDetail />} />
            </Route>
          </Route>

          {/* 2. Org Admin Protected Routes */}
          <Route element={<RoleRouteGuard allowedRoles={['org_admin']} />}>
            <Route path="/org/:orgId" element={<OrgLayout />}>
              <Route index element={<OrgDashboard />} />
              <Route path="users" element={<ManageUsers />} />
            </Route>
          </Route>

          {/* 3. End-User AI Chat Protected Routes */}
          <Route element={<RoleRouteGuard allowedRoles={['end_user']} />}>
            <Route path="/chat" element={<ChatLayout />}>
              <Route index element={<UserChat />} />
            </Route>
          </Route>

          {/* Default redirect to /login */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AppErrorBoundary>
  );
}

export default App;
