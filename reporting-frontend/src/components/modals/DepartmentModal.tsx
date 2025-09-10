// components/modals/DepartmentModal.tsx
'use client';

import { useState } from 'react';
import { Department, Branch } from '@/types';
import { useBranches } from '@/lib/api-hooks';

interface DepartmentModalProps {
  department?: Department | null;
  onSubmit: (departmentData: Partial<Department>) => void;
  onClose: () => void;
  isLoading: boolean;
}

export default function DepartmentModal({ department, onSubmit, onClose, isLoading }: DepartmentModalProps) {
  const [departmentCode, setDepartmentCode] = useState(department?.departmentCode || '');
  const [departmentName, setDepartmentName] = useState(department?.departmentName || '');
  const [branchCode, setBranchCode] = useState(
    typeof department?.branch === 'string'
      ? department.branch
      : typeof department?.branch === 'object' && department.branch !== null
        ? department.branch.branchCode
        : ''
  );

  const { data: branches } = useBranches();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      departmentCode,
      departmentName,
      branch: branchCode,
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
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
              {branches?.map((branch) => (
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