// app/roles/page.tsx
'use client';

import { useState } from 'react';
import { ProtectedRoute } from '@/app/auth/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import RoleModal from '@/components/modals/RoleModal';
import { useRoles, useCreateRole, useUpdateRole, useDeleteRole } from '@/lib/api-hooks';
import { Role } from '@/types';

export default function RolesPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);

  const { data: roles, isLoading, error, refetch } = useRoles();
  const createRoleMutation = useCreateRole();
  const updateRoleMutation = useUpdateRole();
  const deleteRoleMutation = useDeleteRole();

  const handleCreateRole = (roleData: Partial<Role>) => {
    createRoleMutation.mutate(roleData, {
      onSuccess: () => {
        refetch();
        setIsCreateModalOpen(false);
      },
    });
  };

  const handleUpdateRole = (roleData: Partial<Role>) => {
    if (editingRole) {
      updateRoleMutation.mutate(
        { id: editingRole.id, ...roleData },
        {
          onSuccess: () => {
            refetch();
            setEditingRole(null);
          },
        }
      );
    }
  };

  const handleDeleteRole = (id: string) => {
    if (confirm('Are you sure you want to delete this role?')) {
      deleteRoleMutation.mutate(id, {
        onSuccess: () => {
          refetch();
        },
      });
    }
  };

  const handleEdit = (role: Role) => {
    setEditingRole(role);
  };

  return (
    <ProtectedRoute requiredPermissions={['userManagement.view_role']}>
      <DashboardLayout>
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Role Management</h2>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Role
          </button>
        </div>

        {isLoading && (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading roles...</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            Error loading roles: {(error as Error).message}
          </div>
        )}

        {roles && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Permissions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {roles.map((role) => (
                  <tr key={role.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {role.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {role.description}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="flex flex-wrap gap-1">
                        {role.permissions.slice(0, 3).map((permission) => (
                          <span
                            key={permission.id}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {permission.name}
                          </span>
                        ))}
                        {role.permissions.length > 3 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded">
                            +{role.permissions.length - 3} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleEdit(role)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteRole(role.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {(isCreateModalOpen || editingRole) && (
          <RoleModal
            role={editingRole}
            onSubmit={editingRole ? handleUpdateRole : handleCreateRole}
            onClose={() => {
              setIsCreateModalOpen(false);
              setEditingRole(null);
            }}
            isLoading={createRoleMutation.isPending || updateRoleMutation.isPending}
          />
        )}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
