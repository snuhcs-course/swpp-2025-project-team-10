import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import BookCopy, BookPublication

User = get_user_model()


@pytest.mark.django_db
def test_book_detail_get_put_delete_flow():
    user = User.objects.create_user(
        username="booker", email="booker@test.com", password="pw1234"
    )
    pub = BookPublication.objects.create(title="Editable Book")
    book = BookCopy.objects.create(publication=pub, owner=user)

    client = APIClient()
    client.force_authenticate(user=user)

    detail_url = reverse("books:book-detail", args=[book.id])

    resp = client.get(detail_url)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Editable Book"

    resp = client.put(detail_url, {"owner_notes": "Updated note"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["owner_notes"] == "Updated note"


@pytest.mark.django_db
def test_book_list_create_adds_book_for_authenticated_user():
    user = User.objects.create_user(
        username="adder", email="adder@test.com", password="pw1234"
    )
    pub = BookPublication.objects.create(title="New Book")

    client = APIClient()
    client.force_authenticate(user=user)

    list_url = reverse("books:books-list")
    resp = client.post(list_url, {"publication": str(pub.id)}, format="json")
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["title"] == "New Book"
    assert payload["owner"] == user.username
    assert BookCopy.objects.filter(owner=user, publication=pub).exists()
