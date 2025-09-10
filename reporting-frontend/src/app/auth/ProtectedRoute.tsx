'use client';
import { useAuth } from '@/contexts/AuthContext';  
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  anyPermission?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({children,requiredPermissions = [],anyPermission = [],}) => {
  const { user, isLoading, hasPermission, hasAnyPermission } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/auth/login');
        return;
      }

      // Check required permissions
      if (requiredPermissions.length > 0 && !requiredPermissions.every(hasPermission)) {
        router.push('/unauthorized');
        return;
      }

      // Check any permission
      if (anyPermission.length > 0 && !hasAnyPermission(anyPermission)) {
        router.push('/unauthorized');
        return;
      }
    }
  }, [user, isLoading, router, requiredPermissions, anyPermission, hasPermission, hasAnyPermission]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
};