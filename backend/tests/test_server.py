#!/usr/bin/env python
"""
Test server utilities for debugging the Django backend.
This script starts the server and provides testing utilities.
"""

import json
import os
import sys
import threading
import time
from pathlib import Path

import django
import requests

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.management import execute_from_command_line
from django.test import Client


def start_server():
    """Start Django development server in a separate thread."""
    print("Starting Django development server...")
    try:
        execute_from_command_line(
            ["manage.py", "runserver", "127.0.0.1:8000", "--noreload"]
        )
    except KeyboardInterrupt:
        print("Server stopped.")


def test_endpoints():
    """Test API endpoints with requests."""
    base_url = "http://127.0.0.1:8000"

    print("\nTesting API Endpoints")
    print("=" * 40)

    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/admin/", timeout=2)
            if response.status_code in [200, 302]:
                print("Server is running!")
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
            print(f"   Waiting... ({i + 1}/10)")
    else:
        print("Server failed to start")
        return

    # Test signup
    print("\n1. Testing Signup")
    signup_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpass123",
    }

    try:
        response = requests.post(
            f"{base_url}/auth/signup/",
            json=signup_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test login
    print("\n2. Testing Login")
    login_data = {"username": "testuser123", "password": "testpass123"}

    try:
        response = requests.post(
            f"{base_url}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Success: {result.get('ok', False)}")
        if result.get("token"):
            print(f"   Token: {result['token'][:50]}...")
    except Exception as e:
        print(f"   Error: {e}")

    # Test password reset
    print("\n3. Testing Password Reset")
    reset_data = {"email": "test@example.com"}

    try:
        response = requests.post(
            f"{base_url}/auth/forgot/start/",
            json=reset_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Request ID: {result.get('requestId', 'N/A')}")
        if result.get("code"):
            print(f"   Reset Code: {result['code']}")
    except Exception as e:
        print(f"   Error: {e}")


def test_with_django_client():
    """Test using Django's test client (doesn't require server)."""
    print("\nTesting with Django Test Client")
    print("=" * 40)

    client = Client()

    # Test signup
    print("\n1. Testing Signup (Django Client)")
    signup_data = {
        "username": "djangotest",
        "email": "django@test.com",
        "password": "djangopass123",
    }

    response = client.post(
        "/auth/signup/",
        data=json.dumps(signup_data),
        content_type="application/json",
    )

    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Error: {response.content.decode()}")

    # Test login
    print("\n2. Testing Login (Django Client)")
    login_data = {"username": "djangotest", "password": "djangopass123"}

    response = client.post(
        "/auth/login/",
        data=json.dumps(login_data),
        content_type="application/json",
    )

    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result.get('ok', False)}")
        if result.get("token"):
            print(f"   Token: {result['token'][:50]}...")
    else:
        print(
            f"   Error: {response.json() if response.status_code != 500 else response.content.decode()}"
        )


def show_urls():
    """Show available URLs."""
    print("\nAvailable URLs")
    print("=" * 40)
    print("Authentication:")
    print("   POST /auth/signup/     - User registration")
    print("   POST /auth/login/      - User login")
    print("   POST /auth/social/     - Social authentication")
    print("   POST /auth/forgot/start/ - Password reset")
    print("   GET  /auth/profile/    - User profile")
    print("\nAdmin & Docs:")
    print("   GET  /admin/           - Django admin")
    print("   GET  /api/docs/        - API documentation")
    print("   GET  /api/schema/      - API schema")


def main():
    """Main function."""
    print("Django Backend Test Server")
    print("=" * 50)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "server":
            start_server()
        elif command == "test":
            test_with_django_client()
        elif command == "test-live":
            # Start server in background and test
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            time.sleep(3)  # Wait for server to start
            test_endpoints()
        elif command == "urls":
            show_urls()
        else:
            print("Unknown command")
            print("Usage:")
            print("   python test_server.py server     - Start server")
            print(
                "   python test_server.py test       - Test with Django client"
            )
            print(
                "   python test_server.py test-live  - Start server and test"
            )
            print("   python test_server.py urls       - Show available URLs")
    else:
        print("Choose an option:")
        print("1. Test with Django client (no server needed)")
        print("2. Start server and test with HTTP requests")
        print("3. Just start the server")
        print("4. Show available URLs")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            test_with_django_client()
        elif choice == "2":
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            time.sleep(3)
            test_endpoints()
            input("\nPress Enter to stop server...")
        elif choice == "3":
            start_server()
        elif choice == "4":
            show_urls()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
