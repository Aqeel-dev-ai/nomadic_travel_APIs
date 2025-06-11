"""
URL configuration for nomadic_travel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    )
from accounts.views import (
    verify_registration_otp,
    request_password_reset,
    verify_password_reset_otp,
    user_details,
    logout,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Nomadic Travel API",
        default_version='v1',
        description="API documentation for Nomadic Travel application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@nomadictravel.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    #destination urls
    path('admin/', admin.site.urls),
    path('api/destinations/', include('destination.urls')),
#schedule urls
    path('api/', include('schedule.urls')),
#accounts urls
    path('api/auth/', include('rest_registration.api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', logout, name='logout'),
    
    # OTP endpoints
    path('api/auth/verify-otp/', verify_registration_otp, name='verify-otp'),
    path('api/auth/request-password-reset/', request_password_reset, name='request-password-reset'),
    path('api/auth/verify-password-reset/', verify_password_reset_otp, name='verify-password-reset'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
