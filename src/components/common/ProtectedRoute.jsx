import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { AccessDenied } from '../screens/AccessDenied';

/**
 * Route protection guard for official administrative desks.
 * Completely conceals restricted pages and data from public citizens and unauthenticated guests.
 */
export const ProtectedRoute = ({ children, requireOfficial = true, deskTitle }) => {
  const { isOfficial, isLoading } = useAuth();

  // If still loading session from storage, display minimal non-blocking container
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  // Enforce official clearance
  if (requireOfficial && !isOfficial) {
    return <AccessDenied deskTitle={deskTitle} />;
  }

  return children;
};
