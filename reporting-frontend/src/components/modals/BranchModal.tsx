// components/modals/BranchModal.tsx
'use client';

import { useState } from 'react';
import { Branch } from '@/types';

interface BranchModalProps {
  branch?: Branch | null;
  onSubmit: (branchData: Partial<Branch>) => void;
  onClose: () => void;
  isLoading: boolean;
}

export default function BranchModal({ branch, onSubmit, onClose, isLoading }: BranchModalProps) {
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
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
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