"""
Services for importing new Book records from the Kakao Books API.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from books.models import BookCopy, BookPublication
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

from .book_metadata_sync import BookMetadataSynchronizer
from .kakao_book_pipeline import (
    ExternalBook,
    ExternalBookAPIError,
    KakaoBookPipeline,
)

User = get_user_model()

logger = logging.getLogger(__name__)


@dataclass
class ImportSummary:
    """
    Summary statistics for a Kakao import operation.
    """

    processed: int
    created: int
    updated: int
    skipped: int
    failures: int


class BookImportService:
    """Create or update publication metadata and user copies from Kakao results."""

    def __init__(
        self,
        pipeline: KakaoBookPipeline | None = None,
        synchronizer: BookMetadataSynchronizer | None = None,
        *,
        create_copies: bool = True,
    ) -> None:
        self.pipeline = pipeline or KakaoBookPipeline()
        self.synchronizer = synchronizer or BookMetadataSynchronizer(
            pipeline=self.pipeline
        )
        self.create_copies = create_copies

    def import_from_query(
        self,
        query: str,
        owner: User | None,
        *,
        size: int = KakaoBookPipeline.DEFAULT_SIZE,
        overwrite: bool = False,
    ) -> ImportSummary:
        """
        Import book metadata for a single query.
        """
        if not query.strip():
            return ImportSummary(0, 0, 0, 0, 0)

        if self.create_copies and owner is None:
            raise ImproperlyConfigured(
                "BookImportService requires an owner when create_copies=True."
            )

        try:
            documents = self.pipeline.fetch(query, size=size)
        except ExternalBookAPIError:
            logger.warning(
                "Kakao API request failed for query '%s'", query, exc_info=True
            )
            raise

        processed = 0
        created = 0
        updated = 0
        skipped = 0
        failures = 0

        for metadata in documents:
            processed += 1
            try:
                result = self._create_or_update_book(
                    metadata,
                    owner=owner,
                    overwrite=overwrite,
                )
            except Exception:  # pragma: no cover - defensive logging path
                logger.exception(
                    "Failed to import book metadata for '%s'", metadata.title
                )
                failures += 1
                continue

            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
            elif result == "skipped":
                skipped += 1

        return ImportSummary(
            processed=processed,
            created=created,
            updated=updated,
            skipped=skipped,
            failures=failures,
        )

    def _create_or_update_book(
        self,
        metadata: ExternalBook,
        *,
        owner: User | None,
        overwrite: bool,
    ) -> str:
        publication, created_publication = self._ensure_publication(metadata)

        changed_metadata = self.synchronizer.apply_metadata(
            publication,
            metadata,
            overwrite=True if created_publication else overwrite,
        )

        if self.create_copies:
            book_copy, created_copy = BookCopy.objects.get_or_create(
                publication=publication,
                owner=owner,
                defaults={
                    "is_for_barter": True,
                    "trade_status": BookCopy.TRADE_STATUS_CHOICES[0][0],
                },
            )

            if created_copy:
                return "created"
        elif created_publication:
            return "created"

        if changed_metadata:
            return "updated"

        return "skipped"

    def _ensure_publication(
        self,
        metadata: ExternalBook,
    ) -> tuple[BookPublication, bool]:
        isbn = metadata.isbn
        if isbn:
            publication = BookPublication.objects.filter(isbn_13=isbn).first()
            if publication:
                return publication, False
            publication = BookPublication.objects.filter(isbn_10=isbn).first()
            if publication:
                return publication, False

        if metadata.title:
            publication = BookPublication.objects.filter(
                title__iexact=metadata.title
            ).first()
            if publication:
                return publication, False

        return self._create_publication_skeleton(metadata), True

    @transaction.atomic
    def _create_publication_skeleton(
        self,
        metadata: ExternalBook,
    ) -> BookPublication:
        title = metadata.title or "Untitled Book"

        publication = BookPublication.objects.create(
            title=title,
            description=metadata.description or "",
        )
        return publication


def import_books(
    queries: Sequence[str],
    owner: User | None,
    *,
    size: int = KakaoBookPipeline.DEFAULT_SIZE,
    overwrite: bool = False,
    create_copies: bool = True,
) -> ImportSummary:
    """
    Convenience wrapper for importing multiple queries.
    """
    service = BookImportService(create_copies=create_copies)

    aggregated = ImportSummary(0, 0, 0, 0, 0)
    for query in queries:
        summary = service.import_from_query(
            query,
            owner=owner,
            size=size,
            overwrite=overwrite,
        )
        aggregated = ImportSummary(
            processed=aggregated.processed + summary.processed,
            created=aggregated.created + summary.created,
            updated=aggregated.updated + summary.updated,
            skipped=aggregated.skipped + summary.skipped,
            failures=aggregated.failures + summary.failures,
        )

    return aggregated
