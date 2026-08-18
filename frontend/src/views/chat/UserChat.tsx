import React from 'react';
import { ChatWindow } from '../../components/chat/ChatWindow';
import { useAuthStore } from '../../store/useAuthStore';

export const UserChat: React.FC = () => {
  const { currentUser } = useAuthStore();

  const hasAccess = currentUser?.hasChatAccess ?? true;
  const orgName = currentUser?.orgName || 'AIIMS New Delhi (Cardiology)';
  const userName = currentUser?.fullName || 'Dr. Priya Nair';

  return (
    <div className="w-full">
      <ChatWindow orgName={orgName} userName={userName} hasAccess={hasAccess} />
    </div>
  );
};
