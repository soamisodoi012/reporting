# urls.py (main project)
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="BI Project API",
      default_version='v1',
      description="Complete BI Project API with User Management and Reporting",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="support@bi-project.com"),
      license=openapi.License(name="Commercial License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # API Routes
    path('api/user-management/', include('userManagement.urls')),
    path('api/reports/', include('reportApp.urls')),
]
