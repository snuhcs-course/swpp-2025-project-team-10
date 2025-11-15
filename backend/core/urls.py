"""
URL configuration for Book Bartering Social Network.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts.views import UserProfileMeView, follow_view
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Token API
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    # Authentication
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    # Place explicit profile endpoint first to avoid overlap with allauth URLs.
    path("accounts/profile/me/", UserProfileMeView.as_view(), name="profile_me"),
    path("accounts/", include("allauth.urls")),
    # API Endpoints
    path("auth/", include("accounts.urls")),  # Matches frontend expectations
    path("library/", include("books.urls")),  # User's library (reviews, books)
    path("", include("social.urls")),  # Social features (home feed, posts)
    path("barter/", include("barter.urls")),  # Barter requests
    # Follow API to match frontend expectations
    path("users/follow/<int:user_id>/", follow_view, name="follow_user"),
    # path("api/v1/notifications/", include("notify.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )

    # Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns

    # Silk Profiler
    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
