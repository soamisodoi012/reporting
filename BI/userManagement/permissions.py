# userManagement/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class HasPermission(permissions.BasePermission):
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has the specific permission
        return request.user.has_perm(self.permission_codename)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
            
        # Check if the object has a user attribute and it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
            
        return False

# Specific permission classes for common use cases
class CanViewUsers(HasPermission):
    def __init__(self):
        super().__init__('user.view')

class CanAddUsers(HasPermission):
    def __init__(self):
        super().__init__('user.add')

class CanChangeUsers(HasPermission):
    def __init__(self):
        super().__init__('user.change')

class CanDeleteUsers(HasPermission):
    def __init__(self):
        super().__init__('user.delete')

class CanViewRoles(HasPermission):
    def __init__(self):
        super().__init__('role.view')

class CanManageRoles(HasPermission):
    def __init__(self):
        super().__init__('role.manage')

class CanViewPermissions(HasPermission):
    def __init__(self):
        super().__init__('permission.view')

class CanManagePermissions(HasPermission):
    def __init__(self):
        super().__init__('permission.manage')