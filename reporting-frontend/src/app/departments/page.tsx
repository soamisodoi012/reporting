// app/departments/page.tsx
'use client';

import { useState } from 'react';
import { ProtectedRoute } from '@/app/auth/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useDepartments, useCreateDepartment, useUpdateDepartment, useDeleteDepartment, useBranches } from '@/lib/api-hooks';
import { Department, Branch } from '@/types';

export default function DepartmentsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState<Department | null>(null);

  const { data: departments, isLoading, error, refetch } = useDepartments();
  const { data: branches } = useBranches();
  const createDepartmentMutation = useCreateDepartment();
  const updateDepartmentMutation = useUpdateDepartment();
  const deleteDepartmentMutation = useDeleteDepartment();

  const handleCreateDepartment = (departmentData: Partial<Department>) => {
    createDepartmentMutation.mutate(departmentData, {
      onSuccess: () => {
        refetch();
        setIsCreateModalOpen(false);
      },
    });
  };

  const handleUpdateDepartment = (departmentData: Partial<Department>) => {
    if (editingDepartment) {
      updateDepartmentMutation.mutate(
        { id: editingDepartment.departmentCode, ...departmentData },
        {
          onSuccess: () => {
            refetch();
            setEditingDepartment(null);
          },
        }
      );
    }
  };

  const handleDeleteDepartment = (id: string) => {
    if (confirm('Are you sure you want to delete this department?')) {
      deleteDepartmentMutation.mutate(id, {
        onSuccess: () => {
          refetch();
        },
      });
    }
  };

  const handleEdit = (department: Department) => {
    setEditingDepartment(department);
  };

  return (
    <ProtectedRoute requiredPermissions={['userManagement.view_department']}>
      <DashboardLayout>
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Department Management</h2>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Department
          </button>
        </div>

        {isLoading && (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading departments...</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            Error loading departments: {(error as Error).message}
          </div>
        )}

        {departments && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Branch
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {departments.map((department) => (
                  <tr key={department.departmentCode}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {department.departmentCode}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {department.departmentName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {typeof department.branch === 'object' && department.branch !== null
                        ? department.branch.branchName
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleEdit(department)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteDepartment(department.departmentCode)}
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

        {/* Create/Edit Department Modal */}
        {(isCreateModalOpen || editingDepartment) && (
          <DepartmentModal
            department={editingDepartment}
            branches={branches || []}
            onSubmit={editingDepartment ? handleUpdateDepartment : handleCreateDepartment}
            onClose={() => {
              setIsCreateModalOpen(false);
              setEditingDepartment(null);
            }}
            isLoading={createDepartmentMutation.isPending || updateDepartmentMutation.isPending}
          />
        )}
      </DashboardLayout>
    </ProtectedRoute>
  );
}

function DepartmentModal({ department, branches, onSubmit, onClose, isLoading }: {
  department?: Department | null;
  branches: Branch[];
  onSubmit: (departmentData: Partial<Department>) => void;
  onClose: () => void;
  isLoading: boolean;
}) {
  const [departmentCode, setDepartmentCode] = useState(department?.departmentCode || '');
  const [departmentName, setDepartmentName] = useState(department?.departmentName || '');
  const [branchCode, setBranchCode] = useState(
    typeof department?.branch === 'object' && department?.branch !== null
      ? department.branch.branchCode
      : ''
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      departmentCode,
      departmentName,
      branch: branchCode,
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {department ? 'Edit Department' : 'Create New Department'}
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Department Code</label>
            <input
              type="text"
              required
              value={departmentCode}
              onChange={(e) => setDepartmentCode(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              disabled={!!department} // Disable editing for existing departments
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Department Name</label>
            <input
              type="text"
              required
              value={departmentName}
              onChange={(e) => setDepartmentName(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Branch</label>
            <select
              value={branchCode}
              onChange={(e) => setBranchCode(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            >
              <option value="">Select a branch</option>
              {branches.map((branch) => (
                <option key={branch.branchCode} value={branch.branchCode}>
                  {branch.branchName}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : department ? 'Update Department' : 'Create Department'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}