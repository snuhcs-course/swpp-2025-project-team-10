"""
Tests for the book metadata synchronisation pipeline.
"""

from __future__ import annotations

import shutil
import tempfile
from unittest.mock import MagicMock, patch

from books.models import BookCopy, BookPublication
from books.services.book_metadata_sync import BookMetadataSynchronizer
from books.services.kakao_book_pipeline import (
    ExternalBook,
    ExternalBookAPIError,
)
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

User = get_user_model()


class BookMetadataSynchronizerTestCase(TestCase):
    """
    Validate the behaviour of the BookMetadataSynchronizer service.
    """

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

        self.addCleanup(self.override.disable)
        self.addCleanup(
            lambda: shutil.rmtree(self.media_root, ignore_errors=True)
        )

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass1234",
        )

        self.publication = BookPublication.objects.create(
            title="The Testing Book",
        )
        self.book_copy = BookCopy.objects.create(
            publication=self.publication,
            owner=self.owner,
        )

    def _build_synchronizer(self, pipeline):
        synchronizer = BookMetadataSynchronizer(
            pipeline=pipeline,
            session=MagicMock(),
        )
        synchronizer._download_image = MagicMock(return_value=b"\x47\x49")
        return synchronizer

    @patch(
        "books.services.book_metadata_sync.slugify",
        lambda value: "the-testing-book",
    )
    def test_sync_book_populates_missing_metadata(self):
        """
        The synchroniser should fill in description, authors, genres, ISBN and cover.
        """
        candidate = ExternalBook(
            title="The Testing Book",
            authors=["Jane Author"],
            categories=["Testing", "Technology"],
            description="A definitive guide to testing pipelines.",
            thumbnail_url="http://example.com/cover.jpg",
            isbn="9781234567890",
            publisher="Quality Press",
        )

        pipeline = MagicMock()
        pipeline.fetch.return_value = [candidate]

        synchronizer = self._build_synchronizer(pipeline)

        changed = synchronizer.sync_book(self.publication)
        self.assertTrue(changed)

        self.publication.refresh_from_db()
        self.assertEqual(self.publication.description, candidate.description)
        self.assertEqual(self.publication.isbn_13, candidate.isbn)
        self.assertEqual(self.publication.publisher.name, candidate.publisher)
        self.assertEqual(self.publication.authors.count(), 1)
        self.assertEqual(
            self.publication.authors.first().name,
            "Jane Author",
        )
        self.assertGreater(self.publication.genres.count(), 0)
        self.assertTrue(self.publication.cover_image.name.endswith(".jpg"))

    def test_sync_book_skips_when_no_query_available(self):
        """
        Books without title and ISBN should be skipped.
        """
        book = BookPublication.objects.create(title="")
        pipeline = MagicMock()

        synchronizer = self._build_synchronizer(pipeline)

        changed = synchronizer.sync_book(book)
        self.assertFalse(changed)
        pipeline.fetch.assert_not_called()

    def test_sync_book_propagates_external_errors(self):
        """
        Underlying API failures should surface so callers can handle them.
        """
        pipeline = MagicMock()
        pipeline.fetch.side_effect = ExternalBookAPIError()

        synchronizer = self._build_synchronizer(pipeline)

        with self.assertRaises(ExternalBookAPIError):
            synchronizer.sync_book(self.publication)

    def test_sync_queryset_counts_failures(self):
        """
        Batch synchronisation should count processed, updated, and failed books.
        """
        second_publication = BookPublication.objects.create(
            title="Another Testing Book",
        )
        BookCopy.objects.create(
            publication=second_publication,
            owner=self.owner,
        )

        first_candidate = ExternalBook(
            title="The Testing Book",
            authors=["Jane Author"],
            categories=["Testing"],
            description="desc",
            thumbnail_url=None,
            isbn="9781234567890",
            publisher=None,
        )

        pipeline = MagicMock()
        pipeline.fetch.side_effect = [
            [first_candidate],
            ExternalBookAPIError(),
        ]

        synchronizer = self._build_synchronizer(pipeline)

        summary = synchronizer.sync_queryset(
            BookPublication.objects.all(), limit=2
        )

        self.assertEqual(summary.processed, 2)
        self.assertEqual(summary.updated, 1)
        self.assertEqual(summary.failures, 1)
