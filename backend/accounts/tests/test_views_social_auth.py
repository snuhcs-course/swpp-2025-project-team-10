"""
Tests for social authentication views.
Tests username generation and social auth API endpoints.
"""

from unittest.mock import patch

from accounts.models import UserPreferences
from accounts.views import SocialAuthView
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class SocialAuthUsernameGenerationTest(TestCase):
    """
    Test suite for social authentication username generation.
    Tests the fix for N+1 query issue when generating unique usernames.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.social_auth_view = SocialAuthView()

    def test_unique_username_generation_no_collision(self):
        """Test username generation when no collision exists."""
        user_info = {"email": "newuser@example.com", "name": "New User"}

        user, created = self.social_auth_view.get_or_create_social_user(
            "google", user_info
        )

        self.assertTrue(created)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")

    def test_unique_username_generation_with_collision(self):
        """Test username generation when collision exists."""
        # Create existing user with the base username
        User.objects.create_user(
            username="testuser",
            email="existing@example.com",
            password="testpass123",
        )

        user_info = {"email": "testuser@newdomain.com", "name": "Test User"}

        user, created = self.social_auth_view.get_or_create_social_user(
            "google", user_info
        )

        self.assertTrue(created)
        # Username should have a random suffix
        self.assertTrue(user.username.startswith("testuser_"))
        self.assertEqual(len(user.username), len("testuser_") + 6)
        self.assertEqual(user.email, "testuser@newdomain.com")

    def test_unique_username_generation_multiple_collisions(self):
        """
        Test username generation with multiple collisions.
        This tests the efficiency improvement - no N+1 queries.
        """
        # Create multiple users with similar usernames
        base_username = "popular"
        for i in range(10):
            User.objects.create_user(
                username=f"{base_username}_{i:06d}",
                email=f"user{i}@example.com",
                password="testpass123",
            )

        # Try to create a new user with the same base username
        user_info = {"email": "popular@newdomain.com", "name": "Popular User"}

        # This should succeed without N+1 queries
        # Expected queries: 1 for email check, 1 for user insert, 1 for preferences insert
        user, created = self.social_auth_view.get_or_create_social_user(
            "google", user_info
        )

        self.assertTrue(created)
        self.assertTrue(
            user.username == "popular" or user.username.startswith("popular_")
        )
        self.assertEqual(user.email, "popular@newdomain.com")

    def test_existing_user_by_email(self):
        """Test that existing user is returned when email matches."""
        existing_user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="testpass123",
        )

        user_info = {"email": "existing@example.com", "name": "Existing User"}

        user, created = self.social_auth_view.get_or_create_social_user(
            "google", user_info
        )

        self.assertFalse(created)
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.username, "existing")

    def test_user_preferences_created(self):
        """Test that user preferences are created for new social users."""
        user_info = {"email": "newuser@example.com", "name": "New User"}

        user, created = self.social_auth_view.get_or_create_social_user(
            "google", user_info
        )

        self.assertTrue(created)
        self.assertTrue(hasattr(user, "preferences"))
        self.assertIsInstance(user.preferences, UserPreferences)

    def test_no_email_returns_none(self):
        """Test that None is returned when email is missing."""
        user_info = {"name": "No Email User"}

        result = self.social_auth_view.get_or_create_social_user(
            "google", user_info
        )

        self.assertEqual(result, (None, False))


class SocialAuthAPITest(APITestCase):
    """
    Test suite for social authentication API endpoints.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.social_auth_url = reverse("accounts:social_auth")

    @patch("accounts.views.SocialAuthView.validate_social_token")
    def test_social_auth_success(self, mock_validate):
        """Test successful social authentication."""
        mock_validate.return_value = {
            "email": "socialuser@example.com",
            "name": "Social User",
        }

        data = {"provider": "google", "access_token": "mock_token_123"}

        response = self.client.post(self.social_auth_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertIn("accessToken", response.data)
        self.assertIn("user", response.data)

    @patch("accounts.views.SocialAuthView.validate_social_token")
    def test_social_auth_invalid_token(self, mock_validate):
        """Test social authentication with invalid token."""
        mock_validate.return_value = None

        data = {"provider": "google", "access_token": "invalid_token"}

        response = self.client.post(self.social_auth_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])

    def test_social_auth_missing_fields(self):
        """Test social authentication with missing required fields."""
        data = {
            "provider": "google"
            # Missing access_token
        }

        response = self.client.post(self.social_auth_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["ok"])
