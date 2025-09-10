// types/index.ts
// In types/index.ts
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  role?: string | Role; // Can be role ID or Role object
  role_name?: string;
  branch?: string | Branch; // Can be branch code or Branch object
  branch_name?: string;
  permissions: string[];
  date_joined: string;
  last_login: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: AppPermission[];
}

export interface AppPermission {
  id: string;
  name: string;
  codename: string;
  description: string;
  created_at: string;
  updated_at: string;
}

// Add Branch interface
export interface Branch {
  branchCode: string;
  branchName: string;
  user?: string | User; // Can be either user ID or User object
  user_details?: { // Optional user details if expanded
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

// Add Department interface
export interface Department {
  departmentCode: string;
  departmentName: string;
  branch: string | Branch; // Can be either branch code or Branch object
  branch_details?: { // Optional branch details if expanded
    branchCode: string;
    branchName: string;
  };
}

export interface AccountBase {
  account_number: string;
  customer_no: string;
  customer_name: string;
  phone_number: string;
  category: string;
  product_name: string;
  sector: string;
  sector_name: string;
  industry: string;
  industry_name: string;
  currency: string;
  working_balance: number;
  opening_date: string;
  branch_code: string;
  branch_name: string;
  region: string;
  ultimate_ben: string;
  cust_type: string;
  report_date: string;
  report_time: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  refresh: string;
  access: string;
  user: User;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// Add types for API responses
export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Add types for form data
export interface CreateRoleData {
  name: string;
  description: string;
  permission_ids?: string[];
}

export interface UpdateRoleData extends Partial<CreateRoleData> {
  id: string;
}

export interface CreateBranchData {
  branchCode: string;
  branchName: string;
  user?: string;
}

export interface UpdateBranchData extends Partial<CreateBranchData> {
  id: string;
}

export interface CreateDepartmentData {
  departmentCode: string;
  departmentName: string;
  branch: string;
}

export interface UpdateDepartmentData extends Partial<CreateDepartmentData> {
  id: string;
}

// Add types for filter parameters
export interface AccountBaseFilters {
  branch_code?: string;
  branch_name?: string;
  category?: string;
  product_name?: string;
  sector?: string;
  industry?: string;
  cust_type?: string;
  min_balance?: number;
  max_balance?: number;
  opening_date_from?: string;
  opening_date_to?: string;
}

// Add types for statistics
export interface AccountBaseStats {
  total_accounts: number;
  total_balance: number;
  average_balance: number;
  by_branch: Array<{
    branch_name: string;
    count: number;
    total_balance: number;
    average_balance: number;
  }>;
  by_product: Array<{
    product_name: string;
    count: number;
    total_balance: number;
    average_balance: number;
  }>;
  by_category: Array<{
    category: string;
    count: number;
    total_balance: number;
    average_balance: number;
  }>;
}

// Add types for pagination
export interface PaginationParams {
  page?: number;
  page_size?: number;
  ordering?: string;
  search?: string;
}

// Add types for permission checking
export interface UserPermissions {
  user_management: {
    view_users: boolean;
    add_users: boolean;
    change_users: boolean;
    delete_users: boolean;
  };
  role_management: {
    view_roles: boolean;
    manage_roles: boolean;
  };
  permission_management: {
    view_permissions: boolean;
    manage_permissions: boolean;
  };
  branch_management: {
    view_branches: boolean;
    manage_branches: boolean;
  };
  department_management: {
    view_departments: boolean;
    manage_departments: boolean;
  };
  report_access: {
    view_accountbase: boolean;
    view_reports: boolean;
    export_reports: boolean;
  };
}

// Add types for accessible endpoints
export interface AccessibleEndpoints {
  auth: {
    login: string | null;
    register: string | null;
    logout: string | null;
    me: string | null;
  };
  users: {
    list: string | null;
    create: string | null;
    detail: string | null;
    change_password: string | null;
  };
  roles: {
    list: string | null;
    detail: string | null;
  };
  branches: {
    list: string | null;
    detail: string | null;
  };
  departments: {
    list: string | null;
    detail: string | null;
  };
  reports: {
    account_base: string | null;
    stats: string | null;
    export: string | null;
  };
}