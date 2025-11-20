"""
Import book metadata from the Kakao Books API and create local records.
"""

from __future__ import annotations

from books.services.book_import_service import BookImportService
from books.services.kakao_book_pipeline import (
    ExternalBookAPIError,
    KakaoBookPipeline,
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Search the Kakao Books API and create Book records in the local database."

    def add_arguments(self, parser):
        parser.add_argument(
            "queries",
            nargs="+",
            help="Search keywords or ISBNs to import. Multiple queries are allowed.",
        )
        parser.add_argument(
            "--owner-id",
            type=int,
            help="ID of the user who will be set as the owner of imported books.",
        )
        parser.add_argument(
            "--owner-email",
            help="Email of the user who will be set as the owner of imported books.",
        )
        parser.add_argument(
            "--size",
            type=int,
            default=KakaoBookPipeline.DEFAULT_SIZE,
            help="Number of results to request from Kakao for each query (default: 10).",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing metadata for matching books.",
        )

    def handle(self, *args, **options):
        queries: list[str] = options["queries"]
        owner = self._resolve_owner(
            owner_id=options.get("owner_id"),
            owner_email=options.get("owner_email"),
        )
        size = options["size"]
        overwrite = options["overwrite"]

        if size <= 0:
            raise CommandError("The --size option must be a positive integer.")

        try:
            service = BookImportService()
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc
        aggregated = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failures": 0,
        }

        for query in queries:
            try:
                summary = service.import_from_query(
                    query,
                    owner=owner,
                    size=size,
                    overwrite=overwrite,
                )
            except ImproperlyConfigured as exc:
                raise CommandError(str(exc)) from exc
            except ExternalBookAPIError as exc:
                raise CommandError(f"Kakao API request failed: {exc}") from exc

            aggregated["processed"] += summary.processed
            aggregated["created"] += summary.created
            aggregated["updated"] += summary.updated
            aggregated["skipped"] += summary.skipped
            aggregated["failures"] += summary.failures

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{query}] Processed {summary.processed}, "
                    f"created {summary.created}, "
                    f"updated {summary.updated}, "
                    f"skipped {summary.skipped}, "
                    f"failures {summary.failures}."
                )
            )

        totals_message = (
            "Total: processed {processed}, created {created}, "
            "updated {updated}, skipped {skipped}, failures {failures}."
        ).format(**aggregated)

        if aggregated["failures"]:
            self.stdout.write(self.style.WARNING(totals_message))
        else:
            self.stdout.write(self.style.SUCCESS(totals_message))

    def _resolve_owner(
        self,
        *,
        owner_id: int | None,
        owner_email: str | None,
    ) -> User:
        if owner_id is None and owner_email is None:
            raise CommandError(
                "Provide --owner-id or --owner-email to assign book ownership."
            )

        try:
            if owner_id is not None:
                return User.objects.get(id=owner_id)
            return User.objects.get(email=owner_email)
        except User.DoesNotExist as exc:
            raise CommandError(
                "Could not find the specified owner user."
            ) from exc
