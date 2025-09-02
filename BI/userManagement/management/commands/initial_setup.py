# userManagement/management/commands/initial_setup.py
from django.core.management.base import BaseCommand
from userManagement.models import AppPermission, Role

class Command(BaseCommand):
    help = 'Creates initial permissions and roles'

    def handle(self, *args, **options):
        # Create permissions
        permissions_data = [
            {'name': 'View Users', 'codename': 'user.view'},
            {'name': 'Add Users', 'codename': 'user.add'},
            {'name': 'Change Users', 'codename': 'user.change'},
            {'name': 'Delete Users', 'codename': 'user.delete'},
            {'name': 'View Roles', 'codename': 'role.view'},
            {'name': 'Manage Roles', 'codename': 'role.manage'},
            {'name': 'View Permissions', 'codename': 'permission.view'},
            {'name': 'Manage Permissions', 'codename': 'permission.manage'},
        ]

        for perm_data in permissions_data:
            AppPermission.objects.get_or_create(**perm_data)

        # Create roles
        admin_role, created = Role.objects.get_or_create(
            name='Administrator',
            defaults={'description': 'System administrator with full access'}
        )

        user_role, created = Role.objects.get_or_create(
            name='User',
            defaults={'description': 'Regular user with limited access'}
        )

        # Assign all permissions to admin role
        all_permissions = AppPermission.objects.all()
        admin_role.permissions.set(all_permissions)

        # Assign basic permissions to user role
        user_permissions = AppPermission.objects.filter(
            codename__in=['user.view', 'role.view', 'permission.view']
        )
        user_role.permissions.set(user_permissions)

        self.stdout.write(
            self.style.SUCCESS('Successfully created initial permissions and roles')
        )