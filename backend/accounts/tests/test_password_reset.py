"""
Tests for password reset functionality.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.cache import cache


User = get_user_model()


@pytest.mark.django_db
def test_password_reset_invalid_code():
    """Test password reset verify with invalid code."""
    client = APIClient()
    
    # Set up valid request in cache
    request_id = "test-request-id"
    cache_key = f"password_reset_{request_id}"
    cache.set(cache_key, {"email": "test@test.com", "code": "123456", "verified": False}, timeout=900)
    
    # Try with wrong code
    res = client.post(
        reverse("accounts:forgot_password_verify"),
        {"request_id": request_id, "code": "wrong"},
        format="json",
    )
    assert res.status_code == 400
    assert "invalid" in res.data["message"].lower()


@pytest.mark.django_db
def test_password_reset_verify_invalid_serializer():
    """Test password reset verify with invalid data."""
    client = APIClient()
    
    # Missing fields
    res = client.post(
        reverse("accounts:forgot_password_verify"),
        {},
        format="json",
    )
    assert res.status_code == 400
    assert "errors" in res.data


@pytest.mark.django_db
def test_password_reset_request_invalid_email():
    """Test password reset request with invalid email."""
    client = APIClient()
    
    res = client.post(
        reverse("accounts:forgot_password_start"),
        {"email": "nonexistent@test.com"},
        format="json",
    )
    
    # Should still return 200 for security
    assert res.status_code == 200


@pytest.mark.django_db
def test_password_reset_request_valid_email():
    """Test password reset request with valid email."""
    client = APIClient()
    user = User.objects.create(username="user3", email="valid@test.com", first_name="U", last_name="ser")
    user.set_password("oldpass123")
    user.save()
    
    res = client.post(
        reverse("accounts:forgot_password_start"),
        {"email": "valid@test.com"},
        format="json",
    )
    
    assert res.status_code == 200


@pytest.mark.django_db
def test_password_reset_confirm_serializer_validation():
    """Test password reset confirm serializer validates new password."""
    from accounts.serializers import PasswordResetConfirmSerializer
    
    # Valid password
    serializer = PasswordResetConfirmSerializer(data={
        "password": "newpass456",
    })
    assert serializer.is_valid()
    
    # Too short (less than 6 chars)
    serializer = PasswordResetConfirmSerializer(data={
        "password": "short",
    })
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_password_reset_confirm_view_valid():
    """Test password reset confirm view with valid data."""
    client = APIClient()

    res = client.post(
        reverse("accounts:forgot_password_reset"),
        {"password": "newpass123"},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["ok"] is True


@pytest.mark.django_db
def test_password_reset_confirm_view_invalid():
    """Test password reset confirm view with invalid data."""
    client = APIClient()

    # Too short password
    res = client.post(
        reverse("accounts:forgot_password_reset"),
        {"password": "short"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["ok"] is False


@pytest.mark.django_db
def test_password_reset_start_missing_email():
    """Test password reset start without email."""
    client = APIClient()
    
    res = client.post(
        reverse("accounts:forgot_password_start"),
        {},
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_password_reset_verify_invalid_code():
    """Test password reset verify with invalid code."""
    client = APIClient()
    
    res = client.post(
        reverse("accounts:forgot_password_verify"),
        {"email": "test@test.com", "code": "000000"},
        format="json",
    )
    assert res.status_code in [400, 404]
