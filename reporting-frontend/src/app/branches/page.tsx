// app/branches/page.tsx
'use client';

import { useState } from 'react';
import { ProtectedRoute } from '@/app/auth/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useBranches, useCreateBranch, useUpdateBranch, useDeleteBranch } from '@/lib/api-hooks';
import { Branch } from '@/types';

export default function BranchesPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null);

  const { data: branches, isLoading, error, refetch } = useBranches();
  const createBranchMutation = useCreateBranch();
  const updateBranchMutation = useUpdateBranch();
  const deleteBranchMutation = useDeleteBranch();

  const handleCreateBranch = (branchData: Partial<Branch>) => {
    createBranchMutation.mutate(branchData, {
      onSuccess: () => {
        refetch();
        setIsCreateModalOpen(false);
      },
    });
  };

  const handleUpdateBranch = (branchData: Partial<Branch>) => {
    if (editingBranch) {
      updateBranchMutation.mutate(
        { id: editingBranch.branchCode, ...branchData },
        {
          onSuccess: () => {
            refetch();
            setEditingBranch(null);
          },
        }
      );
    }
  };

  const handleDeleteBranch = (id: string) => {
    if (confirm('Are you sure you want to delete this branch?')) {
      deleteBranchMutation.mutate(id, {
        onSuccess: () => {
          refetch();
        },
      });
    }
  };

  const handleEdit = (branch: Branch) => {
    setEditingBranch(branch);
  };

  return (
    <ProtectedRoute requiredPermissions={['userManagement.view_branch']}>
      <DashboardLayout>
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Branch Management</h2>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Branch
          </button>
        </div>

        {isLoading && (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading branches...</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            Error loading branches: {(error as Error).message}
          </div>
        )}

        {branches && (
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
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {branches.map((branch) => (
                  <tr key={branch.branchCode}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {branch.branchCode}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {branch.branchName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleEdit(branch)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteBranch(branch.branchCode)}
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

        {/* Create/Edit Branch Modal */}
        {(isCreateModalOpen || editingBranch) && (
          <BranchModal
            branch={editingBranch}
            onSubmit={editingBranch ? handleUpdateBranch : handleCreateBranch}
            onClose={() => {
              setIsCreateModalOpen(false);
              setEditingBranch(null);
            }}
            isLoading={createBranchMutation.isPending || updateBranchMutation.isPending}
          />
        )}
      </DashboardLayout>
    </ProtectedRoute>
  );
}

function BranchModal({ branch, onSubmit, onClose, isLoading }: {
  branch?: Branch | null;
  onSubmit: (branchData: Partial<Branch>) => void;
  onClose: () => void;
  isLoading: boolean;
}) {
  const [branchCode, setBranchCode] = useState(branch?.branchCode || '');
  const [branchName, setBranchName] = useState(branch?.branchName || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      branchCode,
      branchName,
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {branch ? 'Edit Branch' : 'Create New Branch'}
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Branch Code</label>
            <input
              type="text"
              required
              value={branchCode}
              onChange={(e) => setBranchCode(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              disabled={!!branch} // Disable editing for existing branches
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Branch Name</label>
            <input
              type="text"
              required
              value={branchName}
              onChange={(e) => setBranchName(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
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
              {isLoading ? 'Saving...' : branch ? 'Update Branch' : 'Create Branch'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}