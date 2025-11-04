"""
Tests for /accounts/profile/me/ endpoint.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserTaste

User = get_user_model()


class UserProfileMeEndpointTestCase(TestCase):
    """Test cases for /accounts/profile/me/ endpoint."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            bio="Test bio",
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/accounts/profile/me/"

    def test_get_profile_me_success(self):
        """Test GET /accounts/profile/me/ returns user profile."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["bio"], "Test bio")
        self.assertIn("preferences", response.data)
        self.assertIsNotNone(response.data["preferences"])

    def test_get_profile_me_includes_preferences_object(self):
        """Test that preferences object is always included to prevent NPE."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("preferences", response.data)
        prefs = response.data["preferences"]
        
        # All preference fields should exist (nullable)
        self.assertIn("tradeLocation1", prefs)
        self.assertIn("tradeSpot1", prefs)
        self.assertIn("favBook", prefs)

    def test_get_profile_me_with_taste_data(self):
        """Test GET returns taste data when user has UserTaste."""
        taste = UserTaste.objects.create(
            user=self.user,
            trade_place_name="Test Location",
            trade_address="Test Spot",
            favorite_genres=["NOVEL", "ESSAY"],
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["preferences"]["tradeLocation1"], "Test Location")
        self.assertEqual(response.data["preferences"]["tradeSpot1"], "Test Spot")
        self.assertEqual(response.data["favoriteGenres"], ["NOVEL", "ESSAY"])

    def test_patch_profile_me_updates_user_and_taste(self):
        """Test PATCH /accounts/profile/me/ updates user profile and taste."""
        data = {
            "bio": "Updated bio",
            "preferences": {
                "tradeLocation1": "New Location",
                "tradeSpot1": "New Spot",
            },
            "favoriteGenres": ["SCIENCE_TECH", "HISTORY_PHILOSOPHY"],
        }
        
        response = self.client.patch(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user bio updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Updated bio")
        
        # Verify taste data updated
        taste = UserTaste.objects.get(user=self.user)
        self.assertEqual(taste.trade_place_name, "New Location")
        self.assertEqual(taste.trade_address, "New Spot")
        self.assertEqual(taste.favorite_genres, ["SCIENCE_TECH", "HISTORY_PHILOSOPHY"])

    def test_patch_profile_me_creates_taste_if_not_exists(self):
        """Test PATCH creates UserTaste if it doesn't exist."""
        data = {
            "preferences": {
                "tradeLocation1": "First Location",
            },
        }
        
        response = self.client.patch(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify taste was created
        self.assertTrue(UserTaste.objects.filter(user=self.user).exists())
        taste = UserTaste.objects.get(user=self.user)
        self.assertEqual(taste.trade_place_name, "First Location")

    def test_get_profile_me_includes_counts(self):
        """Test GET includes reviewCount, followerCount, followingCount."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("reviewCount", response.data)
        self.assertIn("followerCount", response.data)
        self.assertIn("followingCount", response.data)
        self.assertEqual(response.data["reviewCount"], 0)  # No reviews yet

    def test_profile_me_requires_authentication(self):
        """Test that unauthenticated requests are rejected."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
