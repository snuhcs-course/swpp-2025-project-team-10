"""
Management command to synchronise book metadata from the Kakao Books API.
"""

from __future__ import annotations

from collections.abc import Iterable

from books.models import BookPublication
from books.services.book_metadata_sync import BookMetadataSynchronizer
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.functions import Length


class Command(BaseCommand):
    help = (
        "Fetch book metadata from the Kakao Books API and update "
        "existing publication records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing metadata instead of filling missing fields only.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of books processed in this run.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process every publication, even if metadata is already populated.",
        )
        parser.add_argument(
            "--book-id",
            type=str,
            action="append",
            dest="book_ids",
            help="Only synchronise the specified publication IDs. Can be passed multiple times.",
        )
        parser.add_argument(
            "--truncated-only",
            action="store_true",
            help=(
                "Only process publications whose descriptions appear truncated "
                "(short previews or ellipsis markers)."
            ),
        )

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        limit = options["limit"]
        all_books = options["all"]
        book_ids: Iterable[str] | None = options.get("book_ids")
        truncated_only = options["truncated_only"]

        if limit is not None and limit <= 0:
            raise CommandError("The --limit value must be a positive integer.")

        queryset = BookPublication.objects.all()

        if book_ids:
            queryset = queryset.filter(id__in=book_ids)
        if truncated_only:
            length_threshold = BookMetadataSynchronizer.DESCRIPTION_MIN_LENGTH
            queryset = queryset.annotate(
                description_length=Length("description")
            )
            queryset = queryset.filter(
                Q(description__isnull=True)
                | Q(description__exact="")
                | Q(description_length__lt=length_threshold)
                | Q(description__icontains="...")
                | Q(description__icontains="…")
                | Q(description__contains="\u0001")
            )
        elif not all_books and not book_ids:
            queryset = queryset.filter(
                Q(description__isnull=True)
                | Q(description__exact="")
                | Q(cover_image__isnull=True)
                | Q(cover_image__exact="")
                | Q(authors__isnull=True)
                | Q(genres__isnull=True)
            ).distinct()

        synchronizer = BookMetadataSynchronizer()

        try:
            summary = synchronizer.sync_queryset(
                queryset,
                overwrite=overwrite,
                limit=limit,
            )
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc

        message = (
            f"Processed {summary.processed} book(s). "
            f"Updated: {summary.updated}. "
            f"Failures: {summary.failures}."
        )

        if summary.failures:
            self.stdout.write(self.style.WARNING(message))
        else:
            self.stdout.write(self.style.SUCCESS(message))
