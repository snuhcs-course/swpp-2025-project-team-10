"""
Unit tests for Google OAuth authentication views.
Tests Google login and signup endpoints.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class GoogleLoginViewTestCase(TestCase):
    """Test cases for Google login view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.google_login_url = "/auth/login/google/"

        # Mock Google user info
        self.mock_google_user_info = {
            "iss": "accounts.google.com",
            "email": "testuser@gmail.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "sub": "1234567890",
            "picture": "https://example.com/photo.jpg",
            "email_verified": True,
        }

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_success_new_user(self, mock_verify):
        """Test successful Google login with new user creation."""
        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_google_id_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertIn("accessToken", response.data)
        self.assertIn("refreshToken", response.data)
        self.assertEqual(response.data["message"], "Google login successful")

        # Verify user was created
        user = User.objects.get(email="testuser@gmail.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_success_existing_user(self, mock_verify):
        """Test successful Google login with existing user."""
        # Create existing user
        User.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="testpass123",
        )

        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_google_id_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

        # Verify no duplicate user was created
        self.assertEqual(
            User.objects.filter(email="testuser@gmail.com").count(), 1
        )

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_invalid_token(self, mock_verify):
        """Test Google login with invalid token."""
        mock_verify.side_effect = ValueError("Invalid token")

        data = {"idToken": "invalid_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])
        self.assertEqual(response.data["message"], "Invalid Google ID token")

    def test_google_login_missing_token(self):
        """Test Google login without providing token."""
        data = {}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_wrong_issuer(self, mock_verify):
        """Test Google login with wrong issuer."""
        wrong_issuer_info = self.mock_google_user_info.copy()
        wrong_issuer_info["iss"] = "wrong.issuer.com"
        mock_verify.return_value = wrong_issuer_info

        data = {"idToken": "valid_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_username_conflict_resolution(self, mock_verify):
        """Test username conflict resolution during Google login."""
        # Create existing user with same username
        User.objects.create_user(
            username="testuser",
            email="existing@example.com",
            password="testpass123",
        )

        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

        # Verify new user was created with different username
        new_user = User.objects.get(email="testuser@gmail.com")
        self.assertNotEqual(new_user.username, "testuser")
        self.assertTrue(new_user.username.startswith("testuser_"))

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_token_format(self, mock_verify):
        """Test that JWT tokens are properly formatted."""
        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify token format (JWT tokens have 3 parts separated by dots)
        access_token = response.data["accessToken"]
        refresh_token = response.data["refreshToken"]

        self.assertEqual(len(access_token.split(".")), 3)
        self.assertEqual(len(refresh_token.split(".")), 3)

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_login_response_structure(self, mock_verify):
        """Test that response structure matches frontend expectations."""
        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_token"}
        response = self.client.post(self.google_login_url, data, format="json")

        # Verify response structure
        self.assertIn("ok", response.data)
        self.assertIn("accessToken", response.data)
        self.assertIn("refreshToken", response.data)
        self.assertIn("message", response.data)

        # Verify types
        self.assertIsInstance(response.data["ok"], bool)
        self.assertIsInstance(response.data["accessToken"], str)
        self.assertIsInstance(response.data["refreshToken"], str)
        self.assertIsInstance(response.data["message"], str)


class GoogleSignupViewTestCase(TestCase):
    """Test cases for Google signup view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.google_signup_url = "/auth/signup/google/"

        # Mock Google user info
        self.mock_google_user_info = {
            "iss": "accounts.google.com",
            "email": "newuser@gmail.com",
            "name": "New User",
            "given_name": "New",
            "family_name": "User",
            "sub": "9876543210",
            "picture": "https://example.com/photo.jpg",
            "email_verified": True,
        }

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_signup_success(self, mock_verify):
        """Test successful Google signup."""
        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_google_id_token"}
        response = self.client.post(
            self.google_signup_url, data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertIn("accessToken", response.data)
        self.assertIn("refreshToken", response.data)
        self.assertEqual(response.data["message"], "Google signup successful")

        # Verify user was created
        user = User.objects.get(email="newuser@gmail.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_signup_existing_user(self, mock_verify):
        """Test Google signup with existing user (should login)."""
        # Create existing user
        User.objects.create_user(
            username="existinguser",
            email="newuser@gmail.com",
            password="testpass123",
        )

        mock_verify.return_value = self.mock_google_user_info

        data = {"idToken": "valid_google_id_token"}
        response = self.client.post(
            self.google_signup_url, data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

        # Verify no duplicate user was created
        self.assertEqual(
            User.objects.filter(email="newuser@gmail.com").count(), 1
        )

    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_signup_invalid_token(self, mock_verify):
        """Test Google signup with invalid token."""
        mock_verify.side_effect = ValueError("Invalid token")

        data = {"idToken": "invalid_token"}
        response = self.client.post(
            self.google_signup_url, data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])

    def test_google_signup_missing_token(self):
        """Test Google signup without providing token."""
        data = {}
        response = self.client.post(
            self.google_signup_url, data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])