import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Author as BookAuthor, Book, Publisher


User = get_user_model()


@pytest.mark.django_db
def test_toggle_wishlist_creates_and_removes():
    client = APIClient()
    user = User.objects.create(username="u1", email="u1@example.com", first_name="A", last_name="B")
    client.force_authenticate(user)

    publisher = Publisher.objects.create(name="Test Pub")
    author = BookAuthor.objects.create(name="Author A")
    book = Book.objects.create(title="AAA", owner=user, publisher=publisher)
    book.authors.add(author)

    url = reverse("books:toggle-wishlist", kwargs={"book_id": book.id})

    # Add to wishlist
    res = client.post(url)
    assert res.status_code == 200
    assert res.data["wishlisted"] is True

    # Remove from wishlist
    res = client.post(url)
    assert res.status_code == 200
    assert res.data["wishlisted"] is False


@pytest.mark.django_db
def test_toggle_book_for_barter_owner_only():
    client = APIClient()
    owner = User.objects.create(username="owner", email="o@example.com", first_name="O", last_name="W")
    other = User.objects.create(username="other", email="x@example.com", first_name="X", last_name="Y")

    publisher = Publisher.objects.create(name="Test Pub")
    author = BookAuthor.objects.create(name="Author A")
    book = Book.objects.create(title="AAA", owner=owner, publisher=publisher, is_for_barter=True)
    book.authors.add(author)

    url = reverse("books:toggle-barter", kwargs={"book_id": book.id})

    # Not owner forbidden
    client.force_authenticate(other)
    res = client.patch(url)
    assert res.status_code == 403

    # Owner can toggle
    client.force_authenticate(owner)
    res = client.patch(url)
    assert res.status_code == 200
    assert res.data["is_for_barter"] == (not True)


@pytest.mark.django_db
def test_nearby_owners_includes_distance_and_profile_blocks():
    client = APIClient()
    me = User.objects.create(username="me", email="me@example.com", first_name="M", last_name="E", latitude=37.5665, longitude=126.9780)
    owner = User.objects.create(username="own", email="own@example.com", first_name="O", last_name="W", latitude=37.5660, longitude=126.9770)

    publisher = Publisher.objects.create(name="Test Pub")
    author = BookAuthor.objects.create(name="Author A")

    # Two books of same title; only owner's is_for_barter True should show
    my_book = Book.objects.create(title="SameTitle", owner=me, publisher=publisher, is_for_barter=False)
    my_book.authors.add(author)
    their_book = Book.objects.create(title="SameTitle", owner=owner, publisher=publisher, is_for_barter=True)
    their_book.authors.add(author)

    url = reverse("books:nearby-owners", kwargs={"book_id": my_book.id})

    client.force_authenticate(me)
    res = client.get(url)
    assert res.status_code == 200
    owners = res.data["owners"]
    assert len(owners) == 1
    info = owners[0]
    # Basic checks
    assert info["username"] == "own"
    assert info["distance_km"] is not None
    assert "library" in info and isinstance(info["library"], list)
    assert "wishlist" in info and isinstance(info["wishlist"], list)
    assert "taste" in info  # may be None if not set
