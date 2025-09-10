# reportApp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountBaseViewSet

router = DefaultRouter()
router.register(r'account-base', AccountBaseViewSet, basename='account-base')

urlpatterns = [
    path('', include(router.urls)),
]
