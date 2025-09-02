# userManagement/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, AppPermission

@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'codename']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    filter_horizontal = ['permissions']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    readonly_fields = ['id', 'date_joined', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff')}
        ),
    )