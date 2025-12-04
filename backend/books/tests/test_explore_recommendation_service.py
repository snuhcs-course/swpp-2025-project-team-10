import pytest
from django.contrib.auth import get_user_model

from accounts.models import UserTaste
from ai_integration.services import AIRecommendationService
from books.models import Author, BookCopy, BookPublication, Genre

User = get_user_model()


@pytest.mark.django_db
def test_explore_recommendations_prioritise_taste_and_authors():
    user = User.objects.create_user(
        username="reader", email="reader@test.com", password="pw1234"
    )
    UserTaste.objects.create(
        user=user,
        favorite_genres=["Mystery"],
        favorite_authors=["Agatha Christie"],
    )
    other_owner = User.objects.create_user(
        username="owner", email="owner@test.com", password="pw1234"
    )

    mystery = Genre.objects.create(name="Mystery")
    romance = Genre.objects.create(name="Romance")
    agatha = Author.objects.create(name="Agatha Christie")
    author_two = Author.objects.create(name="Another Author")

    pub1 = BookPublication.objects.create(
        title="Mysterious Case", category_scores=[{"label": "Mystery", "score": 0.9}]
    )
    pub1.authors.add(agatha)
    pub1.genres.add(mystery)

    pub2 = BookPublication.objects.create(
        title="Romantic Tale", category_scores=[{"label": "Romance", "score": 0.8}]
    )
    pub2.authors.add(author_two)
    pub2.genres.add(romance)

    BookCopy.objects.create(publication=pub1, owner=other_owner)
    BookCopy.objects.create(publication=pub2, owner=other_owner)

    results = AIRecommendationService.recommend_books_for_exploration(
        user=user, limit=5
    )
    assert len(results) == 2
    assert results[0]["title"] == "Mysterious Case"
    assert results[0]["score"] >= results[1]["score"]
    assert results[0]["authors"] == ["Agatha Christie"]


@pytest.mark.django_db
def test_explore_recommendations_handles_errors(monkeypatch):
    user = User.objects.create_user(
        username="reader2", email="reader2@test.com", password="pw1234"
    )

    monkeypatch.setattr(
        AIRecommendationService,
        "get_exploration_context_data",
        lambda _user: {"user": {"taste": {}, "id": str(_user.id)}},
    )

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(BookCopy.objects, "filter", boom)

    results = AIRecommendationService.recommend_books_for_exploration(
        user=user, limit=3
    )
    assert results == []
