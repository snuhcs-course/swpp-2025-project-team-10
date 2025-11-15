"""
Unit tests for accounts serializers.
Tests all serializers including authentication and user management.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserPreferences
from accounts.serializers import (
    GoogleAuthResponseSerializer,
    GoogleAuthSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    SocialAuthSerializer,
    UserPreferencesSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class UserRegistrationSerializerTestCase(TestCase):
    """Test cases for UserRegistrationSerializer."""

    def test_valid_registration_data(self):
        """Test serializer with valid registration data."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "User",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields(self):
        """Test serializer with missing required fields."""
        data = {
            "username": "newuser"
            # Missing email and password
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)

    def test_invalid_email_format(self):
        """Test serializer with invalid email format."""
        data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "securepass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_username(self):
        """Test serializer with duplicate username."""
        # Create existing user
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="pass123",
        )

        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "securepass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class UserSerializerTestCase(TestCase):
    """Test cases for UserSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_serialize_user(self):
        """Test serializing user data."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")

    def test_user_serializer_fields(self):
        """Test that serializer includes expected fields."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        expected_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        for field in expected_fields:
            self.assertIn(field, data)


class GoogleAuthSerializerTestCase(TestCase):
    """Test cases for GoogleAuthSerializer."""

    def test_valid_id_token(self):
        """Test serializer with valid ID token."""
        data = {"idToken": "valid_google_id_token_12345"}
        serializer = GoogleAuthSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["idToken"], "valid_google_id_token_12345"
        )

    def test_missing_id_token(self):
        """Test serializer with missing ID token."""
        data = {}
        serializer = GoogleAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("idToken", serializer.errors)

    def test_empty_id_token(self):
        """Test serializer with empty ID token."""
        data = {"idToken": ""}
        serializer = GoogleAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_field_name_camel_case(self):
        """Test that field name is in camelCase."""
        serializer = GoogleAuthSerializer()
        self.assertIn("idToken", serializer.fields)


class GoogleAuthResponseSerializerTestCase(TestCase):
    """Test cases for GoogleAuthResponseSerializer."""

    def test_valid_response_data(self):
        """Test serializer with valid response data."""
        data = {
            "ok": True,
            "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "message": "Google login successful",
        }
        serializer = GoogleAuthResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_response_with_error(self):
        """Test serializer with error response."""
        data = {
            "ok": False,
            "accessToken": None,
            "refreshToken": None,
            "message": "Authentication failed",
        }
        serializer = GoogleAuthResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_field_names_camel_case(self):
        """Test that all field names are in camelCase."""
        serializer = GoogleAuthResponseSerializer()
        expected_fields = ["ok", "accessToken", "refreshToken", "message"]
        for field in expected_fields:
            self.assertIn(field, serializer.fields)


class PasswordResetRequestSerializerTestCase(TestCase):
    """Test cases for PasswordResetRequestSerializer."""

    def test_valid_email(self):
        """Test serializer with valid email."""
        data = {"email": "user@example.com"}
        serializer = PasswordResetRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_email_format(self):
        """Test serializer with invalid email format."""
        data = {"email": "invalid-email"}
        serializer = PasswordResetRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_email(self):
        """Test serializer with missing email."""
        data = {}
        serializer = PasswordResetRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class SocialAuthSerializerTestCase(TestCase):
    """Test cases for SocialAuthSerializer."""

    def test_valid_social_auth_data(self):
        """Test serializer with valid social auth data."""
        data = {
            "provider": "google",
            "access_token": "valid_access_token_12345",
        }
        serializer = SocialAuthSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_provider(self):
        """Test serializer with missing provider."""
        data = {"access_token": "valid_access_token_12345"}
        serializer = SocialAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("provider", serializer.errors)

    def test_missing_access_token(self):
        """Test serializer with missing access token."""
        data = {"provider": "google"}
        serializer = SocialAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("access_token", serializer.errors)


class UserPreferencesSerializerTestCase(TestCase):
    """Test cases for UserPreferencesSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.preferences = UserPreferences.objects.create(
            user=self.user, email_notifications=True, push_notifications=False
        )

    def test_serialize_preferences(self):
        """Test serializing user preferences."""
        serializer = UserPreferencesSerializer(self.preferences)
        data = serializer.data

        self.assertIn("email_notifications", data)
        self.assertIn("push_notifications", data)

    def test_update_preferences(self):
        """Test updating user preferences."""
        data = {"email_notifications": False, "push_notifications": True}
        serializer = UserPreferencesSerializer(
            self.preferences, data=data, partial=True
        )
        self.assertTrue(serializer.is_valid())


class ProfileUpdateSerializerTestCase(TestCase):
    """Test cases for ProfileUpdateSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_valid_profile_update(self):
        """Test serializer with valid profile update data."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio",
        }
        serializer = ProfileUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_partial_profile_update(self):
        """Test partial profile update."""
        data = {"first_name": "Updated"}
        serializer = ProfileUpdateSerializer(
            self.user, data=data, partial=True
        )
        self.assertTrue(serializer.is_valid())


class CustomTokenObtainPairSerializerTestCase(TestCase):
    """Test cases for CustomTokenObtainPairSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="activeuser",
            email="active@test.com",
            password="pass123",
            first_name="Active",
            last_name="User",
        )

    def test_inactive_user_login(self):
        """Test login with inactive user account."""
        from accounts.serializers import CustomTokenObtainPairSerializer
        
        # Deactivate user
        self.user.is_active = False
        self.user.save()

        serializer = CustomTokenObtainPairSerializer(data={
            "username": "activeuser",
            "password": "pass123",
        })

        with self.assertRaises(Exception):
            serializer.validate({"username": "activeuser", "password": "pass123"})

    def test_missing_credentials(self):
        """Test login without username or password."""
        from accounts.serializers import CustomTokenObtainPairSerializer
        
        serializer = CustomTokenObtainPairSerializer(data={})

        with self.assertRaises(Exception):
            serializer.validate({})


class SocialAuthSerializerTestCase(TestCase):
    """Test cases for SocialAuthSerializer."""

    def test_valid_social_auth_data(self):
        """Test serializer with valid social auth data."""
        data = {
            "provider": "google",
            "access_token": "valid_token_123"
        }
        serializer = SocialAuthSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_provider(self):
        """Test serializer with missing provider."""
        data = {
            "access_token": "valid_token_123"
        }
        serializer = SocialAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_missing_access_token(self):
        """Test serializer with missing access token."""
        data = {
            "provider": "google"
        }
        serializer = SocialAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_provider(self):
        """Test serializer with invalid provider."""
        data = {
            "provider": "invalid_provider",
            "access_token": "valid_token_123"
        }
        serializer = SocialAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class GoogleAuthSerializerTestCase(TestCase):
    """Test cases for GoogleAuthSerializer."""

    def test_valid_id_token(self):
        """Test serializer with valid ID token."""
        data = {"idToken": "valid_google_id_token"}
        serializer = GoogleAuthSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_id_token(self):
        """Test serializer with missing ID token."""
        data = {}
        serializer = GoogleAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_empty_id_token(self):
        """Test serializer with empty ID token."""
        data = {"idToken": ""}
        serializer = GoogleAuthSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class PasswordResetSerializerTestCase(TestCase):
    """Test cases for password reset serializers."""

    def test_password_too_short(self):
        """Test password validation for too short password."""
        from accounts.serializers import UserRegistrationSerializer
        
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "short",  # Less than 6 chars
            "first_name": "Test",
            "last_name": "User"
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_password_no_letter(self):
        """Test password validation for password without letters."""
        from accounts.serializers import UserRegistrationSerializer
        
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "123456",  # No letters
            "first_name": "Test",
            "last_name": "User"
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
