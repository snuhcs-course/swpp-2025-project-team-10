"""
Additional tests for books views to improve coverage.
"""

import pytest
from books.models import BookCopy, BookPublication, Publisher
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_toggle_barter_book_not_found():
    """Test toggle barter with non-existent book."""
    client = APIClient()
    user = User.objects.create(
        username="owner",
        email="owner@test.com",
        first_name="O",
        last_name="wner",
    )
    client.force_authenticate(user)

    # Invalid UUID
    res = client.patch(
        "/library/books/00000000-0000-0000-0000-000000000001/toggle-barter/"
    )

    assert res.status_code == 404
    assert "not found" in res.data["error"].lower()


@pytest.mark.django_db
def test_toggle_barter_not_owner():
    """Test toggle barter when not the owner."""
    client = APIClient()
    owner = User.objects.create(
        username="owner",
        email="owner@test.com",
        first_name="O",
        last_name="wner",
    )
    other = User.objects.create(
        username="other",
        email="other@test.com",
        first_name="O",
        last_name="ther",
    )

    publisher = Publisher.objects.create(name="Pub")
    publication = BookPublication.objects.create(
        title="Book", publisher=publisher
    )
    book = BookCopy.objects.create(
        publication=publication, owner=owner, is_for_barter=False
    )
    client.force_authenticate(other)
    res = client.patch(f"/library/books/{book.id}/toggle-barter/")

    assert res.status_code == 403
    assert "owner" in res.data["error"].lower()


@pytest.mark.django_db
def test_toggle_barter_success():
    """Test successful toggle of barter availability."""
    client = APIClient()
    owner = User.objects.create(
        username="owner",
        email="owner@test.com",
        first_name="O",
        last_name="wner",
    )

    publisher = Publisher.objects.create(name="Pub")
    publication = BookPublication.objects.create(
        title="Book", publisher=publisher
    )
    book = BookCopy.objects.create(
        publication=publication, owner=owner, is_for_barter=False
    )

    client.force_authenticate(owner)
    res = client.patch(f"/library/books/{book.id}/toggle-barter/")

    assert res.status_code == 200
    assert res.data["is_for_barter"] is True

    book.refresh_from_db()
    assert book.is_for_barter is True
