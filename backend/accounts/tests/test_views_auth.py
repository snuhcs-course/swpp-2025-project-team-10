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


# Additional pytest-based tests for coverage

import pytest


@pytest.mark.django_db
def test_user_registration_invalid_password():
    """Test user registration with invalid passwords."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    
    # Password too short
    res = client.post(
        reverse("accounts:signup"),
        {
            "username": "newuser",
            "email": "new@test.com",
            "password": "12345",
            "first_name": "New",
            "last_name": "User",
        },
        format="json",
    )
    assert res.status_code == 400
    
    # Password without letter
    res = client.post(
        reverse("accounts:signup"),
        {
            "username": "newuser2",
            "email": "new2@test.com",
            "password": "123456",
            "first_name": "New",
            "last_name": "User",
        },
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_user_registration_serializer_password_validation():
    """Test registration serializer validates password."""
    from accounts.serializers import UserRegistrationSerializer
    
    # Valid password
    serializer = UserRegistrationSerializer(data={
        "username": "test",
        "email": "test@test.com",
        "password": "validpass123",
        "first_name": "Test",
        "last_name": "User",
    })
    assert serializer.is_valid()
    
    # Too short
    serializer = UserRegistrationSerializer(data={
        "username": "test2",
        "email": "test2@test.com",
        "password": "short",
        "first_name": "Test",
        "last_name": "User",
    })
    assert not serializer.is_valid()
    
    # No letter
    serializer = UserRegistrationSerializer(data={
        "username": "test3",
        "email": "test3@test.com",
        "password": "123456789",
        "first_name": "Test",
        "last_name": "User",
    })
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_user_registration_success():
    """Test successful user registration via UserRegistrationView."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    
    res = client.post(
        reverse("accounts:signup"),
        {
            "username": "newuser",
            "email": "new@test.com",
            "password": "validpass123",
            "first_name": "New",
            "last_name": "User",
        },
        format="json",
    )
    assert res.status_code in [200, 201]
    
    # Verify user was created
    user = User.objects.filter(username="newuser").first()
    assert user is not None
    assert user.email == "new@test.com"


@pytest.mark.django_db
def test_login_success():
    """Test successful login via CustomTokenObtainPairView."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    
    # Create user
    user = User.objects.create(username="testuser", email="test@test.com", first_name="Test", last_name="User")
    user.set_password("testpass123")
    user.save()
    
    # Login
    res = client.post(
        reverse("accounts:login"),
        {
            "username": "testuser",
            "password": "testpass123",
        },
        format="json",
    )
    assert res.status_code == 200
    assert "accessToken" in res.data
    assert "refreshToken" in res.data
    assert res.data["ok"] is True


@pytest.mark.django_db
def test_token_refresh():
    """Test token refresh endpoint."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    
    # Create and login user first
    user = User.objects.create(username="testuser2", email="test2@test.com", first_name="Test", last_name="User")
    user.set_password("testpass123")
    user.save()
    
    login_res = client.post(
        reverse("accounts:login"),
        {"username": "testuser2", "password": "testpass123"},
        format="json",
    )
    
    refresh_token = login_res.data["refreshToken"]
    
    # Test refresh
    res = client.post(
        reverse("accounts:token_refresh"),
        {"refresh": refresh_token},
        format="json",
    )
    
    assert res.status_code == 200
    assert "accessToken" in res.data


@pytest.mark.django_db
def test_user_registration_duplicate_username():
    """Test registration with duplicate username."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    
    # Create existing user
    User.objects.create(username="existing", email="existing@test.com", first_name="E", last_name="User")
    
    res = client.post(
        reverse("accounts:signup"),
        {
            "username": "existing",
            "email": "new@test.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "New",
            "last_name": "User",
        },
        format="json",
    )
    
    assert res.status_code == 400


@pytest.mark.django_db
def test_login_with_email():
    """Test login using email instead of username."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    user = User.objects.create(username="user9", email="test9@test.com", first_name="U", last_name="ser")
    user.set_password("testpass123")
    user.save()
    
    # Login with email
    res = client.post(
        reverse("accounts:login"),
        {"username": "test9@test.com", "password": "testpass123"},
        format="json",
    )
    
    assert res.status_code == 200
    assert "accessToken" in res.data


@pytest.mark.django_db
def test_login_wrong_password():
    """Test login with wrong password."""
    from rest_framework.test import APIClient
    from django.urls import reverse
    
    client = APIClient()
    user = User.objects.create(username="user10", email="u10@test.com", first_name="U", last_name="ser")
    user.set_password("correctpass")
    user.save()
    
    res = client.post(
        reverse("accounts:login"),
        {"username": "user10", "password": "wrongpass"},
        format="json",
    )
    
    assert res.status_code == 400
