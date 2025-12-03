"""
Serializers for the accounts app.
Handles user authentication, registration, and profile management.
"""

from books.models import BookReview, BookWishlist
from books.serializers import BookSummarySerializer, ReviewSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, UserPreferences, UserTaste


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
    has_initial_taste = serializers.BooleanField(read_only=True)

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
            "has_initial_taste",
        )
        read_only_fields = (
            "id",
            "reputation_score",
            "successful_trades",
            "created_at",
            "has_initial_taste",
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


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for user profile tab.
    Returns all profile info including computed stats, taste, preferences, and library.
    """

    # Computed counts
    follower_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()

    # Nested related data
    taste = serializers.SerializerMethodField()
    preferences = UserPreferencesSerializer(read_only=True)

    # Library and wishlist (from books app)
    library_count = serializers.SerializerMethodField()
    wishlist_count = serializers.SerializerMethodField()

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
            "has_initial_taste",
            "follower_count",
            "following_count",
            "post_count",
            "library_count",
            "wishlist_count",
            "taste",
            "preferences",
            "created_at",
            "last_active",
        )
        read_only_fields = (
            "id",
            "reputation_score",
            "successful_trades",
            "has_initial_taste",
            "created_at",
        )

    def get_taste(self, obj):
        """Return taste data if user completed initial taste survey."""
        if obj.has_initial_taste:
            try:
                return UserTasteSerializer(obj.taste).data
            except UserTaste.DoesNotExist:
                return None
        return None

    def get_library_count(self, obj):
        """Return count of books user owns."""
        return obj.books.count()

    def get_wishlist_count(self, obj):
        """Return count of books in user's wishlist."""
        return obj.wishlist.count()


class UserBarterInfoSerializer(serializers.ModelSerializer):
    """
    Rich user info payload to attach to barter requests/notifications.
    Includes counts and compact lists for library and wishlist.
    """

    follower_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()
    profilePicture = serializers.SerializerMethodField()

    library = serializers.SerializerMethodField()
    wishlist = serializers.SerializerMethodField()
    taste = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    reviewCount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "bio",
            "location",
            "follower_count",
            "following_count",
            "post_count",
            "profilePicture",
            "library",
            "wishlist",
            "taste",
            "reviews",
            "reviewCount",
        )

    def get_profilePicture(self, obj):
        request = self.context.get("request")
        if obj.profile_picture:
            return (
                request.build_absolute_uri(obj.profile_picture.url)
                if request
                else obj.profile_picture.url
            )
        return None

    def get_library(self, obj):
        # All books owned by the user (use reverse relation to avoid import ambiguity)
        qs = obj.book_copies.select_related("publication").prefetch_related(
            "publication__authors"
        )
        return BookSummarySerializer(qs, many=True, context=self.context).data

    def get_wishlist(self, obj):
        qs = (
            BookWishlist.objects.filter(user=obj)
            .select_related("book__publication")
            .prefetch_related("book__publication__authors")
        )
        books = [item.book for item in qs]
        return BookSummarySerializer(
            books, many=True, context=self.context
        ).data

    def get_taste(self, obj):
        """Return the user's full taste profile."""
        try:
            taste = obj.taste
        except UserTaste.DoesNotExist:
            return None

        data = UserTasteSerializer(taste, context=self.context).data
        return data

    def get_distance_km(self, obj):
        """Compute approximate distance (km) from request.user to obj without exposing coords."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        me = request.user
        if not (
            me.latitude and me.longitude and obj.latitude and obj.longitude
        ):
            return None

        from math import atan2, cos, radians, sin, sqrt

        try:
            lat1 = float(me.latitude)
            lon1 = float(me.longitude)
            lat2 = float(obj.latitude)
            lon2 = float(obj.longitude)
        except (TypeError, ValueError):
            return None

        # Haversine formula
        earth_radius_km = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        km = earth_radius_km * c
        return round(km, 2)

    def get_reviews(self, obj):
        """All reviews written by this user (as seen in their user tab)."""
        qs = (
            BookReview.objects.filter(reviewer=obj)
            .select_related("reviewer")
            .prefetch_related("helpful_votes")
            .order_by("-created_at")
        )
        return ReviewSerializer(qs, many=True, context=self.context).data

    def get_reviewCount(self, obj):
        return BookReview.objects.filter(reviewer=obj).count()


class UserTasteSerializer(serializers.ModelSerializer):
    """
    Serializer for user's book preferences and taste information.
    """

    # TextChoices가 아닌 실제 모델의 ID 리스트를 받도록 수정
    favorite_genres = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    favorite_authors = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    favorite_books = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    # Trade style fields (optional, can be set later from profile)
    trade_place_name = serializers.CharField(
        max_length=120, required=False, allow_blank=True
    )
    trade_address = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )

    class Meta:
        model = UserTaste
        fields = (
            "favorite_genres",
            "favorite_authors",
            "favorite_books",
            "trade_place_name",
            "trade_address",
            "current_step",
        )
        read_only_fields = ("current_step",)

    def validate_favorite_genres(self, value):
        # 실제 Genre 모델 ID가 존재하는지 검증 (선택 사항)
        return value

    def validate_favorite_authors(self, value):
        # 실제 Author 모델 ID가 존재하는지 검증 (선택 사항)
        return value

    def validate_favorite_books(self, value):
        # 실제 BookPublication 모델 ID(UUID)가 존재하는지 검증 (선택 사항)
        return value


class OnboardingSerializer(serializers.Serializer):
    """Serializer for onboarding data submission."""

    book_ids = serializers.ListField(child=serializers.CharField(), required=False)
    author_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    genre_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
