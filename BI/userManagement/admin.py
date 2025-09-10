from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, AppPermission, Branch, Department

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'role', 'branch', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'role', 'branch')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('id', 'date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'branch')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'role',
                'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'first_name', 'last_name', 'branch', 'is_active', 'is_staff', 'role'
            )
        }),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    filter_horizontal = ('permissions',)
    search_fields = ('name',)

@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'description')
    search_fields = ('name', 'codename')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branchCode', 'branchName')
    search_fields = ('branchCode', 'branchName')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('departmentCode', 'departmentName', 'branch')
    list_filter = ('branch',)
    search_fields = ('departmentCode', 'departmentName')
