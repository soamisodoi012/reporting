# userManagement/permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class HasPermission(permissions.BasePermission):
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.has_perm(self.permission_codename)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
            
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
            
        return False

# User permissions
class CanViewUsers(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_customuser')

class CanAddUsers(HasPermission):
    def __init__(self):
        super().__init__('userManagement.add_customuser')

class CanChangeUsers(HasPermission):
    def __init__(self):
        super().__init__('userManagement.change_customuser')

class CanDeleteUsers(HasPermission):
    def __init__(self):
        super().__init__('userManagement.delete_customuser')

# Role permissions
class CanViewRoles(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_role')

class CanManageRoles(HasPermission):
    def __init__(self):
        super().__init__('userManagement.manage_role')

# Permission permissions
class CanViewPermissions(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_apppermission')

class CanManagePermissions(HasPermission):
    def __init__(self):
        super().__init__('userManagement.manage_apppermission')

# Branch permissions
class CanViewBranches(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_branch')

class CanManageBranches(HasPermission):
    def __init__(self):
        super().__init__('userManagement.manage_branch')

# Department permissions
class CanViewDepartments(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_department')

class CanManageDepartments(HasPermission):
    def __init__(self):
        super().__init__('userManagement.manage_department')

# Report permissions
class CanViewAccountBase(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_accountbase')

class CanViewReports(HasPermission):
    def __init__(self):
        super().__init__('userManagement.view_reports')

class CanExportReports(HasPermission):
    def __init__(self):
        super().__init__('userManagement.export_reports')

class OrPermission(permissions.BasePermission):
    """
    Permission that allows access if any of the given permissions passes.
    """
    def __init__(self, *permission_classes):
        self.permission_classes = permission_classes

    def has_permission(self, request, view):
        for permission_class in self.permission_classes:
            permission = permission_class()
            if permission.has_permission(request, view):
                return True
        return False

    def has_object_permission(self, request, view, obj):
        for permission_class in self.permission_classes:
            permission = permission_class()
            if permission.has_object_permission(request, view, obj):
                return True
        return False
