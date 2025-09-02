# userManagement/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission as AuthPermission
from .models import CustomUser, Role, AppPermission

class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class AuthPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthPermission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    permissions = AppPermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Role
        fields = '__all__'
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

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password',
            'is_active', 'is_staff', 'is_superuser', 'role', 'role_name',
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

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user