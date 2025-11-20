import pytest
from books.models import Author, BookCopy, BookPublication
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


def _create_copy(owner: User, title: str, author_name: str) -> BookCopy:
    publication = BookPublication.objects.create(
        title=title, description="desc", isbn_13=None
    )
    publication.authors.add(Author.objects.create(name=author_name))
    return BookCopy.objects.create(publication=publication, owner=owner)


@pytest.mark.django_db
def test_book_search_requires_query_param():
    client = APIClient()
    user = User.objects.create_user(
        username="searcher", email="s@example.com", password="pass123"
    )
    client.force_authenticate(user)

    response = client.get(reverse("books:book-search"))

    assert response.status_code == 400
    assert "Missing query" in response.data["error"]


@pytest.mark.django_db
def test_book_search_finds_by_title_or_author():
    client = APIClient()
    user = User.objects.create_user(
        username="reader", email="r@example.com", password="pass123"
    )
    client.force_authenticate(user)
    _create_copy(owner=user, title="Galactic Mystery", author_name="Jane Doe")
    _create_copy(owner=user, title="Another Book", author_name="Chris Puzzle")

    response = client.get(
        reverse("books:book-search"), {"q": "mystery"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Galactic Mystery"
    assert "Jane Doe" in response.data[0]["authors"]


@pytest.mark.django_db
def test_book_search_returns_404_on_no_results():
    client = APIClient()
    user = User.objects.create_user(
        username="missing", email="m@example.com", password="pass123"
    )
    client.force_authenticate(user)

    response = client.get(reverse("books:book-search"), {"q": "unknown"})

    assert response.status_code == 404
    assert "Not found" in response.data["message"]
