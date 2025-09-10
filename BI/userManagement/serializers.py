from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission as AuthPermission
from .models import CustomUser, Role, AppPermission, Branch, Department

# -------------------- AppPermission --------------------
class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = ['id', 'name', 'codename', 'description', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at')

class AuthPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthPermission
        fields = '__all__'

# -------------------- Role --------------------
class RoleSerializer(serializers.ModelSerializer):
    permissions = AppPermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_ids', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        if permission_ids:
            permissions = AppPermission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permission_ids is not None:
            permissions = AppPermission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        return instance

# -------------------- Branch --------------------
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['branchCode', 'branchName']
        read_only_fields = []

# -------------------- Department --------------------
class DepartmentSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.branchName', read_only=True)
    
    class Meta:
        model = Department
        fields = ['departmentCode', 'departmentName', 'branch', 'branch_name']

# -------------------- User --------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role_name = serializers.CharField(source='role.name', read_only=True)
    branch_name = serializers.CharField(source='branch.branchName', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password',
            'is_active', 'is_staff', 'is_superuser',
            'role', 'role_name', 'branch', 'branch_name',
            'permissions', 'date_joined', 'last_login'
        ]
        read_only_fields = ('id', 'date_joined', 'last_login')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_permissions(self, obj):
        return [p.codename for p in obj.get_all_permissions() if hasattr(p, 'codename')]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# -------------------- Login --------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Authenticate with email
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if not user:
                try:
                    user = CustomUser.objects.get(email=email)
                    if user.check_password(password):
                        if not user.is_active:
                            raise serializers.ValidationError('User account is disabled.')
                        data['user'] = user
                    else:
                        raise serializers.ValidationError('Unable to log in with provided credentials.')
                except CustomUser.DoesNotExist:
                    raise serializers.ValidationError('Unable to log in with provided credentials.')
            else:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        return data

# -------------------- Change Password --------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        return value

# -------------------- Registration --------------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'branch']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            branch=validated_data.get('branch', None)
        )
        return user
