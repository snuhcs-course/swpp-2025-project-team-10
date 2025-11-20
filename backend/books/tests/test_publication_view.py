import pytest
from books.services.publication_categories import PublicationClassification
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_publication_recommendations_returns_samples(monkeypatch):
    class _Categorizer:
        def classify(self, payload):  # pragma: no cover - simple stub
            return PublicationClassification(
                category_scores=[{"label": "Sample", "score": 0.73}],
                taste_profile={
                    "genres": ["NOVEL"],
                    "moods": ["WARM"],
                    "purposes": ["HEALING"],
                    "length": "MEDIUM",
                },
            )

    monkeypatch.setattr(
        "books.views.PublicationCategorizer", lambda: _Categorizer()
    )

    client = APIClient()
    url = reverse("books:publication-recommendations")
    response = client.get(url + "?limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["results"]) == 2
    first = payload["results"][0]
    assert first["categoryScores"][0]["label"] == "Sample"
    assert first["tasteProfile"]["genres"] == ["NOVEL"]
