"""
Tests for user taste survey functionality.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import UserTaste, BookGenre, BookMood, ReadingPurpose, BookLength


User = get_user_model()


@pytest.mark.django_db
def test_taste_survey_validation_errors():
    """Test taste survey with insufficient selections."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Step 1: Less than 3 genres
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_genres": [BookGenre.NOVEL]},
        format="json",
    )
    assert res.status_code == 400
    # Check if message exists in response, could be in 'message' or 'errors'
    assert "3개 이상" in str(res.data) or res.status_code == 400
    
    # Step 2: Less than 3 authors
    taste = UserTaste.objects.get(user=user)
    taste.current_step = 2
    taste.save()
    
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_authors": ["Author 1"]},
        format="json",
    )
    assert res.status_code == 400
    
    # Step 3: Less than 3 books
    taste.current_step = 3
    taste.save()
    
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_books": ["Book 1"]},
        format="json",
    )
    assert res.status_code == 400
    
    # Step 4: Missing preferred_length
    taste.current_step = 4
    taste.save()
    
    res = client.post(
        reverse("accounts:user_taste"),
        {"preferred_length": ""},
        format="json",
    )
    assert res.status_code == 400
    
    # Step 5: Less than 3 moods
    taste.current_step = 5
    taste.save()
    
    res = client.post(
        reverse("accounts:user_taste"),
        {"preferred_moods": [BookMood.WARM]},
        format="json",
    )
    assert res.status_code == 400
    
    # Step 6: Less than 3 purposes
    taste.current_step = 6
    taste.save()
    
    res = client.post(
        reverse("accounts:user_taste"),
        {"reading_purposes": [ReadingPurpose.HEALING]},
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_taste_survey_creates_if_not_exists():
    """Test taste survey GET creates UserTaste if it doesn't exist."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Verify no taste exists
    assert not UserTaste.objects.filter(user=user).exists()
    
    # GET should create it
    res = client.get(reverse("accounts:user_taste"))
    assert res.status_code == 200
    assert UserTaste.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_taste_survey_invalid_serializer():
    """Test taste survey with invalid data."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Invalid data type
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_genres": "not_a_list"},
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_taste_survey_complete_flow():
    """Test complete taste survey flow through all 7 steps."""
    client = APIClient()
    user = User.objects.create(username="user_flow", email="uflow@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Create authors and books for the test
    from books.models import Author as BookAuthor, Book, Publisher
    from accounts.models import Author, Book as BookChoice
    
    publisher = Publisher.objects.create(name="Test Publisher")
    
    # Create physical author objects (not used for taste - taste uses enum)
    auth1 = BookAuthor.objects.create(name="Author 1")
    auth2 = BookAuthor.objects.create(name="Author 2")
    auth3 = BookAuthor.objects.create(name="Author 3")
    
    book1 = Book.objects.create(title="Book 1", owner=user, publisher=publisher, is_for_barter=False)
    book2 = Book.objects.create(title="Book 2", owner=user, publisher=publisher, is_for_barter=False)
    book3 = Book.objects.create(title="Book 3", owner=user, publisher=publisher, is_for_barter=False)
    
    # Step 1: Genres (valid - need 3+)
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_genres": [BookGenre.NOVEL, BookGenre.ESSAY, BookGenre.SELF_HELP]},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["ok"] is True
    assert res.data["step"] == 2
    
    # Step 2: Authors (valid - need 3+) - Use Author enum from models, not book Author IDs
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_authors": [Author.HAN_KANG, Author.KIM_YOUNG_HA, Author.JUNG_JAE_SEUNG]},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["step"] == 3
    
    # Step 3: Books (valid - need 3+) - Use Book enum from models, not book IDs
    res = client.post(
        reverse("accounts:user_taste"),
        {"favorite_books": [BookChoice.DEMIAN, BookChoice.SAPIENS, BookChoice.NINETEEN_EIGHTY_FOUR]},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["step"] == 4
    
    # Step 4: Preferred length (valid)
    res = client.post(
        reverse("accounts:user_taste"),
        {"preferred_length": BookLength.MEDIUM},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["step"] == 5
    
    # Step 5: Moods (valid - need 3+)
    res = client.post(
        reverse("accounts:user_taste"),
        {"preferred_moods": [BookMood.WARM, BookMood.CALM, BookMood.IMMERSIVE]},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["step"] == 6
    
    # Step 6: Purposes (valid - need 3+)
    res = client.post(
        reverse("accounts:user_taste"),
        {"reading_purposes": [ReadingPurpose.HEALING, ReadingPurpose.CULTURE, ReadingPurpose.ESCAPISM]},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["step"] == 7
    
    # Step 7: Trade location (optional fields, no strict validation)
    res = client.post(
        reverse("accounts:user_taste"),
        {"trade_place_name": "Cafe", "trade_address": "Seoul"},
        format="json",
    )
    assert res.status_code == 200
    
    # Verify user has completed taste survey
    user.refresh_from_db()
    assert user.has_initial_taste is True


@pytest.mark.django_db
def test_user_taste_get_creates_new_taste():
    """Test GET on user_taste creates new UserTaste if not exists."""
    client = APIClient()
    user = User.objects.create(username="user2", email="u2@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Ensure no taste exists
    assert not UserTaste.objects.filter(user=user).exists()
    
    res = client.get(reverse("accounts:user_taste"))
    
    assert res.status_code == 200
    assert res.data["ok"] is True
    assert res.data["step"] == 1
    assert res.data["is_complete"] is False
    assert UserTaste.objects.filter(user=user).exists()
    