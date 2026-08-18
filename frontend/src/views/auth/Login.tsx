import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Building2, User as UserIcon, ArrowRight, Lock } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { UserRole } from '../../types/user';

export const Login: React.FC = () => {
  const { loginAs } = useAuthStore();
  const navigate = useNavigate();

  const handleSelectRole = (role: UserRole) => {
    loginAs(role);
    if (role === 'admin') {
      navigate('/admin');
    } else if (role === 'org_admin') {
      navigate('/org/1');
    } else {
      navigate('/chat');
    }
  };

  const roles = [
    {
      key: 'admin',
      userKey: 'admin',
      role: 'admin' as UserRole,
      icon: <Shield className="w-5 h-5 text-blue-600" />,
      iconBg: 'bg-blue-50 border-blue-100',
      badge: 'Platform Owner',
      badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
      title: 'Global Admin Console',
      name: 'Dr. Ananya Sharma',
      desc: 'Coordinate federated training rounds, view convergence curves, review differential privacy budgets, and inspect hospital silo nodes.',
    },
    {
      key: 'org_admin',
      userKey: 'org_admin_alpha',
      role: 'org_admin' as UserRole,
      icon: <Building2 className="w-5 h-5 text-violet-600" />,
      iconBg: 'bg-violet-50 border-violet-100',
      badge: 'Hospital Silo Lead',
      badgeColor: 'bg-violet-50 text-violet-700 border-violet-200',
      title: 'Organization Portal',
      name: 'Dr. Rajesh Varma',
      desc: 'AIIMS New Delhi cardiology node. View local client hardware telemetry, local datasets, and manage staff AI permissions.',
    },
    {
      key: 'end_user',
      userKey: 'end_user_granted',
      role: 'end_user' as UserRole,
      icon: <UserIcon className="w-5 h-5 text-emerald-600" />,
      iconBg: 'bg-emerald-50 border-emerald-100',
      badge: 'Clinical Practitioner',
      badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      title: 'Clinical AI Assistant',
      name: 'Dr. Priya Nair',
      desc: 'Query the global trained federated model for clinical evaluations with zero exposure to raw training records.',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4 font-sans text-slate-900">
      <div className="max-w-4xl w-full">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 text-blue-600 mb-3 shadow-sm">
            <Shield size={24} />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
            Federated Shield
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-lg mx-auto">
            Privacy-Preserving Federated Learning & Clinical Intelligence Platform
          </p>
        </div>

        {/* 3 Role Persona Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {roles.map((item) => (
            <div
              key={item.key}
              onClick={() => handleSelectRole(item.role)}
              className="bg-white border border-slate-200 hover:border-slate-300 rounded-xl p-5 cursor-pointer shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3.5">
                  <div className={`w-9 h-9 rounded-lg ${item.iconBg} border flex items-center justify-center`}>
                    {item.icon}
                  </div>
                  <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                </div>

                <h2 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {item.title}
                </h2>
                <div className="text-xs font-semibold text-slate-700 mt-0.5 mb-2">
                  {item.name}
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {item.desc}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-600">
                <span>Enter Workspace</span>
                <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>

        {/* Security Footer Note */}
        <div className="mt-8 text-center text-xs text-slate-500 flex items-center justify-center gap-1.5">
          <Lock size={13} className="text-emerald-600" />
          <span>Differential Privacy & Secure Multi-Party Aggregation Active</span>
        </div>
      </div>
    </div>
  );
};
