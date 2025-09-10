from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.conf import settings
from .models import CustomUser, Role, AppPermission, Branch, Department
from .serializers import (
    UserSerializer, RoleSerializer, AppPermissionSerializer,
    LoginSerializer, ChangePasswordSerializer, UserRegistrationSerializer,
    BranchSerializer, DepartmentSerializer
)
from .permissions import (
    IsAdmin, IsOwnerOrAdmin, CanViewUsers, CanAddUsers, 
    CanChangeUsers, CanDeleteUsers, CanViewRoles, CanManageRoles,
    CanViewPermissions, CanManagePermissions, CanViewBranches, 
    CanManageBranches, CanViewDepartments, CanManageDepartments, OrPermission
)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="User login with email and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response('Login successful', LoginSerializer),
            400: 'Invalid credentials'
        }
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="User registration",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response('Registration successful', UserSerializer),
            400: 'Invalid data'
        }
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="User logout (blacklist refresh token)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            205: 'Logout successful',
            400: 'Invalid token'
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'is_staff', 'role']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined']

    def get_permissions(self):
        if getattr(settings, "DEVELOPMENT", False):
            # Development mode: allow everything
            return [AllowAny()]
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), OrPermission(CanViewUsers, IsAdmin)]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), OrPermission(CanChangeUsers, IsAdmin)]
        elif self.action == 'destroy':
            return [IsAuthenticated(), OrPermission(CanDeleteUsers, IsAdmin)]
        elif self.action in ['change_password', 'permissions_check']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        else:
            return [IsAuthenticated()]


    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: 'Password changed successfully',
            400: 'Invalid data'
        }
    )
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'password changed'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Check user permissions and accessible endpoints",
        responses={200: 'User permissions information'}
    )
    @action(detail=False,  methods=['get'], url_path='permissions-check')
    def permissions_check(self, request):
        user = request.user
        permissions = {
            'user_management': {
                'view_users': user.has_perm('userManagement.view_customuser'),
                'add_users': user.has_perm('userManagement.add_customuser'),
                'change_users': user.has_perm('userManagement.change_customuser'),
                'delete_users': user.has_perm('userManagement.delete_customuser'),
            },
            'role_management': {
                'view_roles': user.has_perm('userManagement.view_role'),
                'manage_roles': user.has_perm('userManagement.manage_role'),
            },
            'permission_management': {
                'view_permissions': user.has_perm('userManagement.view_apppermission'),
                'manage_permissions': user.has_perm('userManagement.manage_apppermission'),
            },
            'branch_management': {
                'view_branches': user.has_perm('userManagement.view_branch'),
                'manage_branches': user.has_perm('userManagement.manage_branch'),
            },
            'department_management': {
                'view_departments': user.has_perm('userManagement.view_department'),
                'manage_departments': user.has_perm('userManagement.manage_department'),
            },
            'report_access': {
                'view_accountbase': user.has_perm('userManagement.view_accountbase'),
                'view_reports': user.has_perm('userManagement.view_reports'),
                'export_reports': user.has_perm('userManagement.export_reports'),
            }
        }
        return Response({"status": "permissions checked"})
        # return Response({
        #     'user': {
        #         'id': user.id,
        #         'email': user.email,
        #         'role': user.role.name if user.role else None,
        #         'is_superuser': user.is_superuser,
        #         'is_staff': user.is_staff
        #     },
        #     'permissions': permissions,
        #     'accessible_endpoints': self.get_accessible_endpoints(permissions)
        # })

    def get_accessible_endpoints(self, permissions):
        base_url = '/api/'  # ✅ only /api/, not /api/auth/

        return {
            'auth': {
                'login': f'{base_url}auth/login/',
                'register': f'{base_url}auth/register/',
                'logout': f'{base_url}auth/logout/',
                'me': f'{base_url}auth/me/',   # ✅ now /api/auth/me/
            },
            'users': {
                'list': f'{base_url}users/' if permissions['user_management']['view_users'] else None,
                'create': f'{base_url}users/' if permissions['user_management']['add_users'] else None,
                'detail': f'{base_url}users/{{id}}/' if permissions['user_management']['view_users'] else None,
                'change_password': f'{base_url}users/{{id}}/change_password/' if permissions['user_management']['change_users'] else None,
            },
            'roles': {
                'list': f'{base_url}roles/' if permissions['role_management']['view_roles'] else None,
                'detail': f'{base_url}roles/{{id}}/' if permissions['role_management']['view_roles'] else None,
            },
            'reports': {
                'account_base': f'/api/reports/account-base/' if permissions['report_access']['view_accountbase'] else None,
                'stats': f'/api/reports/account-base/stats/' if permissions['report_access']['view_reports'] else None,
                'export': f'/api/reports/account-base/export/' if permissions['report_access']['export_reports'] else None,
            }
        }


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewRoles(),  IsAdmin()]
        else:
            return [IsAuthenticated(), CanManageRoles() | IsAdmin()]

    @swagger_auto_schema(
        operation_description="Get role details with permissions",
        responses={200: RoleSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new role",
        request_body=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: 'Invalid data'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = AppPermission.objects.all()
    serializer_class = AppPermissionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'codename']
    ordering_fields = ['name', 'codename']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewPermissions(), IsAdmin()]
        else:
            return [IsAuthenticated(), CanManagePermissions() , IsAdmin()]

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['branchCode', 'branchName']
    filterset_fields = ['user']
    ordering_fields = ['branchCode', 'branchName']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewBranches() | IsAdmin()]
        else:
            return [IsAuthenticated(), CanManageBranches() | IsAdmin()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['departmentCode', 'departmentName']
    filterset_fields = ['branch']
    ordering_fields = ['departmentCode', 'departmentName']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewDepartments() | IsAdmin()]
        else:
            return [IsAuthenticated(), CanManageDepartments() | IsAdmin()]

