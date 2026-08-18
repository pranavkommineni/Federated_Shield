import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole } from '../types/user';

interface RoleRouteGuardProps {
  allowedRoles: UserRole[];
}

export const RoleRouteGuard: React.FC<RoleRouteGuardProps> = ({ allowedRoles }) => {
  const { currentUser, isAuthenticated } = useAuthStore();

  if (!isAuthenticated || !currentUser) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(currentUser.role)) {
    // Redirect to the user's appropriate home view
    if (currentUser.role === 'admin') {
      return <Navigate to="/admin" replace />;
    } else if (currentUser.role === 'org_admin') {
      return <Navigate to={`/org/${currentUser.orgId || 1}`} replace />;
    } else if (currentUser.role === 'end_user') {
      return <Navigate to="/chat" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
