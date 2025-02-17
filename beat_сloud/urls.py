"""
URL configuration for beat_сloud project.

The `urlpatterns` list routes URLs to listens. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function listens
    1. Add an import:  from my_app import listens
    2. Add a URL to urlpatterns:  path('', listens.home, name='home')
Class-based listens
    1. Add an import:  from other_app.listens import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.renderers import SwaggerUIRenderer


schema_view = get_schema_view(
    openapi.Info(
        title="BeatCloud API",
        default_version='v1',
        description="BeatCloud Docs",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='verify_refresh'),
    path('auth/sign-in/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/', include("userapp.urls")),
    path('music/', include("musicapp.urls")),
    path('favorites/', include("featuredapp.urls")),
    path('singers/', include("singerapp.urls")),
    path('comments/', include("commentapp.urls")),
    path('playlist/', include("playlistapp.urls")),
    path('love/', include("subscriptions.urls"))
]
