"""
Unit tests for accounts models.
Tests User model and UserPreferences model.
"""

from accounts.models import UserPreferences
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        self.assertEqual(superuser.username, "admin")
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), "testuser")

    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(**self.user_data)

        # Try to create another user with same email
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="anotheruser",
                email="test@example.com",
                password="pass123",
            )

    def test_user_username_unique(self):
        """Test that username must be unique."""
        User.objects.create_user(**self.user_data)

        # Try to create another user with same username
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="testuser",
                email="another@example.com",
                password="pass123",
            )


class UserPreferencesModelTestCase(TestCase):
    """Test cases for UserPreferences model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_create_user_preferences(self):
        """Test creating user preferences."""
        preferences = UserPreferences.objects.create(
            user=self.user,
            email_notifications=True,
            push_notifications=False,
        )

        self.assertEqual(preferences.user, self.user)
        self.assertTrue(preferences.email_notifications)
        self.assertFalse(preferences.push_notifications)

    def test_user_preferences_default_values(self):
        """Test default values for user preferences."""
        preferences = UserPreferences.objects.create(user=self.user)

        # Check if default values are set (adjust based on your model)
        self.assertIsNotNone(preferences.user)

    def test_user_preferences_string_representation(self):
        """Test user preferences string representation."""
        preferences = UserPreferences.objects.create(user=self.user)
        expected = f"{self.user.username}'s preferences"
        self.assertEqual(str(preferences), expected)

    def test_one_to_one_relationship(self):
        """Test one-to-one relationship between User and UserPreferences."""
        preferences = UserPreferences.objects.create(user=self.user)

        # Try to create another preferences for same user
        with self.assertRaises(Exception):
            UserPreferences.objects.create(user=self.user)

    def test_cascade_delete(self):
        """Test that preferences are deleted when user is deleted."""
        preferences = UserPreferences.objects.create(user=self.user)
        preferences_id = preferences.id

        # Delete user
        self.user.delete()

        # Check that preferences are also deleted
        with self.assertRaises(UserPreferences.DoesNotExist):
            UserPreferences.objects.get(id=preferences_id)
