#!/usr/bin/env python
"""
Authentication debugging utilities.
Used to isolate and debug authentication issues.
"""

import os
import sys
import django
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.test import Client

User = get_user_model()

def test_simple_auth():
    """Test simple authentication."""
    print("Simple Authentication Test")
    print("=" * 30)
    
    # Clean up and create a fresh user
    try:
        User.objects.filter(username='simpletest').delete()
    except:
        pass
    
    # Create user using Django's create_user method
    user = User.objects.create_user(
        username='simpletest',
        email='simple@test.com',
        password='simplepass123'
    )
    print(f"Created user: {user.username}")
    print(f"User ID: {user.id}")
    print(f"User is_active: {user.is_active}")
    
    # Test direct authentication with EMAIL (since USERNAME_FIELD = 'email')
    auth_result = authenticate(username='simple@test.com', password='simplepass123')
    print(f"Direct authenticate result (with email): {auth_result}")

    # Also test with username (should fail)
    auth_result_username = authenticate(username='simpletest', password='simplepass123')
    print(f"Direct authenticate result (with username): {auth_result_username}")
    
    if auth_result is None:
        print("Authentication failed - checking possible issues...")
        
        # Check if the issue is with the custom User model
        print(f"User model: {User}")
        print(f"User._meta.app_label: {User._meta.app_label}")
        print(f"User._meta.model_name: {User._meta.model_name}")
        
        # Check authentication backends
        from django.conf import settings
        print(f"Authentication backends: {settings.AUTHENTICATION_BACKENDS}")
        
        # Test each backend individually
        from django.contrib.auth.backends import ModelBackend
        backend = ModelBackend()
        
        # Check if user exists in backend
        try:
            backend_user = backend.get_user(user.id)
            print(f"Backend can get user: {backend_user}")
        except:
            print("Backend cannot get user")
        
        # Test backend authenticate method
        backend_auth = backend.authenticate(None, username='simpletest', password='simplepass123')
        print(f"Backend authenticate: {backend_auth}")
        
        # Check if the issue is with the username field
        username_field = User.USERNAME_FIELD
        print(f"USERNAME_FIELD: {username_field}")
        
        # Try to get user by username
        try:
            db_user = User.objects.get(username='simpletest')
            print(f"User found in DB: {db_user}")
            print(f"Password check: {db_user.check_password('simplepass123')}")
        except User.DoesNotExist:
            print("User not found in DB!")
    
    else:
        print("Authentication successful!")
        
        # Test JWT token creation
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(auth_result)
        print(f"JWT token created: {str(refresh.access_token)[:50]}...")
        
        # Test our custom serializer with EMAIL
        from accounts.serializers import CustomTokenObtainPairSerializer

        print("\nTesting custom serializer with email:")
        serializer_email = CustomTokenObtainPairSerializer(data={
            'username': 'simple@test.com',  # Use email
            'password': 'simplepass123'
        })

        if serializer_email.is_valid():
            tokens = serializer_email.validated_data
            print("Custom serializer works with email!")
            print(f"Access token: {tokens['access'][:50]}...")
        else:
            print(f"Custom serializer errors with email: {serializer_email.errors}")

        print("\nTesting custom serializer with username:")
        serializer_username = CustomTokenObtainPairSerializer(data={
            'username': 'simpletest',  # Use username
            'password': 'simplepass123'
        })

        if serializer_username.is_valid():
            tokens = serializer_username.validated_data
            print("Custom serializer works with username!")
            print(f"Access token: {tokens['access'][:50]}...")
        else:
            print(f"Custom serializer errors with username: {serializer_username.errors}")

def debug_user_model():
    """Debug user model configuration."""
    print("\nUser Model Debug Information")
    print("=" * 30)
    
    print(f"User model: {User}")
    print(f"USERNAME_FIELD: {User.USERNAME_FIELD}")
    print(f"REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")
    print(f"User._meta.db_table: {User._meta.db_table}")
    
    # Check authentication backends
    from django.conf import settings
    print(f"AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")
    
    # Check user count
    user_count = User.objects.count()
    print(f"Total users in database: {user_count}")
    
    if user_count > 0:
        print("\nExisting users:")
        for user in User.objects.all()[:5]:  # Show first 5 users
            print(f"  - {user.username} ({user.email}) - Active: {user.is_active}")

if __name__ == '__main__':
    debug_user_model()
    test_simple_auth()
