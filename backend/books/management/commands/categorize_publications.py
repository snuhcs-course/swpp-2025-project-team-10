from __future__ import annotations

import json
from collections.abc import Iterable, Sequence

from accounts.models import BookGenre
from books.models import BookPublication, Genre
from books.services.publication_categories import (
    PublicationCategorizer,
    PublicationClassification,
    PublicationPayload,
)
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Classify publications with the LLM-backed PublicationCategorizer "
        "and persist the resulting taste profile + category scores."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            help="Maximum number of publications to process.",
        )
        parser.add_argument(
            "--ids",
            nargs="+",
            help="Specific publication UUIDs to process.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite cached JSON fields even if already set.",
        )
        parser.add_argument(
            "--skip-llm",
            action="store_true",
            help="Force heuristic mode (no LLM calls).",
        )
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only process publications without cached taste/category data.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run classification but do not write changes to the database.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=8,
            help="Number of publications to classify per LLM call (default: 8).",
        )

    def handle(self, *args, **options):
        limit: int | None = options["limit"]
        ids: Sequence[str] | None = options["ids"]
        overwrite: bool = options["overwrite"]
        skip_llm: bool = options["skip_llm"]
        only_missing: bool = options["only_missing"]
        dry_run: bool = options["dry_run"]
        batch_size: int = options["batch_size"] or 8

        if limit is not None and limit <= 0:
            raise CommandError("--limit must be a positive integer")
        if batch_size <= 0:
            raise CommandError("--batch-size must be a positive integer")

        qs = (
            BookPublication.objects.all()
            .prefetch_related("authors", "genres")
            .order_by("title")
        )
        if ids:
            qs = qs.filter(id__in=ids)

        categorizer = PublicationCategorizer(enable_llm=not skip_llm)
        stats = {
            "processed": 0,
            "updated": 0,
            "genre_updates": 0,
            "skipped": 0,
            "failures": 0,
        }

        pending: list[tuple[BookPublication, PublicationPayload]] = []

        for publication in qs.iterator(chunk_size=100):
            if limit is not None and stats["processed"] >= limit:
                break

            if (
                only_missing
                and not overwrite
                and publication.category_scores
                and publication.taste_profile
            ):
                stats["skipped"] += 1
                continue

            payload = self._build_payload(publication)
            pending.append((publication, payload))
            stats["processed"] += 1

            if len(pending) >= batch_size:
                self._flush_batch(
                    pending,
                    categorizer,
                    stats,
                    overwrite=overwrite,
                    dry_run=dry_run,
                )
                pending.clear()

        if pending:
            self._flush_batch(
                pending,
                categorizer,
                stats,
                overwrite=overwrite,
                dry_run=dry_run,
            )

        summary = (
            "Processed {processed}, updated {updated}, "
            "genre updates {genre_updates}, skipped {skipped}, "
            "failures {failures}."
        ).format(**stats)
        if stats["failures"]:
            self.stderr.write(self.style.WARNING(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))

    def _build_payload(
        self, publication: BookPublication
    ) -> PublicationPayload:
        authors = list(publication.authors.values_list("name", flat=True))
        genres = list(publication.genres.values_list("name", flat=True))
        description = publication.description or ""
        cover = None
        if publication.cover_image:
            cover = publication.cover_image.url
        return PublicationPayload(
            identifier=str(publication.pk),
            title=publication.title,
            description=description,
            authors=authors,
            genres=genres,
            cover_image=cover,
        )

    def _flush_batch(
        self,
        batch: list[tuple[BookPublication, PublicationPayload]],
        categorizer: PublicationCategorizer,
        stats: dict[str, int],
        *,
        overwrite: bool,
        dry_run: bool,
    ) -> None:
        payloads = [payload for _, payload in batch]
        try:
            classifications = categorizer.classify_many(payloads)
        except Exception as exc:  # pragma: no cover - defensive logging
            self.stderr.write(
                f"[WARN] Batch classification failed ({len(batch)} books): {exc}"
            )
            stats["failures"] += len(batch)
            return

        for publication, payload in batch:
            classification = classifications.get(payload.identifier)
            if classification is None:
                stats["failures"] += 1
                continue
            try:
                changed, genres_changed = self._persist_classification(
                    publication,
                    classification,
                    overwrite=overwrite,
                    dry_run=dry_run,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                stats["failures"] += 1
                self.stderr.write(
                    f"[WARN] Failed to persist classification for {publication.title}: {exc}"
                )
                continue
            if changed:
                stats["updated"] += 1
            if genres_changed:
                stats["genre_updates"] += 1

    def _persist_classification(
        self,
        publication: BookPublication,
        classification: PublicationClassification,
        *,
        overwrite: bool,
        dry_run: bool,
    ) -> tuple[bool, bool]:
        changed_fields: list[str] = []

        if (
            overwrite
            or publication.category_scores != classification.category_scores
        ):
            publication.category_scores = json.loads(
                json.dumps(classification.category_scores)
            )
            changed_fields.append("category_scores")

        if (
            overwrite
            or publication.taste_profile != classification.taste_profile
        ):
            publication.taste_profile = json.loads(
                json.dumps(classification.taste_profile)
            )
            changed_fields.append("taste_profile")

        genres_changed = self._sync_genre_relations(
            publication,
            classification.taste_profile.get("genres", []),
            overwrite=overwrite,
            dry_run=dry_run,
        )

        if changed_fields and not dry_run:
            publication.save(update_fields=changed_fields + ["updated_at"])

        return bool(changed_fields), genres_changed

    def _sync_genre_relations(
        self,
        publication: BookPublication,
        genre_keys: Iterable[str],
        *,
        overwrite: bool,
        dry_run: bool,
    ) -> bool:
        if not genre_keys:
            return False

        label_map = dict(BookGenre.choices)
        desired_labels = []
        for key in genre_keys:
            label = label_map.get(key)
            if not label:
                label = key.replace("_", " ").title()
            desired_labels.append(label)

        current_labels = set(publication.genres.values_list("name", flat=True))
        desired_set = set(desired_labels)
        if not overwrite and desired_set == current_labels:
            return False

        genre_objs = [
            Genre.objects.get_or_create(name=label)[0]
            for label in desired_labels
        ]

        if dry_run:
            return bool(desired_set - current_labels)

        with transaction.atomic():
            publication.genres.set(genre_objs)
        return True
