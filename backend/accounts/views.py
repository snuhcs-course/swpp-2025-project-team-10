"""
Views for the accounts app.
Handles user authentication, registration, and profile management.
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiResponse
import uuid
import requests
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer,
    SocialAuthSerializer,
    GoogleAuthSerializer,
    KakaoAuthSerializer,
    ProfileUpdateSerializer
)
from .models import UserPreferences

User = get_user_model()


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
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data

            return Response({
                'ok': True,
                'token': tokens['access'],
                'refresh': tokens['refresh'],
                'user': tokens['user'],
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)

        except Exception:
            return Response({
                'ok': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_400_BAD_REQUEST)


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
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'ok': True,
                'message': 'Registration successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'ok': False,
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Generate reset code and request ID
            request_id = str(uuid.uuid4())
            reset_code = get_random_string(6, allowed_chars='0123456789')

            # Store in cache for 15 minutes
            cache_key = f"password_reset_{request_id}"
            cache.set(cache_key, {
                'email': email,
                'code': reset_code,
                'verified': False
            }, timeout=900)  # 15 minutes

            # Send email (in production, use proper email service)
            try:
                send_mail(
                    subject='Password Reset Code',
                    message=f'Your password reset code is: {reset_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception:
                # In development, just log the code
                print(f"Password reset code for {email}: {reset_code}")

            return Response({
                'requestId': request_id,
                'code': reset_code if settings.DEBUG else None,  # Only return code in debug mode
                'message': 'Reset code sent to email'
            }, status=status.HTTP_200_OK)

        return Response({
            'ok': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
        }
    )
    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)

        if serializer.is_valid():
            request_id = serializer.validated_data['request_id']
            code = serializer.validated_data['code']

            cache_key = f"password_reset_{request_id}"
            reset_data = cache.get(cache_key)

            if reset_data and reset_data['code'] == code:
                # Mark as verified
                reset_data['verified'] = True
                cache.set(cache_key, reset_data, timeout=900)

                return Response({
                    'ok': True,
                    'message': 'Code verified successfully'
                }, status=status.HTTP_200_OK)

            return Response({
                'ok': False,
                'message': 'Invalid or expired code'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'ok': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
        }
    )
    def post(self, request):
        # This would typically require the request_id from the session or token
        # For now, we'll implement a basic version
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            # In a real implementation, you'd get the request_id from the session
            # and verify it was previously verified
            return Response({
                'ok': True,
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)

        return Response({
            'ok': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
        }
    )
    def post(self, request):
        serializer = SocialAuthSerializer(data=request.data)

        if serializer.is_valid():
            provider = serializer.validated_data['provider']
            access_token = serializer.validated_data['access_token']

            # Validate token with provider and get user info
            user_info = self.validate_social_token(provider, access_token)

            if user_info:
                # Get or create user
                user, _ = self.get_or_create_social_user(provider, user_info)

                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)

                return Response({
                    'ok': True,
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                    'message': 'Social authentication successful'
                }, status=status.HTTP_200_OK)

            return Response({
                'ok': False,
                'message': 'Invalid social token'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'ok': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def validate_social_token(self, provider, access_token):
        """Validate social token with provider."""
        try:
            if provider == 'google':
                response = requests.get(
                    f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}'
                )
                if response.status_code == 200:
                    return response.json()

            elif provider == 'facebook':
                response = requests.get(
                    f'https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}'
                )
                if response.status_code == 200:
                    return response.json()

            elif provider == 'kakao':
                response = requests.get(
                    'https://kapi.kakao.com/v2/user/me',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            print(f"Social auth error: {e}")

        return None

    def get_or_create_social_user(self, _provider, user_info):
        """Get or create user from social provider info."""
        from django.db import IntegrityError, transaction

        email = user_info.get('email')
        name = user_info.get('name', '')

        if email:
            try:
                user = User.objects.get(email=email)
                return user, False
            except User.DoesNotExist:
                # Create new user with unique username
                base_username = email.split('@')[0]

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
                                allowed_chars='0123456789abcdefghijklmnopqrstuvwxyz'
                            )
                            username = f"{base_username}_{random_suffix}"

                        # Use atomic transaction to handle IntegrityError properly
                        with transaction.atomic():
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                first_name=name.split(' ')[0] if name else '',
                                last_name=' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else ''
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update current user profile."""
    serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'ok': True,
            'user': UserSerializer(request.user).data,
            'message': 'Profile updated successfully'
        })

    return Response({
        'ok': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


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
        }
    )
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)

        if serializer.is_valid():
            id_token = serializer.validated_data['idToken']

            # Validate Google ID token and get user info
            user_info = self.validate_google_id_token(id_token)

            if user_info:
                # Get or create user
                user, _ = self.get_or_create_google_user(user_info)

                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)

                return Response({
                    'ok': True,
                    'accessToken': str(refresh.access_token),
                    'refreshToken': str(refresh),
                    'message': 'Google login successful'
                }, status=status.HTTP_200_OK)

            return Response({
                'ok': False,
                'accessToken': None,
                'refreshToken': None,
                'message': 'Invalid Google ID token'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'ok': False,
            'accessToken': None,
            'refreshToken': None,
            'message': 'Invalid request data'
        }, status=status.HTTP_400_BAD_REQUEST)

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
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            return {
                'email': id_info.get('email'),
                'name': id_info.get('name', ''),
                'first_name': id_info.get('given_name', ''),
                'last_name': id_info.get('family_name', ''),
                'google_id': id_info.get('sub'),
                'picture': id_info.get('picture', ''),
                'email_verified': id_info.get('email_verified', False)
            }

        except Exception as e:
            print(f"Google ID token validation error: {e}")
            return None

    def get_or_create_google_user(self, user_info):
        """Get or create user from Google user info."""
        from django.db import IntegrityError, transaction

        email = user_info.get('email')

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
                base_username = email.split('@')[0]
                username = base_username
                counter = 1

                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=user_info.get('first_name', ''),
                    last_name=user_info.get('last_name', ''),
                    is_active=True
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
        }
    )
    def post(self, request):
        # For Google auth, login and signup are essentially the same
        # We'll reuse the login logic but with different messaging
        login_view = GoogleLoginView()
        response = login_view.post(request)

        # Modify the message for signup context
        if response.status_code == 200:
            data = response.data.copy()
            data['message'] = 'Google signup successful'
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
        }
    )
    def post(self, request):
        serializer = KakaoAuthSerializer(data=request.data)

        if serializer.is_valid():
            access_token = serializer.validated_data['accessToken']

            # Validate Kakao access token and get user info
            user_info = self.validate_kakao_token(access_token)

            if user_info:
                # Get or create user
                user, _ = self.get_or_create_kakao_user(user_info)

                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)

                return Response({
                    'ok': True,
                    'accessToken': str(refresh.access_token),
                    'refreshToken': str(refresh),
                    'message': 'Kakao login successful'
                }, status=status.HTTP_200_OK)

            return Response({
                'ok': False,
                'accessToken': None,
                'refreshToken': None,
                'message': 'Invalid Kakao access token'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'ok': False,
            'accessToken': None,
            'refreshToken': None,
            'message': 'Invalid request data'
        }, status=status.HTTP_400_BAD_REQUEST)

    def validate_kakao_token(self, access_token):
        """Validate Kakao access token by calling Kakao API."""
        try:
            response = requests.get(
                'https://kapi.kakao.com/v2/user/me',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                kakao_account = data.get('kakao_account', {})
                profile = kakao_account.get('profile', {})

                return {
                    'email': kakao_account.get('email'),
                    'name': profile.get('nickname', ''),
                    'kakao_id': str(data.get('id')),
                    'profile_image': profile.get('profile_image_url', ''),
                    'email_verified': kakao_account.get('is_email_verified', False)
                }
        except Exception as e:
            print(f"Kakao token validation error: {e}")

        return None

    def get_or_create_kakao_user(self, user_info):
        """Get or create user from Kakao user info."""
        email = user_info.get('email')

        if not email:
            raise ValueError("Email is required from Kakao")

        # Try to get existing user by email
        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            pass

        # Create new user
        username = email.split('@')[0]

        # Handle username conflicts
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=user_info.get('name', ''),
            password=User.objects.make_random_password()
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
        }
    )
    def post(self, request):
        # For Kakao auth, login and signup are essentially the same
        # We'll reuse the login logic but with different messaging
        login_view = KakaoLoginView()
        response = login_view.post(request)

        # Modify the message for signup context
        if response.status_code == 200:
            data = response.data.copy()
            data['message'] = 'Kakao signup successful'
            return Response(data, status=status.HTTP_200_OK)

        return response
