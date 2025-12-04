import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from books.models import BookCopy, BookPublication
from accounts.models import UserTaste

User = get_user_model()

@pytest.mark.django_db
def test_explore_recommendations_basic():
    user = User.objects.create_user(username="aiuser", email="aiuser@test.com", password="pw1234")
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("explore-recommendations")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        first = data[0]
        assert "id" in first
        assert "title" in first
        assert "authors" in first


@pytest.mark.django_db
def test_explore_recommendations_recommendations_path():
    user = User.objects.create_user(username="aiuser2", email="aiuser2@test.com", password="pw1234")
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("explore-recommendations-list")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
@pytest.mark.django_db
def test_ai_barter_context_basic():
    user_a = User.objects.create_user(username="usera", email="usera@test.com", password="pw1234")
    user_b = User.objects.create_user(username="userb", email="userb@test.com", password="pw1234")
    pub = BookPublication.objects.create(title="TestBook")
    book_b = BookCopy.objects.create(publication=pub, owner=user_b, is_for_barter=True, trade_status="available")
    client = APIClient()
    client.force_authenticate(user=user_a)
    url = reverse("barter-context")
    payload = {"recipient_id": str(user_b.id), "requested_book_id": str(book_b.id)}
    response = client.post(url, payload, format="json")
    assert response.status_code == 200
    data = response.json()
    assert "context" in data
    assert "requester_id" in data
    assert "recipient_id" in data
    assert "requested_book_id" in data
    assert data["recipient_id"] == str(user_b.id)
    assert data["requested_book_id"] == str(book_b.id)
    assert "requester" in data["context"]
    assert "recipient" in data["context"]
    assert "available_books" in data["context"]["requester"]
    assert "wishlist" in data["context"]["recipient"]
    assert "owned_book_ids" in data["context"]["recipient"]
