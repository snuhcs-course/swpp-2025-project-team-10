"""
Unit tests for profile management views.
Tests profile retrieval, update, and preferences.
"""

from accounts.models import UserPreferences
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class ProfileViewTestCase(TestCase):
    """Test cases for profile view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.profile_url = "/auth/profile/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_get_profile_unauthenticated(self):
        """Test getting profile when not authenticated."""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_contains_expected_fields(self):
        """Test that profile contains expected fields."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        expected_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)


class ProfileUpdateViewTestCase(TestCase):
    """Test cases for profile update view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.update_url = "/auth/profile/update/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_update_profile_authenticated(self):
        """Test updating profile when authenticated."""
        self.client.force_authenticate(user=self.user)

        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.put(self.update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_update_profile_partial(self):
        """Test partial profile update."""
        self.client.force_authenticate(user=self.user)

        data = {"first_name": "Updated"}
        response = self.client.patch(self.update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only first_name was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "User")  # Unchanged

    def test_update_profile_unauthenticated(self):
        """Test updating profile when not authenticated."""
        data = {"first_name": "Updated"}
        response = self.client.put(self.update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_empty_data(self):
        """Test updating profile with empty data."""
        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.put(self.update_url, data, format="json")

        # Should still succeed (no changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserPreferencesViewTestCase(TestCase):
    """Test cases for user preferences view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.preferences_url = "/auth/preferences/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.preferences = UserPreferences.objects.create(
            user=self.user, email_notifications=True, push_notifications=False
        )

    def test_get_preferences_authenticated(self):
        """Test getting preferences when authenticated."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.preferences_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email_notifications", response.data)
        self.assertIn("push_notifications", response.data)

    def test_get_preferences_unauthenticated(self):
        """Test getting preferences when not authenticated."""
        response = self.client.get(self.preferences_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_preferences_authenticated(self):
        """Test updating preferences when authenticated."""
        self.client.force_authenticate(user=self.user)

        data = {"email_notifications": False, "push_notifications": True}
        response = self.client.put(self.preferences_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify preferences were updated
        self.preferences.refresh_from_db()
        self.assertFalse(self.preferences.email_notifications)
        self.assertTrue(self.preferences.push_notifications)

    def test_update_preferences_partial(self):
        """Test partial preferences update."""
        self.client.force_authenticate(user=self.user)

        data = {"email_notifications": False}
        response = self.client.patch(self.preferences_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only email_notifications was updated
        self.preferences.refresh_from_db()
        self.assertFalse(self.preferences.email_notifications)
        self.assertFalse(self.preferences.push_notifications)  # Unchanged

    def test_update_preferences_unauthenticated(self):
        """Test updating preferences when not authenticated."""
        data = {"email_notifications": False}
        response = self.client.put(self.preferences_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_preferences_if_not_exists(self):
        """Test that preferences are created if they don't exist."""
        # Create user without preferences
        new_user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=new_user)

        data = {"email_notifications": True, "push_notifications": True}
        response = self.client.put(self.preferences_url, data, format="json")

        # Should create preferences
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify preferences were created
        preferences = UserPreferences.objects.get(user=new_user)
        self.assertTrue(preferences.email_notifications)
        self.assertTrue(preferences.push_notifications)


# Additional pytest-based tests for coverage

import pytest


@pytest.mark.django_db
def test_user_profile_me_view():
    """Test /auth/me/ endpoint."""
    from django.urls import reverse
    from rest_framework.test import APIClient

    client = APIClient()
    user = User.objects.create(
        username="user4",
        email="u4@test.com",
        first_name="Test",
        last_name="User",
        location="Seoul",
    )
    client.force_authenticate(user)

    res = client.get(reverse("accounts:user_profile"))

    assert res.status_code == 200
    assert res.data["username"] == "user4"


@pytest.mark.django_db
def test_user_profile_view_other_user():
    """Test viewing another user's profile."""
    from django.urls import reverse
    from rest_framework.test import APIClient

    client = APIClient()
    user1 = User.objects.create(
        username="user5", email="u5@test.com", first_name="U", last_name="1"
    )
    user2 = User.objects.create(
        username="user6", email="u6@test.com", first_name="U", last_name="2"
    )
    client.force_authenticate(user1)

    # Note: Current implementation doesn't support viewing other user's profile by ID
    # This test may need to be updated based on actual API design
    res = client.get(reverse("accounts:user_profile"))

    assert res.status_code == 200


@pytest.mark.django_db
def test_update_profile_with_location():
    """Test updating profile with location."""
    from django.urls import reverse
    from rest_framework.test import APIClient

    client = APIClient()
    user = User.objects.create(
        username="user7", email="u7@test.com", first_name="U", last_name="ser"
    )
    client.force_authenticate(user)

    res = client.patch(
        reverse("accounts:update_profile"),
        {
            "location": "Busan",
            "bio": "Test bio",
        },
        format="json",
    )

    assert res.status_code == 200
    user.refresh_from_db()
    assert user.location == "Busan"


@pytest.mark.django_db
def test_user_preferences_get_and_update():
    """Test user preferences GET and PATCH."""
    from django.urls import reverse
    from rest_framework.test import APIClient

    client = APIClient()
    user = User.objects.create(
        username="user8", email="u8@test.com", first_name="U", last_name="ser"
    )
    client.force_authenticate(user)

    # GET - should create preferences if not exists
    res = client.get(reverse("accounts:user_preferences"))
    assert res.status_code == 200

    # PATCH - update preferences
    res = client.patch(
        reverse("accounts:user_preferences"),
        {
            "notification_enabled": False,
            "email_notifications": False,
        },
        format="json",
    )
    assert res.status_code == 200
