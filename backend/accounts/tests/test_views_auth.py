"""
Unit tests for authentication views.
Tests login, signup, token refresh, and password reset.
"""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class LoginViewTestCase(TestCase):
    """Test cases for login view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = "/auth/login/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_login_success(self):
        """Test successful login."""
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))
        self.assertIn("accessToken", response.data)
        self.assertIn("refreshToken", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get("ok"))

    def test_login_missing_username(self):
        """Test login with missing username."""
        data = {"password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        """Test login with missing password."""
        data = {"username": "testuser"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        data = {"username": "nonexistent", "password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SignupViewTestCase(TestCase):
    """Test cases for signup view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.signup_url = "/auth/signup/"

    def test_signup_success(self):
        """Test successful user registration."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("ok"))
        self.assertIn("user", response.data)

        # Verify user was created
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")

    def test_signup_duplicate_username(self):
        """Test signup with duplicate username."""
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
        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get("ok"))

    def test_signup_duplicate_email(self):
        """Test signup with duplicate email."""
        # Create existing user
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="pass123",
        )

        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "securepass123",
        }
        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_email(self):
        """Test signup with invalid email format."""
        data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "securepass123",
        }
        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_missing_required_fields(self):
        """Test signup with missing required fields."""
        data = {"username": "newuser"}
        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTestCase(TestCase):
    """Test cases for token refresh view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = "/auth/login/"
        self.refresh_url = "/auth/token/refresh/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        # First login to get tokens
        login_data = {"username": "testuser", "password": "testpass123"}
        login_response = self.client.post(
            self.login_url, login_data, format="json"
        )

        refresh_token = login_response.data.get("refreshToken")

        # Refresh the token
        refresh_data = {"refresh": refresh_token}
        response = self.client.post(
            self.refresh_url, refresh_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("accessToken", response.data)

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        data = {"refresh": "invalid_token"}
        response = self.client.post(self.refresh_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_missing_token(self):
        """Test token refresh with missing token."""
        data = {}
        response = self.client.post(self.refresh_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetViewTestCase(TestCase):
    """Test cases for password reset views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.reset_start_url = "/auth/forgot/start/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        cache.clear()

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_password_reset_request_success(self):
        """Test successful password reset request."""
        data = {"email": "test@example.com"}
        response = self.client.post(self.reset_start_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))
        self.assertIn("requestId", response.data)

    def test_password_reset_nonexistent_email(self):
        """Test password reset with nonexistent email."""
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.reset_start_url, data, format="json")

        # Should still return success for security reasons
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_invalid_email(self):
        """Test password reset with invalid email format."""
        data = {"email": "invalid-email"}
        response = self.client.post(self.reset_start_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_missing_email(self):
        """Test password reset with missing email."""
        data = {}
        response = self.client.post(self.reset_start_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
