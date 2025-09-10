
'use client';

import { useState } from 'react';
import { ProtectedRoute } from '@/app/auth/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';

// Simple client component for reports
function ReportsContent() {
  const [filters, setFilters] = useState({
    branch_code: '',
    branch_name: '',
    category: '',
    min_balance: '',
  });

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Account Base Reports</h2>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <h3 className="text-lg font-medium mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Branch Code</label>
            <input
              type="text"
              value={filters.branch_code}
              onChange={(e) => handleFilterChange('branch_code', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Branch Name</label>
            <input
              type="text"
              value={filters.branch_name}
              onChange={(e) => handleFilterChange('branch_name', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <input
              type="text"
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Min Balance</label>
            <input
              type="number"
              value={filters.min_balance}
              onChange={(e) => handleFilterChange('min_balance', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Results placeholder */}
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p className="text-gray-600">Reports will be loaded here</p>
      </div>
    </div>
  );
}

// Main page component
export default function ReportsPage() {
  return (
    <ProtectedRoute 
      requiredPermissions={['userManagement.view_accountbase', 'userManagement.view_reports']}
      anyPermission={['userManagement.view_accountbase', 'userManagement.view_reports']}
    >
      <DashboardLayout>
        <ReportsContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}