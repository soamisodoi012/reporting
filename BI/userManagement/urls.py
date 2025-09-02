# userManagement/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, RoleViewSet, PermissionViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
]