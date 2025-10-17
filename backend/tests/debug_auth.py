#!/usr/bin/env python
"""
Debug authentication issues.
Comprehensive debugging utilities for authentication problems.
"""

import os
import sys
from pathlib import Path

import django

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


def debug_authentication():
    """Debug authentication issues."""
    print("Debugging Authentication")
    print("=" * 30)

    # Check if user exists
    try:
        user = User.objects.get(username="testuser123")
        print(f"User found: {user.username} ({user.email})")
        print(f"User is active: {user.is_active}")
        print(f"User has usable password: {user.has_usable_password()}")

        # Test password
        print(f"Password check: {user.check_password('testpass123')}")

        # Test Django authenticate
        auth_user = authenticate(
            username="testuser123", password="testpass123"
        )
        print(f"Django authenticate result: {auth_user}")

        # Test with email
        auth_user_email = authenticate(
            username=user.username, password="testpass123"
        )
        print(f"Django authenticate with email lookup: {auth_user_email}")

        # Test authentication backends directly
        from django.contrib.auth.backends import ModelBackend

        backend = ModelBackend()
        auth_result = backend.authenticate(
            None, username="testuser123", password="testpass123"
        )
        print(f"ModelBackend authenticate result: {auth_result}")

        # Check user model
        print(f"User model: {User}")
        print(
            f"User._meta.get_field('username'): {User._meta.get_field('username')}"
        )

        # Test creating a new user and immediate authentication
        print("\nTesting fresh user creation and authentication:")
        fresh_user = User.objects.create_user(
            username="freshuser",
            email="fresh@example.com",
            password="freshpass123",
        )
        print(f"Created fresh user: {fresh_user.username}")
        fresh_auth = authenticate(
            username="freshuser", password="freshpass123"
        )
        print(f"Fresh user authentication: {fresh_auth}")

        # Check database directly
        print("\nDatabase check:")
        print(f"User table name: {User._meta.db_table}")

        # Check if there are any issues with the password field
        print(f"Password field: {user.password}")
        print(
            f"Password starts with hash: {user.password.startswith('pbkdf2_')}"
        )

        # Try to authenticate with the superuser
        try:
            superuser = User.objects.get(is_superuser=True)
            print(f"Superuser found: {superuser.username}")
            # Don't test superuser password for security
        except User.DoesNotExist:
            print("No superuser found")

        # Check authentication with a simple test
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post("/login/")
        request.user = user
        print(f"User can be set on request: {request.user == user}")

    except User.DoesNotExist:
        print("User does not exist!")

        # Create a test user
        print("Creating test user...")
        user = User.objects.create_user(
            username="debuguser",
            email="debug@example.com",
            password="debugpass123",
        )
        print(f"Created user: {user.username}")

        # Test authentication
        auth_user = authenticate(username="debuguser", password="debugpass123")
        print(f"Authentication result: {auth_user}")


def debug_user_settings():
    """Debug user model settings."""
    print("\nUser Model Settings Debug")
    print("=" * 30)

    print(f"USERNAME_FIELD: {User.USERNAME_FIELD}")
    print(f"REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")
    print(f"User._meta.app_label: {User._meta.app_label}")
    print(f"User._meta.model_name: {User._meta.model_name}")

    # Check authentication backends
    from django.conf import settings

    print(f"AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")

    # Check database settings
    print(f"DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
    print(f"DATABASE NAME: {settings.DATABASES['default']['NAME']}")


if __name__ == "__main__":
    debug_user_settings()
    debug_authentication()
