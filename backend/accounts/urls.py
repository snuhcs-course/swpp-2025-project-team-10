"""
URL patterns for the accounts app.
"""

from django.urls import path

from . import views

app_name = "accounts"

# Add URL patterns for the UserTaste views

urlpatterns = [
    # Authentication endpoints matching frontend expectations
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("signup/", views.UserRegistrationView.as_view(), name="signup"),
    path(
        "token/refresh/",
        views.CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # Password reset endpoints
    path(
        "forgot/start/",
        views.PasswordResetRequestView.as_view(),
        name="forgot_password_start",
    ),
    path(
        "forgot/verify/",
        views.PasswordResetVerifyView.as_view(),
        name="forgot_password_verify",
    ),
    path(
        "forgot/reset/",
        views.PasswordResetConfirmView.as_view(),
        name="forgot_password_reset",
    ),
    # Social authentication
    path("social/", views.SocialAuthView.as_view(), name="social_auth"),
    # Google-specific authentication endpoints (matching frontend expectations)
    path(
        "login/google/", views.GoogleLoginView.as_view(), name="google_login"
    ),
    path(
        "signup/google/",
        views.GoogleSignupView.as_view(),
        name="google_signup",
    ),
    # Kakao-specific authentication endpoints (matching frontend expectations)
    path("login/kakao/", views.KakaoLoginView.as_view(), name="kakao_login"),
    path(
        "signup/kakao/", views.KakaoSignupView.as_view(), name="kakao_signup"
    ),
    # Profile management
    path("profile/", views.user_profile, name="user_profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("preferences/", views.user_preferences, name="user_preferences"),
    # User Taste endpoints
    path("taste/", views.UserTasteView.as_view(), name="user_taste"),
    # Onboarding
    path("users/onboarding/", views.onboarding_submit, name="onboarding_submit"),
]
