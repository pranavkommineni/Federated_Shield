import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore, MOCK_USERS } from '../../store/useAuthStore';
import { UserRole } from '../../types/user';

export const Login: React.FC = () => {
  const { loginAs } = useAuthStore();
  const navigate = useNavigate();

  const handleSelectRole = (role: UserRole, userKey?: string) => {
    if (userKey && MOCK_USERS[userKey]) {
      loginAs(role, MOCK_USERS[userKey]);
    } else {
      loginAs(role);
    }
    if (role === 'admin') navigate('/admin');
    else if (role === 'org_admin') navigate('/org/1');
    else navigate('/chat');
  };

  const roles = [
    {
      key: 'admin',
      userKey: 'admin',
      role: 'admin' as UserRole,
      emoji: '👑',
      label: 'Platform Admin',
      title: 'Global Admin',
      name: 'Dr. Evelyn Vance',
      desc: 'Full platform visibility. Start/stop FL rounds, live convergence charts, privacy ε budget audit across all hospital silos.',
      color: '#00f2fe',
      border: 'rgba(0, 242, 254, 0.4)',
      bg: 'rgba(0, 242, 254, 0.07)',
    },
    {
      key: 'org_admin',
      userKey: 'org_admin_alpha',
      role: 'org_admin' as UserRole,
      emoji: '🏥',
      label: 'Hospital Silo Lead',
      title: 'Organization Admin',
      name: 'Dr. Rajesh Varma',
      desc: 'Manage Hospital Alpha edge devices, local DP calibration, and grant/revoke AI chat access for clinical staff.',
      color: '#a855f7',
      border: 'rgba(168, 85, 247, 0.4)',
      bg: 'rgba(168, 85, 247, 0.07)',
    },
    {
      key: 'end_user',
      userKey: 'end_user_granted',
      role: 'end_user' as UserRole,
      emoji: '💬',
      label: 'Clinical Practitioner',
      title: 'End-User / Clinician',
      name: 'Dr. Sarah Connor',
      desc: 'Query the global federated AI model via private conversational interface. Zero visibility into training internals.',
      color: '#34d399',
      border: 'rgba(52, 211, 153, 0.4)',
      bg: 'rgba(52, 211, 153, 0.07)',
    },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#070b14',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
      fontFamily: "'Inter', system-ui, sans-serif",
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background glow orbs */}
      <div style={{ position: 'absolute', top: '20%', left: '15%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,242,254,0.06) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: '20%', right: '15%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)', pointerEvents: 'none' }} />

      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 48, position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(0,242,254,0.08)', border: '1px solid rgba(0,242,254,0.2)', padding: '6px 16px', borderRadius: 999, color: '#00f2fe', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 20 }}>
          🛡️ Smart India Hackathon (SIH) 2026 Prototype
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, marginBottom: 12 }}>
          <div style={{ width: 52, height: 52, borderRadius: 16, background: 'linear-gradient(135deg, #00f2fe, #a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 26, boxShadow: '0 0 24px rgba(0,242,254,0.3)' }}>
            🛡️
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 900, margin: 0, color: '#f8fafc', letterSpacing: '-0.03em' }}>
            FEDERATED<span style={{ color: '#00f2fe' }}>SHIELD</span>
          </h1>
        </div>

        <p style={{ color: '#64748b', fontSize: 14, maxWidth: 520, margin: '0 auto', lineHeight: 1.6 }}>
          Privacy-Preserving Federated Learning Platform with Differential Privacy, Secure Multi-Party Aggregation, and Role-Based Healthcare Governance.
        </p>
      </div>

      {/* Role Cards */}
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 1100, width: '100%', position: 'relative', zIndex: 1 }}>
        {roles.map((r) => (
          <div
            key={r.key}
            onClick={() => handleSelectRole(r.role, r.userKey)}
            style={{
              flex: '1 1 300px',
              maxWidth: 340,
              background: '#121a2e',
              border: `1px solid rgba(255,255,255,0.08)`,
              borderRadius: 20,
              padding: '28px 24px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLDivElement).style.border = `1px solid ${r.border}`;
              (e.currentTarget as HTMLDivElement).style.background = r.bg;
              (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-4px)';
              (e.currentTarget as HTMLDivElement).style.boxShadow = `0 8px 32px ${r.border}`;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLDivElement).style.border = '1px solid rgba(255,255,255,0.08)';
              (e.currentTarget as HTMLDivElement).style.background = '#121a2e';
              (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
              (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
            }}
          >
            <div>
              <div style={{ width: 52, height: 52, borderRadius: 14, background: `${r.bg}`, border: `1px solid ${r.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, marginBottom: 16 }}>
                {r.emoji}
              </div>
              <div style={{ fontSize: 10, fontWeight: 700, color: r.color, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>
                {r.label}
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 800, color: '#f8fafc', margin: '0 0 10px 0' }}>
                {r.title}
              </h3>
              <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.6, margin: '0 0 20px 0' }}>
                {r.desc}
              </p>
            </div>
            <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: r.color }}>
                Login as {r.name}
              </span>
              <span style={{ color: r.color, fontSize: 18 }}>→</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 40, fontSize: 12, color: '#334155', textAlign: 'center' }}>
        Demo Mode • Click any role card above to test that perspective end-to-end
      </div>
    </div>
  );
};
