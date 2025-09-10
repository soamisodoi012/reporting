# management/commands/load_initial_data.py
from django.core.management.base import BaseCommand
from userManagement.models import AppPermission, Role, CustomUser

class Command(BaseCommand):
    help = 'Load initial data for the application'

    def handle(self, *args, **options):
        # Create basic permissions
        permissions_data = [
            {'name': 'View Users', 'codename': 'view_customuser'},
            {'name': 'Add Users', 'codename': 'add_customuser'},
            {'name': 'Change Users', 'codename': 'change_customuser'},
            {'name': 'Delete Users', 'codename': 'delete_customuser'},
            {'name': 'View Roles', 'codename': 'view_role'},
            {'name': 'Manage Roles', 'codename': 'manage_role'},
            {'name': 'View Permissions', 'codename': 'view_apppermission'},
            {'name': 'Manage Permissions', 'codename': 'manage_apppermission'},
            {'name': 'View Branches', 'codename': 'view_branch'},
            {'name': 'Manage Branches', 'codename': 'manage_branch'},
            {'name': 'View Departments', 'codename': 'view_department'},
            {'name': 'Manage Departments', 'codename': 'manage_department'},
        ]

        for perm_data in permissions_data:
            AppPermission.objects.get_or_create(**perm_data)

        # Create admin role
        admin_role, created = Role.objects.get_or_create(
            name='Administrator',
            description='Full system access'
        )
        
        if created:
            all_permissions = AppPermission.objects.all()
            admin_role.permissions.set(all_permissions)

        # Create default admin user if not exists
        if not CustomUser.objects.filter(email='admin@example.com').exists():
            admin_user = CustomUser.objects.create_superuser(
                email='admin@example.com',
                password='adminpassword',
                first_name='Admin',
                last_name='User'
            )
            admin_user.role = admin_role
            admin_user.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded initial data')
        )
    # management/commands/load_initial_data.py
# Add these permissions to your existing command
report_permissions_data = [
    {'name': 'View Account Base', 'codename': 'view_accountbase'},
    {'name': 'View Reports', 'codename': 'view_reports'},
    {'name': 'Export Reports', 'codename': 'export_reports'},
]

for perm_data in report_permissions_data:
    AppPermission.objects.get_or_create(**perm_data)

# Optionally, add these permissions to your admin role
admin_role = Role.objects.get_or_create(name='Administrator')[0]
report_permissions = AppPermission.objects.filter(
    codename__in=['view_accountbase', 'view_reports', 'export_reports']
)
admin_role.permissions.add(*report_permissions)