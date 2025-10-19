"""
Serializers for the accounts app.
Handles user authentication, registration, and profile management.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserPreferences


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that matches frontend expectations.
    """

    username_field = "username"  # Can be email or username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field and add custom fields
        self.fields.pop("username", None)
        self.fields["username"] = serializers.CharField()
        self.fields["password"] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            # Since USERNAME_FIELD = 'email', we need to handle both cases
            user = None

            if "@" in username:
                # Looks like email - authenticate directly
                user = authenticate(
                    request=self.context.get("request"),
                    username=username,
                    password=password,
                )
            else:
                # Looks like username - find user by username and authenticate with email
                try:
                    user_obj = User.objects.get(username=username)
                    user = authenticate(
                        request=self.context.get("request"),
                        username=user_obj.email,
                        password=password,
                    )
                except User.DoesNotExist:
                    pass

            if not user:
                raise serializers.ValidationError("Invalid credentials")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")

            # Get tokens
            refresh = self.get_token(user)

            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }
        else:
            raise serializers.ValidationError(
                "Must include username and password"
            )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration matching frontend SignUpRequest.
    """

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_username(self, value):
        """Validate username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        """Validate password meets requirements."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        # Additional validation to match frontend requirements
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters long"
            )

        # Check for at least one letter (matching frontend regex)
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one letter"
            )

        return value

    def create(self, validated_data):
        """Create new user with encrypted password."""
        password = validated_data.pop("password")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=password,
        )

        # Create user preferences
        UserPreferences.objects.create(user=user)

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """

    follower_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    books_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "location",
            "birth_date",
            "profile_picture",
            "phone_number",
            "is_profile_public",
            "allow_direct_messages",
            "reputation_score",
            "successful_trades",
            "follower_count",
            "following_count",
            "books_count",
            "created_at",
            "last_active",
        )
        read_only_fields = (
            "id",
            "reputation_score",
            "successful_trades",
            "created_at",
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request (forgot password).
    Note: We don't validate if email exists for security reasons
    (to prevent email enumeration attacks).
    """

    email = serializers.EmailField()


class PasswordResetVerifySerializer(serializers.Serializer):
    """
    Serializer for password reset verification.
    """

    request_id = serializers.CharField()
    code = serializers.CharField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """

    password = serializers.CharField(min_length=6)

    def validate_password(self, value):
        """Validate new password."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class SocialAuthSerializer(serializers.Serializer):
    """
    Serializer for social authentication.
    """

    provider = serializers.ChoiceField(choices=["google", "facebook", "kakao"])
    access_token = serializers.CharField()

    def validate(self, attrs):
        """Validate social auth token."""
        provider = attrs.get("provider")
        access_token = attrs.get("access_token")

        # Here you would validate the token with the respective provider
        # For now, we'll implement basic validation
        if not provider:
            raise serializers.ValidationError("Provider is required")

        if not access_token:
            raise serializers.ValidationError("Access token is required")

        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google ID Token authentication.
    Matches frontend GoogleAuthRequest format.
    """

    idToken = serializers.CharField()

    def validate_idToken(self, value):
        """Validate Google ID token format."""
        if not value:
            raise serializers.ValidationError("Google ID token is required")
        return value


class GoogleAuthResponseSerializer(serializers.Serializer):
    """
    Serializer for Google authentication response.
    Matches frontend GoogleAuthResponse format.
    """

    ok = serializers.BooleanField()
    accessToken = serializers.CharField(required=False, allow_null=True)
    refreshToken = serializers.CharField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.
    """

    class Meta:
        model = UserPreferences
        exclude = ("user",)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "bio",
            "location",
            "birth_date",
            "profile_picture",
            "phone_number",
            "is_profile_public",
            "allow_direct_messages",
        )

    def validate_profile_picture(self, value):
        """Validate profile picture size."""
        if value and value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError(
                "Profile picture must be less than 5MB"
            )
        return value


class KakaoAuthSerializer(serializers.Serializer):
    """Serializer for Kakao access token authentication."""

    accessToken = serializers.CharField()

    def validate_accessToken(self, value):
        if not value:
            raise serializers.ValidationError("Kakao access token is required")
        return value


class KakaoAuthResponseSerializer(serializers.Serializer):
    """Serializer for Kakao authentication response."""

    ok = serializers.BooleanField()
    accessToken = serializers.CharField(required=False, allow_null=True)
    refreshToken = serializers.CharField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)
