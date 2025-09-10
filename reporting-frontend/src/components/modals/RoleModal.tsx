// components/modals/RoleModal.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { Role, AppPermission } from '@/types';
import { usePermissions } from '@/lib/api-hooks';

interface RoleModalProps {
  role?: Role | null;
  onSubmit: (roleData: Partial<Role>) => void;
  onClose: () => void;
  isLoading?: boolean;
}

export default function RoleModal({ role, onSubmit, onClose, isLoading }: RoleModalProps) {
  const [name, setName] = useState(role?.name || '');
  const [description, setDescription] = useState(role?.description || '');
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>(
    role?.permissions.map(p => p.id) || []
  );

  const { data: permissions } = usePermissions();

  // Group permissions by module prefix
  const groupedPermissions = permissions?.reduce((acc, perm) => {
    const module = perm.codename.split('.')[0] || 'Other';
    if (!acc[module]) acc[module] = [];
    acc[module].push(perm);
    return acc;
  }, {} as Record<string, AppPermission[]>) || {};

  const togglePermission = (id: string) => {
    setSelectedPermissions(prev =>
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ name, description, permissions: permissions?.filter(p => selectedPermissions.includes(p.id)) || [] });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-11/12 max-w-2xl p-6">
        <h2 className="text-xl font-bold mb-4">{role ? 'Edit Role' : 'Create Role'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Role Name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full border px-3 py-2 rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full border px-3 py-2 rounded"
            />
          </div>
          <div className="mb-4 max-h-60 overflow-y-auto border rounded p-2">
            {Object.entries(groupedPermissions).map(([module, perms]) => (
              <div key={module} className="mb-2">
                <h3 className="font-semibold text-sm mb-1">{module}</h3>
                <div className="flex flex-wrap gap-2">
                  {perms.map(p => (
                    <label key={p.id} className="text-xs bg-gray-100 px-2 py-1 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedPermissions.includes(p.id)}
                        onChange={() => togglePermission(p.id)}
                        className="mr-1"
                      />
                      {p.name}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-3 mt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
