import json

import pytest
from books.management.commands import bootstrap_korean_books as bootstrap_cmd
from books.management.commands import categorize_publications as categorize_cmd
from books.management.commands import import_books_from_kakao as import_cmd
from books.management.commands import sync_book_metadata as sync_cmd
from books.models import BookPublication, Genre
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command

User = get_user_model()


class _DummySummary:
    def __init__(
        self, processed=1, created=0, updated=0, skipped=0, failures=0
    ):
        self.processed = processed
        self.created = created
        self.updated = updated
        self.skipped = skipped
        self.failures = failures


@pytest.mark.django_db
def test_bootstrap_uses_default_keywords(monkeypatch):
    # Shrink the default keyword list for a faster test while still exercising defaults.
    monkeypatch.setattr(bootstrap_cmd, "DEFAULT_KEYWORDS", ["Alpha", "Beta"])

    calls: list[tuple[str, int, bool]] = []

    class DummyService:
        def __init__(self, create_copies=True):
            self.create_copies = create_copies

        def import_from_query(self, query, owner, size, overwrite):
            calls.append((query, size, overwrite))
            return _DummySummary(processed=1)

    monkeypatch.setattr(
        bootstrap_cmd,
        "BookImportService",
        lambda *a, **k: DummyService(*a, **k),
    )

    call_command("bootstrap_korean_books", "--skip-copies", "--size", "2")

    assert calls == [("Alpha", 2, False), ("Beta", 2, False)]


def test_bootstrap_rejects_non_positive_size():
    with pytest.raises(CommandError):
        call_command("bootstrap_korean_books", "--skip-copies", "--size", "0")


@pytest.mark.django_db
def test_import_books_resolves_owner_and_calls_service(monkeypatch):
    user = User.objects.create_user(email="owner@example.com", password="pass")
    calls: list[tuple[str, User, int, bool]] = []

    class DummyService:
        def import_from_query(self, query, owner, size, overwrite):
            calls.append((query, owner, size, overwrite))
            return _DummySummary()

    monkeypatch.setattr(
        import_cmd, "BookImportService", lambda: DummyService()
    )

    call_command(
        "import_books_from_kakao",
        "harry potter",
        "--owner-id",
        str(user.id),
        "--size",
        "3",
        "--overwrite",
    )

    assert calls == [("harry potter", user, 3, True)]


def test_import_books_rejects_non_positive_size():
    with pytest.raises(CommandError):
        call_command(
            "import_books_from_kakao",
            "query",
            "--owner-email",
            "x@y.com",
            "--size",
            "0",
        )


@pytest.mark.django_db
def test_categorize_publications_persists_classification(monkeypatch):
    publication = BookPublication.objects.create(
        title="Test Book", description=""
    )

    classification = categorize_cmd.PublicationClassification(
        category_scores=[{"label": "Mystery", "score": 0.9}],
        taste_profile={"genres": ["Mystery"]},
    )

    def classify_many(payloads):
        assert payloads[0].identifier == str(publication.pk)
        return {payloads[0].identifier: classification}

    class DummyCategorizer:
        def __init__(self, enable_llm=True):
            self.enable_llm = enable_llm

        def classify_many(self, payloads):
            return classify_many(payloads)

    monkeypatch.setattr(
        categorize_cmd, "PublicationCategorizer", DummyCategorizer
    )

    call_command(
        "categorize_publications",
        "--ids",
        str(publication.pk),
        "--overwrite",
        "--batch-size",
        "1",
    )

    publication.refresh_from_db()
    assert publication.category_scores == classification.category_scores
    assert publication.taste_profile == json.loads(
        json.dumps(classification.taste_profile)
    )
    assert Genre.objects.filter(name="Mystery").exists()
    assert publication.genres.filter(name="Mystery").exists()


def test_categorize_publications_rejects_invalid_batch_size():
    with pytest.raises(CommandError):
        call_command("categorize_publications", "--batch-size", "0")


@pytest.mark.django_db
def test_sync_book_metadata_calls_synchronizer(monkeypatch):
    pub1 = BookPublication.objects.create(title="Needs Sync")
    pub2 = BookPublication.objects.create(title="Also Sync")

    calls: list[tuple[bool, int, set[str]]] = []

    class DummySyncResult:
        def __init__(self, processed, updated, failures):
            self.processed = processed
            self.updated = updated
            self.failures = failures

    class DummySynchronizer:
        def sync_queryset(self, queryset, *, overwrite, limit):
            titles = {p.title for p in queryset}
            calls.append((overwrite, limit, titles))
            # Limit is passed through; mimic processing that many records.
            processed = (
                min(limit, len(titles)) if limit is not None else len(titles)
            )
            return DummySyncResult(processed=processed, updated=1, failures=0)

    monkeypatch.setattr(
        sync_cmd,
        "BookMetadataSynchronizer",
        lambda *a, **k: DummySynchronizer(),
    )

    call_command("sync_book_metadata", "--all", "--limit", "1")

    assert calls
    overwrite, limit, titles = calls[0]
    assert overwrite is False
    assert limit == 1
    assert {"Needs Sync", "Also Sync"} == titles
