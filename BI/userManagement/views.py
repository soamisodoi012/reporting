# userManagement/views.py
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import CustomUser, Role, Permission
from .serializers import (
    UserSerializer, RoleSerializer, PermissionSerializer,
    LoginSerializer, ChangePasswordSerializer, UserRegistrationSerializer
)
from .permissions import (
    IsAdmin, IsOwnerOrAdmin, CanViewUsers, CanAddUsers, 
    CanChangeUsers, CanDeleteUsers, CanViewRoles, CanManageRoles,
    CanViewPermissions, CanManagePermissions
)

# Auth Views
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# User Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewUsers() | IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), CanChangeUsers() | IsAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), CanDeleteUsers() | IsAdmin()]
        elif self.action == 'change_password':
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

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

# Role Views
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewRoles() | IsAdmin()]
        else:
            return [IsAuthenticated(), CanManageRoles() | IsAdmin()]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

# Permission Views
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewPermissions() | IsAdmin()]
        else:
            return [IsAuthenticated(), CanManagePermissions() | IsAdmin()]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()