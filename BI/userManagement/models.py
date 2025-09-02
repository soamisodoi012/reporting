# userManagement/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

# Rename Permission to AppPermission to avoid conflict with Django's built-in Permission
class AppPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Application Permission'
        verbose_name_plural = 'Application Permissions'

    def __str__(self):
        return self.name

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(AppPermission, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_all_permissions(self, obj=None):
        permissions = set()
        
        # Get permissions from role
        if self.role:
            permissions.update(self.role.permissions.all())
        
        # Get direct user permissions (Django's built-in permissions)
        permissions.update(self.user_permissions.all())
        
        # Superusers have all permissions
        if self.is_superuser:
            permissions.update(AppPermission.objects.all())
            
        return permissions

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
            
        # Check if user has the specific permission
        perm_codename = perm.split('.')[-1] if '.' in perm else perm
        
        # Check Django's built-in permissions
        if hasattr(self, 'has_perm_builtin'):
            if self.has_perm_builtin(perm):
                return True
        
        # Check custom application permissions
        user_permissions = self.get_all_permissions()
        return any(p.codename == perm_codename for p in user_permissions if hasattr(p, 'codename'))