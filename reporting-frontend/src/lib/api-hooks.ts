// lib/api-hooks.ts
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  User, 
  Role, 
  AppPermission, 
  AccountBase, 
  LoginCredentials, 
  AuthResponse, 
  Branch,
  Department
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

// Helper function to handle API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth hooks
export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation<AuthResponse, Error, LoginCredentials>({
    mutationFn: (credentials) =>
      apiCall<AuthResponse>('/user-management/auth/login/', {
        method: 'POST',
        body: JSON.stringify(credentials),
      }),
    onSuccess: (data) => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
      }
      queryClient.setQueryData(['currentUser'], data.user);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
      if (refreshToken) {
        await apiCall('/user-management/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh: refreshToken }),
        });
      }
    },
    onSuccess: () => {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
      queryClient.setQueryData(['currentUser'], null);
      queryClient.clear();
    },
  });
}

export function useCurrentUser() {
  return useQuery<User | null>({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) return null;

      try {
        return await apiCall<User>('/user-management/auth/me/');
      } catch (error) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
        }
        return null;
      }
    },
    initialData: () => {
      if (typeof window !== 'undefined') {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
      }
      return null;
    },
  });
}

// User management hooks
export function useUsers() {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: () => apiCall<User[]>('/user-management/users/'),
    enabled: false, // Don't fetch automatically
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation<User, Error, Partial<User>>({
    mutationFn: (userData) =>
      apiCall<User>('/user-management/users/', {
        method: 'POST',
        body: JSON.stringify(userData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, string>({
    mutationFn: (userId) =>
      apiCall<void>(`/user-management/users/${userId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// Reports hooks
export function useAccountBase(params?: any) {
  return useQuery<AccountBase[]>({
    queryKey: ['accountBase', params],
    queryFn: () => apiCall<AccountBase[]>('/reports/account-base/', {
      method: 'GET',
    }),
  });
}

export function useAccountBaseStats() {
  return useQuery({
    queryKey: ['accountBaseStats'],
    queryFn: () => apiCall('/reports/account-base/stats/'),
  });
}

export function useExportAccountBase() {
  return useMutation<Blob, Error, any>({
    mutationFn: async (params) => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers: HeadersInit = {};
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/reports/account-base/export/?${new URLSearchParams(params)}`, {
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.blob();
    },
  });
}

// Roles and permissions hooks

export function usePermissions() {
  return useQuery<AppPermission[]>({
    queryKey: ['permissions'],
    queryFn: () => apiCall<AppPermission[]>('/user-management/permissions/'),
  });
}
// Add to lib/api-hooks.ts

// Roles hooks
export function useRoles() {
  return useQuery<Role[]>({
    queryKey: ['roles'],
    queryFn: () => apiCall<Role[]>('/user-management/roles/'),
  });
}

export function useCreateRole() {
  const queryClient = useQueryClient();
  
  return useMutation<Role, Error, Partial<Role>>({
    mutationFn: (roleData) =>
      apiCall<Role>('/user-management/roles/', {
        method: 'POST',
        body: JSON.stringify(roleData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

export function useUpdateRole() {
  const queryClient = useQueryClient();
  
  return useMutation<Role, Error, { id: string } & Partial<Role>>({
    mutationFn: ({ id, ...roleData }) =>
      apiCall<Role>(`/user-management/roles/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(roleData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

export function useDeleteRole() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, string>({
    mutationFn: (roleId) =>
      apiCall<void>(`/user-management/roles/${roleId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

// Branches hooks
export function useBranches() {
  return useQuery<Branch[]>({
    queryKey: ['branches'],
    queryFn: () => apiCall<Branch[]>('/auth/branches/'),
  });
}

export function useCreateBranch() {
  const queryClient = useQueryClient();
  
  return useMutation<Branch, Error, Partial<Branch>>({
    mutationFn: (branchData) =>
      apiCall<Branch>('/auth/branches/', {
        method: 'POST',
        body: JSON.stringify(branchData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['branches'] });
    },
  });
}

export function useUpdateBranch() {
  const queryClient = useQueryClient();
  
  return useMutation<Branch, Error, { id: string } & Partial<Branch>>({
    mutationFn: ({ id, ...branchData }) =>
      apiCall<Branch>(`/auth/branches/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(branchData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['branches'] });
    },
  });
}

export function useDeleteBranch() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, string>({
    mutationFn: (branchId) =>
      apiCall<void>(`/auth/branches/${branchId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['branches'] });
    },
  });
}

// Departments hooks
export function useDepartments() {
  return useQuery<Department[]>({
    queryKey: ['departments'],
    queryFn: () => apiCall<Department[]>('/auth/departments/'),
  });
}

export function useCreateDepartment() {
  const queryClient = useQueryClient();
  
  return useMutation<Department, Error, Partial<Department>>({
    mutationFn: (departmentData) =>
      apiCall<Department>('/auth/departments/', {
        method: 'POST',
        body: JSON.stringify(departmentData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}

export function useUpdateDepartment() {
  const queryClient = useQueryClient();
  
  return useMutation<Department, Error, { id: string } & Partial<Department>>({
    mutationFn: ({ id, ...departmentData }) =>
      apiCall<Department>(`/auth/departments/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(departmentData),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}

export function useDeleteDepartment() {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, string>({
    mutationFn: (departmentId) =>
      apiCall<void>(`/auth/departments/${departmentId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });
}
export const useUpdateUser = () =>
  useMutation<any, Error, { id: string; [key: string]: any }>({
    mutationFn: ({ id, ...data }) =>
      apiCall(`/api/auth/users/${id}/`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
  });
