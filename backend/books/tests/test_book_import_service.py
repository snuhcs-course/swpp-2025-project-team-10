"""
Tests for the BookImportService responsible for creating book records.
"""

from __future__ import annotations

import shutil
import tempfile
from unittest.mock import MagicMock, patch

from books.models import BookCopy, BookPublication
from books.services.book_import_service import BookImportService, ImportSummary
from books.services.kakao_book_pipeline import (
    ExternalBook,
    ExternalBookAPIError,
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

User = get_user_model()


class BookImportServiceTestCase(TestCase):
    """
    Validate creation and update behaviour when importing from Kakao.
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
            username="importer",
            email="importer@example.com",
            password="pass1234",
        )

    def _build_service(self, pipeline, *, create_copies=True):
        synchronizer = MagicMock()
        synchronizer.apply_metadata.return_value = True

        service = BookImportService(
            pipeline=pipeline,
            synchronizer=synchronizer,
            create_copies=create_copies,
        )
        return service, synchronizer

    def _build_metadata(self, **overrides):
        data = {
            "title": "Default Title",
            "authors": ["Author"],
            "translators": [],
            "categories": ["Category"],
            "description": "Description",
            "thumbnail_url": "http://example.com/thumb.jpg",
            "isbn": "9780000000000",
            "publisher": "Publisher",
            "url": "http://example.com/book",
            "publication_date": "2024-01-01",
            "price": 10000,
            "sale_price": 9000,
            "status": "normal",
        }
        data.update(overrides)
        return ExternalBook(**data)

    def test_import_creates_new_book(self):
        """
        Import should create a book when no existing record matches.
        """
        metadata = self._build_metadata(
            title="Import Book",
            authors=["Jane Author"],
            categories=["New"],
            description="Imported description",
            isbn="9780000000000",
            publisher="Import Publisher",
        )

        pipeline = MagicMock()
        pipeline.fetch.return_value = [metadata]

        service, synchronizer = self._build_service(pipeline)

        summary = service.import_from_query("Import Book", owner=self.owner)

        self.assertEqual(summary, ImportSummary(1, 1, 0, 0, 0))
        copy_exists = BookCopy.objects.filter(
            owner=self.owner, publication__title="Import Book"
        ).exists()
        self.assertTrue(copy_exists)
        publication = BookPublication.objects.get(title="Import Book")
        synchronizer.apply_metadata.assert_called_once_with(
            publication,
            metadata,
            overwrite=True,
        )

    def test_import_updates_existing_book_when_overwrite_true(self):
        """
        Existing book should be updated when overwrite is enabled.
        """
        publication = BookPublication.objects.create(
            title="Existing Book",
            isbn_13="9781111111111",
        )
        BookCopy.objects.create(publication=publication, owner=self.owner)

        metadata = self._build_metadata(
            title="Existing Book",
            authors=["Jane Author"],
            categories=["Updated"],
            description="Updated description",
            thumbnail_url=None,
            isbn="9781111111111",
            publisher="Updated Publisher",
        )

        pipeline = MagicMock()
        pipeline.fetch.return_value = [metadata]

        service, synchronizer = self._build_service(pipeline)
        synchronizer.apply_metadata.return_value = True

        summary = service.import_from_query(
            "Existing Book",
            owner=self.owner,
            overwrite=True,
        )

        self.assertEqual(summary.updated, 1)
        synchronizer.apply_metadata.assert_called_with(
            publication,
            metadata,
            overwrite=True,
        )

    def test_import_skips_when_no_changes(self):
        """
        When metadata does not alter the existing book, it should be skipped.
        """
        publication = BookPublication.objects.create(
            title="Existing Book",
            isbn_13="9781111111111",
        )
        BookCopy.objects.create(publication=publication, owner=self.owner)

        metadata = self._build_metadata(
            title="Existing Book",
            authors=["Jane Author"],
            categories=["Updated"],
            description="Updated description",
            thumbnail_url=None,
            isbn="9781111111111",
            publisher="Updated Publisher",
        )

        pipeline = MagicMock()
        pipeline.fetch.return_value = [metadata]

        service, synchronizer = self._build_service(pipeline)
        synchronizer.apply_metadata.return_value = False

        summary = service.import_from_query(
            "Existing Book",
            owner=self.owner,
        )

        self.assertEqual(summary.skipped, 1)
        synchronizer.apply_metadata.assert_called_with(
            publication,
            metadata,
            overwrite=False,
        )

    def test_import_propagates_external_errors(self):
        """
        External API failures should bubble up so the caller can handle them.
        """
        pipeline = MagicMock()
        pipeline.fetch.side_effect = ExternalBookAPIError()

        service, _ = self._build_service(pipeline)

        with self.assertRaises(ExternalBookAPIError):
            service.import_from_query("Error query", owner=self.owner)

    def test_owner_required_when_creating_copies(self):
        """
        Service should raise when copy creation is enabled but owner is missing.
        """
        pipeline = MagicMock()
        pipeline.fetch.return_value = []
        service, _ = self._build_service(pipeline, create_copies=True)

        with self.assertRaises(ImproperlyConfigured):
            service.import_from_query("query", owner=None)

    def test_can_skip_copy_creation(self):
        """
        When create_copies=False, publications are created without book copies.
        """
        metadata = self._build_metadata(
            title="Copyless Book",
            authors=["Author"],
            categories=["Cat"],
            description="Desc",
            thumbnail_url=None,
            isbn="9782222222222",
            publisher="Pub",
        )
        pipeline = MagicMock()
        pipeline.fetch.return_value = [metadata]
        service, _ = self._build_service(pipeline, create_copies=False)

        summary = service.import_from_query("Copyless Book", owner=None)

        self.assertEqual(summary.created, 1)
        self.assertFalse(BookCopy.objects.exists())
        self.assertTrue(
            BookPublication.objects.filter(title="Copyless Book").exists()
        )
