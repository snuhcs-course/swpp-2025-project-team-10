"""
Views for the accounts app.
Handles user authentication, registration, and profile management.
"""

import uuid

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .models import UserPreferences, UserTaste
from .serializers import (
    CustomTokenObtainPairSerializer,
    GoogleAuthSerializer,
    KakaoAuthSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    ProfileUpdateSerializer,
    SocialAuthSerializer,
    UserPreferencesSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserTasteSerializer,
)

User = get_user_model()


class UserTasteView(APIView):
    """
    View for managing user's book preferences and taste information.
    Each step of the categorization process is handled separately.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's current taste information and step."""
        try:
            taste = UserTaste.objects.get(user=request.user)
            serializer = UserTasteSerializer(taste)
            return Response(
                {
                    "ok": True,
                    "taste": serializer.data,
                    "step": taste.current_step,
                    "is_complete": request.user.has_initial_taste,
                }
            )
        except UserTaste.DoesNotExist:
            # Create new taste profile if it doesn't exist
            taste = UserTaste.objects.create(user=request.user)
            return Response(
                {
                    "ok": True,
                    "taste": UserTasteSerializer(taste).data,
                    "step": 1,
                    "is_complete": False,
                }
            )

    def post(self, request):
        """Handle each step of the taste categorization process."""
        try:
            taste = UserTaste.objects.get(user=request.user)
        except UserTaste.DoesNotExist:
            taste = UserTaste.objects.create(user=request.user)

        # Get current step from the taste profile
        current_step = taste.current_step

        # Validate and update based on current step
        serializer = UserTasteSerializer(
            taste, data=request.data, partial=True
        )
        if serializer.is_valid():
            # Validate minimum selections based on current step
            try:
                self._validate_step_data(
                    current_step, serializer.validated_data
                )
            except serializers.ValidationError as e:
                return Response(
                    {"ok": False, "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the taste profile
            taste = serializer.save()

            # Move to next step or complete the process (now 7 steps)
            if current_step < 7:
                taste.current_step += 1
                taste.save()
            else:
                # Mark categorization as complete
                request.user.has_initial_taste = True
                request.user.save()

            return Response(
                {
                    "ok": True,
                    "taste": UserTasteSerializer(taste).data,
                    "step": taste.current_step,
                    "is_complete": request.user.has_initial_taste,
                }
            )

        return Response(
            {"ok": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _validate_step_data(self, step, data):
        """Validate data for each categorization step."""
        if step == 1 and "favorite_genres" in data:
            if len(data["favorite_genres"]) < 3:
                raise serializers.ValidationError(
                    "최소 3개 이상의 장르를 선택해주세요"
                )
        elif step == 2 and "favorite_authors" in data:
            if len(data["favorite_authors"]) < 3:
                raise serializers.ValidationError(
                    "최소 3명 이상의 작가를 선택해주세요"
                )
        elif step == 3 and "favorite_books" in data:
            if len(data["favorite_books"]) < 3:
                raise serializers.ValidationError(
                    "최소 3권 이상의 책을 선택해주세요"
                )
        elif step == 4 and "preferred_length" in data:
            if not data["preferred_length"]:
                raise serializers.ValidationError("책 분량을 선택해주세요")
        elif step == 5 and "preferred_moods" in data:
            if len(data["preferred_moods"]) < 3:
                raise serializers.ValidationError(
                    "최소 3개 이상의 분위기를 선택해주세요"
                )
        elif step == 6 and "reading_purposes" in data:
            if len(data["reading_purposes"]) < 3:
                raise serializers.ValidationError(
                    "최소 3개 이상의 목적을 선택해주세요"
                )
        elif step == 7:
            # Trade style step is optional; if provided, accept without strict min checks
            # Fields: trade_place_name, trade_address
            # No additional validation required here.
            return


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that matches frontend expectations.
    Returns response in format: {"ok": true, "token": "...", "message": "..."}
    """

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticate user and return JWT tokens",
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data

            return Response(
                {
                    "ok": True,
                    "accessToken": tokens["access"],
                    "refreshToken": tokens["refresh"],
                    "user": tokens["user"],
                    "message": "Login successful",
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            return Response(
                {"ok": False, "message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view that matches frontend expectations.
    Returns response in format: {"accessToken": "...", "refreshToken": "..."}
    """

    @extend_schema(
        summary="Refresh JWT Token",
        description="Refresh access token using refresh token",
        responses={
            200: OpenApiResponse(description="Token refresh successful"),
            401: OpenApiResponse(description="Invalid refresh token"),
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            data = response.data
            return Response(
                {
                    "accessToken": data.get("access"),
                    "refreshToken": data.get("refresh", ""),
                },
                status=status.HTTP_200_OK,
            )

        return response


class UserRegistrationView(APIView):
    """
    User registration view matching frontend SignUpRequest/Response.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="User Registration",
        description="Register a new user account",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="Registration successful"),
            400: OpenApiResponse(description="Registration failed"),
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "ok": True,
                    "message": "Registration successful",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "ok": False,
                "message": "Registration failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetRequestView(APIView):
    """
    Password reset request view (forgot password start).
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Request Password Reset",
        description="Send password reset code to user email",
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(description="Reset code sent"),
            400: OpenApiResponse(description="Invalid email"),
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Check if user exists (but don't reveal this in response)
            try:
                User.objects.get(email=email)
                user_exists = True
            except User.DoesNotExist:
                user_exists = False

            # Generate reset code and request ID
            request_id = str(uuid.uuid4())
            reset_code = get_random_string(6, allowed_chars="0123456789")

            # Only store and send email if user exists
            if user_exists:
                # Store in cache for 15 minutes
                cache_key = f"password_reset_{request_id}"
                cache.set(
                    cache_key,
                    {"email": email, "code": reset_code, "verified": False},
                    timeout=900,
                )  # 15 minutes

                # Send email (in production, use proper email service)
                try:
                    send_mail(
                        subject="Password Reset Code",
                        message=f"Your password reset code is: {reset_code}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                except Exception:
                    # In development, just log the code
                    print(f"Password reset code for {email}: {reset_code}")

            # Always return success to prevent email enumeration
            return Response(
                {
                    "ok": True,
                    "requestId": request_id,
                    "code": (
                        reset_code if settings.DEBUG and user_exists else None
                    ),  # Only return code in debug mode and if user exists
                    "message": "If the email exists, a reset code has been sent",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"ok": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetVerifyView(APIView):
    """
    Password reset verification view.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Verify Password Reset Code",
        description="Verify the password reset code",
        request=PasswordResetVerifySerializer,
        responses={
            200: OpenApiResponse(description="Code verified"),
            400: OpenApiResponse(description="Invalid code"),
        },
    )
    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)

        if serializer.is_valid():
            request_id = serializer.validated_data["request_id"]
            code = serializer.validated_data["code"]

            cache_key = f"password_reset_{request_id}"
            reset_data = cache.get(cache_key)

            if reset_data and reset_data["code"] == code:
                # Mark as verified
                reset_data["verified"] = True
                cache.set(cache_key, reset_data, timeout=900)

                return Response(
                    {"ok": True, "message": "Code verified successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"ok": False, "message": "Invalid or expired code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"ok": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation view.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Reset Password",
        description="Reset user password with new password",
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            400: OpenApiResponse(description="Reset failed"),
        },
    )
    def post(self, request):
        # This would typically require the request_id from the session or token
        # For now, we'll implement a basic version
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            # In a real implementation, you'd get the request_id from the session
            # and verify it was previously verified
            return Response(
                {"ok": True, "message": "Password reset successful"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"ok": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SocialAuthView(APIView):
    """
    Social authentication view for Google, Facebook, Kakao.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Social Authentication",
        description="Authenticate user with social provider",
        request=SocialAuthSerializer,
        responses={
            200: OpenApiResponse(description="Social auth successful"),
            400: OpenApiResponse(description="Social auth failed"),
        },
    )
    def post(self, request):
        serializer = SocialAuthSerializer(data=request.data)

        if serializer.is_valid():
            provider = serializer.validated_data["provider"]
            access_token = serializer.validated_data["access_token"]

            # Validate token with provider and get user info
            user_info = self.validate_social_token(provider, access_token)

            if user_info:
                # Get or create user
                user, _ = self.get_or_create_social_user(provider, user_info)

                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        "ok": True,
                        "accessToken": str(refresh.access_token),
                        "refreshToken": str(refresh),
                        "user": UserSerializer(user).data,
                        "message": "Social authentication successful",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"ok": False, "message": "Invalid social token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"ok": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def validate_social_token(self, provider, access_token):
        """Validate social token with provider."""
        try:
            if provider == "google":
                response = requests.get(
                    f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}",
                    timeout=10,
                )
                if response.status_code == 200:
                    return response.json()

            elif provider == "facebook":
                response = requests.get(
                    f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}",
                    timeout=10,
                )
                if response.status_code == 200:
                    return response.json()

            elif provider == "kakao":
                response = requests.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            print(f"Social auth error: {e}")

        return None

    def get_or_create_social_user(self, _provider, user_info):
        """Get or create user from social provider info."""
        from django.db import IntegrityError, transaction

        email = user_info.get("email")
        name = user_info.get("name", "")

        if email:
            try:
                user = User.objects.get(email=email)
                return user, False
            except User.DoesNotExist:
                # Create new user with unique username
                base_username = email.split("@")[0]

                # Try to create user with retry logic for username conflicts
                max_attempts = 5
                for attempt in range(max_attempts):
                    try:
                        # Generate username with random suffix if not first attempt
                        if attempt == 0:
                            username = base_username
                        else:
                            # Use random 6-character suffix for uniqueness
                            random_suffix = get_random_string(
                                6,
                                allowed_chars="0123456789abcdefghijklmnopqrstuvwxyz",
                            )
                            username = f"{base_username}_{random_suffix}"

                        # Use atomic transaction to handle IntegrityError properly
                        with transaction.atomic():
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                first_name=name.split(" ")[0] if name else "",
                                last_name=(
                                    " ".join(name.split(" ")[1:])
                                    if len(name.split(" ")) > 1
                                    else ""
                                ),
                            )

                            # Create user preferences
                            UserPreferences.objects.create(user=user)

                        return user, True

                    except IntegrityError:
                        # Username collision, retry with different suffix
                        if attempt == max_attempts - 1:
                            # Last attempt failed, raise error
                            raise Exception(
                                "Failed to create unique username after "
                                f"{max_attempts} attempts"
                            )
                        continue

        return None, False


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update current user profile."""
    serializer = ProfileUpdateSerializer(
        request.user, data=request.data, partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "ok": True,
                "user": UserSerializer(request.user).data,
                "message": "Profile updated successfully",
            }
        )

    return Response(
        {"ok": False, "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def user_preferences(request):
    """Get or update user preferences."""
    # Get or create preferences for the user
    preferences, created = UserPreferences.objects.get_or_create(
        user=request.user
    )

    if request.method == "GET":
        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data)

    # PUT or PATCH
    serializer = UserPreferencesSerializer(
        preferences, data=request.data, partial=(request.method == "PATCH")
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileMeView(APIView):
    """
    Combined endpoint for fetching and updating the authenticated user's profile.
    Matches frontend expectation for /accounts/profile/me/ (GET, PUT/PATCH) and
    supports multipart form uploads for profile_picture.
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        """Return the current user's profile in frontend's expected shape."""
        return Response(self._build_frontend_profile(request.user, request))

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial: bool):
        # 1) Update basic profile fields (bio, names, etc.)
        base_serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if base_serializer.is_valid():
            base_serializer.save()
        else:
            # We don't hard-fail here because frontend may only send preferences
            pass

        # 2) Update preferences coming from nested object
        prefs = request.data.get("preferences") or {}
        favorite_genres = request.data.get("favoriteGenres") or []

        # Store trade locations in UserTaste (closest existing fields)
        # Ensure taste exists
        from .models import UserTaste
        taste, _ = UserTaste.objects.get_or_create(user=request.user)
        # Map incoming fields to available fields
        trade_location1 = prefs.get("tradeLocation1")
        trade_spot1 = prefs.get("tradeSpot1")
        if trade_location1 is not None:
            taste.trade_place_name = trade_location1
        if trade_spot1 is not None:
            taste.trade_address = trade_spot1

        # Save favorite genres if provided
        if isinstance(favorite_genres, list):
            taste.favorite_genres = favorite_genres
        taste.save()

        # Mark initial taste as present if any taste data exists
        if (trade_location1 or trade_spot1 or favorite_genres) and not request.user.has_initial_taste:
            request.user.has_initial_taste = True
            request.user.save(update_fields=["has_initial_taste"])

        return Response(self._build_frontend_profile(request.user, request))

    def _build_frontend_profile(self, user, request):
        """Build response matching frontend UserProfile DTO."""
        # Profile URL
        profile_url = None
        if user.profile_picture:
            profile_url = (
                request.build_absolute_uri(user.profile_picture.url)
                if request else user.profile_picture.url
            )

        # Taste and preferences mapping
        favorite_genres = []
        trade_location1 = None
        trade_spot1 = None
        try:
            taste = user.taste
            favorite_genres = taste.favorite_genres or []
            trade_location1 = taste.trade_place_name or None
            trade_spot1 = taste.trade_address or None
        except Exception:
            pass

        # Compute counts
        from books.models import BookReview
        review_count = BookReview.objects.filter(reviewer=user).count()
        follower_count = getattr(user, "follower_count", None)
        following_count = getattr(user, "following_count", None)
        if follower_count is None:
            follower_count = user.follower_relationships.count()
        if following_count is None:
            following_count = user.following_relationships.count()

        return {
            "username": user.username,
            "bio": user.bio,
            "profileUrl": profile_url,
            "reviewCount": review_count,
            "followerCount": follower_count,
            "followingCount": following_count,
            "favoriteGenres": favorite_genres,
            "preferences": {
                # Provide non-null object with nullable fields to avoid NPE on client
                "tradeLocation1": trade_location1,
                "tradeLocation2": None,
                "tradeSpot1": trade_spot1,
                "tradeSpot2": None,
                "favBook": None,
                "favBookNote": None,
                "favAuthor": None,
                "favAuthorNote": None,
                "readingHabit": None,
            },
        }


class GoogleLoginView(APIView):
    """
    Google ID Token authentication for login.
    Matches frontend expectations for /auth/login/google endpoint.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Google Login",
        description="Authenticate user with Google ID Token",
        request=GoogleAuthSerializer,
        responses={
            200: OpenApiResponse(description="Google login successful"),
            400: OpenApiResponse(description="Google login failed"),
        },
    )
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)

        if serializer.is_valid():
            id_token = serializer.validated_data["idToken"]

            # Validate Google ID token and get user info
            user_info = self.validate_google_id_token(id_token)

            if user_info:
                # Get or create user
                user, _ = self.get_or_create_google_user(user_info)

                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        "ok": True,
                        "accessToken": str(refresh.access_token),
                        "refreshToken": str(refresh),
                        "message": "Google login successful",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "ok": False,
                    "accessToken": None,
                    "refreshToken": None,
                    "message": "Invalid Google ID token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "ok": False,
                "accessToken": None,
                "refreshToken": None,
                "message": "Invalid request data",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def validate_google_id_token(self, id_token):
        """Validate Google ID token and extract user information."""
        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token as google_id_token

            # Verify the token
            request = google_requests.Request()
            id_info = google_id_token.verify_oauth2_token(
                id_token, request, settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            # Verify the issuer
            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer.")

            return {
                "email": id_info.get("email"),
                "name": id_info.get("name", ""),
                "first_name": id_info.get("given_name", ""),
                "last_name": id_info.get("family_name", ""),
                "google_id": id_info.get("sub"),
                "picture": id_info.get("picture", ""),
                "email_verified": id_info.get("email_verified", False),
            }

        except Exception as e:
            print(f"Google ID token validation error: {e}")
            return None

    def get_or_create_google_user(self, user_info):
        """Get or create user from Google user info."""
        from django.db import IntegrityError, transaction

        email = user_info.get("email")

        if not email:
            raise ValueError("Email is required from Google")

        # Try to find existing user by email
        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            pass

        # Create new user
        try:
            with transaction.atomic():
                # Generate unique username from email
                base_username = email.split("@")[0]
                username = base_username
                counter = 1

                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=user_info.get("first_name", ""),
                    last_name=user_info.get("last_name", ""),
                    is_active=True,
                )

                return user, True

        except IntegrityError as e:
            # If there's still a conflict, try to get the existing user
            try:
                user = User.objects.get(email=email)
                return user, False
            except User.DoesNotExist:
                raise ValueError(f"Failed to create user: {e}")


class GoogleSignupView(APIView):
    """
    Google ID Token authentication for signup.
    Matches frontend expectations for /auth/signup/google endpoint.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Google Signup",
        description="Register user with Google ID Token",
        request=GoogleAuthSerializer,
        responses={
            200: OpenApiResponse(description="Google signup successful"),
            400: OpenApiResponse(description="Google signup failed"),
        },
    )
    def post(self, request):
        # For Google auth, login and signup are essentially the same
        # We'll reuse the login logic but with different messaging
        login_view = GoogleLoginView()
        response = login_view.post(request)

        # Modify the message for signup context
        if response.status_code == 200:
            data = response.data.copy()
            data["message"] = "Google signup successful"
            return Response(data, status=status.HTTP_200_OK)

        return response


class KakaoLoginView(APIView):
    """
    Kakao access token authentication for login.
    Matches frontend expectations for /auth/login/kakao endpoint.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Kakao Login",
        description="Authenticate user with Kakao access token",
        request=KakaoAuthSerializer,
        responses={
            200: OpenApiResponse(description="Kakao login successful"),
            400: OpenApiResponse(description="Kakao login failed"),
        },
    )
    def post(self, request):
        serializer = KakaoAuthSerializer(data=request.data)

        if serializer.is_valid():
            access_token = serializer.validated_data["accessToken"]

            # Validate Kakao access token and get user info
            user_info = self.validate_kakao_token(access_token)

            if user_info:
                # Get or create user
                user, _ = self.get_or_create_kakao_user(user_info)

                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        "ok": True,
                        "accessToken": str(refresh.access_token),
                        "refreshToken": str(refresh),
                        "message": "Kakao login successful",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "ok": False,
                    "accessToken": None,
                    "refreshToken": None,
                    "message": "Invalid Kakao access token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "ok": False,
                "accessToken": None,
                "refreshToken": None,
                "message": "Invalid request data",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def validate_kakao_token(self, access_token):
        """Validate Kakao access token by calling Kakao API."""
        try:
            response = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                kakao_account = data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})

                return {
                    "email": kakao_account.get("email"),
                    "name": profile.get("nickname", ""),
                    "kakao_id": str(data.get("id")),
                    "profile_image": profile.get("profile_image_url", ""),
                    "email_verified": kakao_account.get(
                        "is_email_verified", False
                    ),
                }
        except Exception as e:
            print(f"Kakao token validation error: {e}")

        return None

    def get_or_create_kakao_user(self, user_info):
        """Get or create user from Kakao user info."""
        email = user_info.get("email")

        if not email:
            raise ValueError("Email is required from Kakao")

        # Try to get existing user by email
        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            pass

        # Create new user
        username = email.split("@")[0]

        # Handle username conflicts
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=user_info.get("name", ""),
            password=User.objects.make_random_password(),
        )

        return user, True


class KakaoSignupView(APIView):
    """
    Kakao signup view (reuses login logic).
    Matches frontend expectations for /auth/signup/kakao endpoint.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Kakao Signup",
        description="Register user with Kakao access token",
        request=KakaoAuthSerializer,
        responses={
            200: OpenApiResponse(description="Kakao signup successful"),
            400: OpenApiResponse(description="Kakao signup failed"),
        },
    )
    def post(self, request):
        # For Kakao auth, login and signup are essentially the same
        # We'll reuse the login logic but with different messaging
        login_view = KakaoLoginView()
        response = login_view.post(request)

        # Modify the message for signup context
        if response.status_code == 200:
            data = response.data.copy()
            data["message"] = "Kakao signup successful"
            return Response(data, status=status.HTTP_200_OK)

        return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if target_user == request.user:
        return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    follow, created = Follow.objects.get_or_create(follower=request.user, followed=target_user)
    if not created:
        return Response({"detail": "Already following."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": f"You are now following {target_user.username}."}, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    try:
        follow = Follow.objects.get(follower=request.user, followed_id=user_id)
    except Follow.DoesNotExist:
        return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

    follow.delete()
    return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
def list_followers(request, user_id):
    followers = Follow.objects.filter(followed_id=user_id).select_related("follower")
    data = [{"id": f.follower.id, "username": f.follower.username} for f in followers]
    return Response(data)

@api_view(["GET"])
def list_following(request, user_id):
    following = Follow.objects.filter(follower_id=user_id).select_related("followed")
    data = [{"id": f.followed.id, "username": f.followed.username} for f in following]
    return Response(data)


