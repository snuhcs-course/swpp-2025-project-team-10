import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from accounts.models import UserTaste, BookGenre, BookMood, BookLength, ReadingPurpose
from accounts.serializers import UserBarterInfoSerializer
from books.models import Author as BookAuthor, Book, Publisher, BookWishlist


User = get_user_model()


@pytest.mark.django_db
def test_user_barter_info_includes_full_taste_and_counts():
    # Create users
    me = User.objects.create(
        username="me",
        email="me@example.com",
        first_name="Me",
        last_name="User",
    )
    other = User.objects.create(
        username="other",
        email="other@example.com",
        first_name="Other",
        last_name="User",
        bio="Hello",
        location="Seoul",
    )

    # Taste (full)
    taste = UserTaste.objects.create(
        user=other,
        favorite_genres=[BookGenre.NOVEL, BookGenre.ESSAY, BookGenre.SELF_HELP],
        favorite_authors=[],
        favorite_books=[],
        preferred_length=BookLength.MEDIUM,
        preferred_moods=[BookMood.WARM, BookMood.CALM, BookMood.IMMERSIVE],
        reading_purposes=[ReadingPurpose.HEALING, ReadingPurpose.CULTURE, ReadingPurpose.ESCAPISM],
        trade_place_name="Cafe",
        trade_address="Gangnam-gu",
        current_step=7,
    )

    # Library and wishlist
    publisher = Publisher.objects.create(name="Test Pub")
    author = BookAuthor.objects.create(name="Author A")
    b1 = Book.objects.create(title="Book A", owner=other, publisher=publisher)
    b1.authors.add(author)
    b2 = Book.objects.create(title="Book B", owner=other, publisher=publisher)
    b2.authors.add(author)
    BookWishlist.objects.create(user=other, book=b1)

    # Serialize with request context
    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = me

    data = UserBarterInfoSerializer(other, context={"request": request}).data

    # Core identity
    assert data["id"] == other.id
    assert data["username"] == "other"
    assert data["bio"] == "Hello"
    assert data["location"] == "Seoul"

    # Taste - full survey values included, but precise coords removed
    assert data["taste"]["favorite_genres"]
    assert data["taste"]["preferred_moods"]
    assert data["taste"]["reading_purposes"]
    assert data["taste"]["preferred_length"] == BookLength.MEDIUM
    assert data["taste"]["trade_place_name"] == "Cafe"
    assert data["taste"]["trade_address"] == "Gangnam-gu"

    # Collections
    assert isinstance(data["library"], list) and len(data["library"]) >= 2
    assert isinstance(data["wishlist"], list) and len(data["wishlist"]) >= 1

    # Reviews info present even if none exist
    assert data["reviewCount"] == 0
    assert isinstance(data["reviews"], list)
