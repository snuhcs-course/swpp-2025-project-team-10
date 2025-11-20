"""
Services for synchronising book publication records with the Kakao Books API.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlsplit

import requests
from books.models import Author, BookPublication, Genre, Publisher, Translator
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import QuerySet
from django.utils.text import slugify

from .kakao_book_pipeline import (
    ExternalBook,
    ExternalBookAPIError,
    KakaoBookPipeline,
)

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """
    Result summary for batch synchronisation.
    """

    processed: int
    updated: int
    failures: int


class BookMetadataSynchronizer:
    """Enrich internal publication metadata using Kakao book data."""

    IMAGE_TIMEOUT = 10
    DESCRIPTION_MIN_LENGTH = 110
    DESCRIPTION_TRUNCATION_MARKERS = ("...", "…", "\u0001")

    def __init__(
        self,
        pipeline: KakaoBookPipeline | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.pipeline = pipeline or KakaoBookPipeline()
        self.session = session or requests.Session()

    def sync_book(
        self, publication: BookPublication, *, overwrite: bool = False
    ) -> bool:
        """Enrich a single publication."""
        query = self._determine_query(publication)
        if not query:
            logger.debug(
                "Skipping publication %s due to missing query",
                publication.id,
            )
            return False

        try:
            candidates = self.pipeline.fetch(query, size=5)
        except ExternalBookAPIError:
            logger.warning(
                "Kakao API call failed while syncing publication %s",
                publication.id,
                exc_info=True,
            )
            raise

        match = self._select_match(publication, candidates)
        if not match:
            logger.debug(
                "No external match found for publication %s",
                publication.id,
            )
            return False

        return self.apply_metadata(publication, match, overwrite=overwrite)

    def sync_queryset(
        self,
        queryset: QuerySet[BookPublication],
        *,
        overwrite: bool = False,
        limit: int | None = None,
    ) -> SyncResult:
        """
        Loop through a queryset of books and enrich them sequentially.
        """
        processed = 0
        updated = 0
        failures = 0

        for publication in queryset.iterator():
            if limit is not None and processed >= limit:
                break

            processed += 1

            try:
                changed = self.sync_book(publication, overwrite=overwrite)
            except ExternalBookAPIError:
                failures += 1
                continue

            if changed:
                updated += 1

        return SyncResult(
            processed=processed, updated=updated, failures=failures
        )

    def _determine_query(self, publication: BookPublication) -> str | None:
        if publication.isbn_13:
            return publication.isbn_13
        if publication.isbn_10:
            return publication.isbn_10
        title = (publication.title or "").strip()
        if title:
            return title
        return None

    def _select_match(
        self,
        publication: BookPublication,
        candidates: Iterable[ExternalBook],
    ) -> ExternalBook | None:
        candidates = list(candidates)
        if not candidates:
            return None

        isbn_priority = [
            publication.isbn_13 or "",
            publication.isbn_10 or "",
        ]
        for isbn in isbn_priority:
            if not isbn:
                continue
            for candidate in candidates:
                if candidate.isbn == isbn:
                    return candidate

        for candidate in candidates:
            if candidate.title.lower() == publication.title.lower():
                return candidate

        return candidates[0]

    @transaction.atomic
    def apply_metadata(
        self,
        publication: BookPublication,
        metadata: ExternalBook,
        *,
        overwrite: bool,
    ) -> bool:
        fields_updated = set()
        changed = False

        # Sync description (contents from Kakao API, optionally crawling full text)
        description_source = metadata.description
        if metadata.url and self._should_fetch_full_description(
            description_source
        ):
            full_description = self._fetch_external_description(metadata.url)
            if full_description:
                description_source = full_description

        if description_source and (
            overwrite
            or not publication.description
            or description_source != metadata.description
        ):
            publication.description = description_source
            fields_updated.add("description")

        # Sync external URL
        if metadata.url and (overwrite or not publication.external_url):
            publication.external_url = metadata.url
            fields_updated.add("external_url")

        # Sync publication date
        if metadata.publication_date and (
            overwrite or not publication.publication_date
        ):
            # Parse ISO 8601 datetime to date
            pub_date = self._parse_publication_date(metadata.publication_date)
            if pub_date:
                publication.publication_date = pub_date
                fields_updated.add("publication_date")

        # Sync prices
        if metadata.price is not None and (
            overwrite or publication.original_price is None
        ):
            publication.original_price = metadata.price
            fields_updated.add("original_price")

        if metadata.sale_price is not None and (
            overwrite or publication.sale_price is None
        ):
            publication.sale_price = metadata.sale_price
            fields_updated.add("sale_price")

        # Sync sales status
        if metadata.status and (overwrite or not publication.sales_status):
            publication.sales_status = metadata.status
            fields_updated.add("sales_status")

        genres_changed = self._sync_genres(
            publication, metadata.categories, overwrite
        )
        authors_changed = self._sync_authors(
            publication, metadata.authors, overwrite
        )
        translators_changed = self._sync_translators(
            publication, metadata.translators, overwrite
        )
        cover_changed = self._sync_cover(
            publication, metadata.thumbnail_url, overwrite
        )

        publisher_changed = False
        if metadata.publisher and (overwrite or publication.publisher is None):
            publisher_obj, _ = Publisher.objects.get_or_create(
                name=metadata.publisher
            )
            if publication.publisher != publisher_obj:
                publication.publisher = publisher_obj
                fields_updated.add("publisher")
                publisher_changed = True

        isbn_fields = self._sync_isbn(publication, metadata.isbn, overwrite)
        if isbn_fields:
            fields_updated.update(isbn_fields)
            isbn_changed = True
        else:
            isbn_changed = False

        if fields_updated:
            publication.save(
                update_fields=list(fields_updated) + ["updated_at"]
            )
            changed = True

        if (
            authors_changed
            or translators_changed
            or genres_changed
            or cover_changed
            or publisher_changed
            or isbn_changed
        ):
            changed = True

        return changed

    def _sync_authors(
        self,
        publication: BookPublication,
        authors: Iterable[str],
        overwrite: bool,
    ) -> bool:
        authors = [author.strip() for author in authors if author.strip()]
        if not authors:
            return False

        existing_names = {author.name for author in publication.authors.all()}
        changed = False

        if overwrite:
            publication.authors.clear()
            existing_names.clear()

        for author_name in authors:
            if author_name in existing_names:
                continue
            author_obj, _ = Author.objects.get_or_create(name=author_name)
            publication.authors.add(author_obj)
            changed = True

        return changed

    def _sync_translators(
        self,
        publication: BookPublication,
        translators: Iterable[str],
        overwrite: bool,
    ) -> bool:
        translators = [
            translator.strip()
            for translator in translators
            if translator.strip()
        ]
        if not translators:
            return False

        existing_names = {
            translator.name for translator in publication.translators.all()
        }
        changed = False

        if overwrite:
            publication.translators.clear()
            existing_names.clear()

        for translator_name in translators:
            if translator_name in existing_names:
                continue
            translator_obj, _ = Translator.objects.get_or_create(
                name=translator_name
            )
            publication.translators.add(translator_obj)
            changed = True

        return changed

    def _sync_isbn(
        self,
        publication: BookPublication,
        external_isbn: str | None,
        overwrite: bool,
    ) -> set[str]:
        if not external_isbn:
            return set()

        external_isbn = external_isbn.strip()
        if not external_isbn:
            return set()

        isbn13 = external_isbn if len(external_isbn) == 13 else None
        isbn10 = external_isbn if len(external_isbn) == 10 else None

        fields = set()

        if (
            isbn13
            and (overwrite or not publication.isbn_13)
            and publication.isbn_13 != isbn13
        ):
            if self._isbn_in_use("isbn_13", isbn13, publication):
                logger.warning(
                    "Skipping ISBN-13 %s for publication %s because another record already uses it.",
                    isbn13,
                    publication.pk,
                )
            else:
                publication.isbn_13 = isbn13
                fields.add("isbn_13")

        if (
            isbn10
            and (overwrite or not publication.isbn_10)
            and publication.isbn_10 != isbn10
        ):
            if self._isbn_in_use("isbn_10", isbn10, publication):
                logger.warning(
                    "Skipping ISBN-10 %s for publication %s because another record already uses it.",
                    isbn10,
                    publication.pk,
                )
            else:
                publication.isbn_10 = isbn10
                fields.add("isbn_10")

        return fields

    @staticmethod
    def _isbn_in_use(
        field_name: str,
        value: str,
        publication: BookPublication,
    ) -> bool:
        if not value:
            return False

        filter_kwargs = {field_name: value}
        return (
            BookPublication.objects.filter(**filter_kwargs)
            .exclude(pk=publication.pk)
            .exists()
        )

    def _sync_genres(
        self,
        publication: BookPublication,
        categories: Iterable[str],
        overwrite: bool,
    ) -> bool:
        categories = [
            category.strip() for category in categories if category.strip()
        ]
        if not categories:
            return False

        existing_names = {genre.name for genre in publication.genres.all()}
        changed = False

        if overwrite:
            publication.genres.clear()
            existing_names.clear()

        for category in categories:
            genre_obj, _ = Genre.objects.get_or_create(name=category)
            if genre_obj.name in existing_names:
                continue
            publication.genres.add(genre_obj)
            changed = True

        return changed

    def _sync_cover(
        self,
        publication: BookPublication,
        thumbnail_url: str | None,
        overwrite: bool,
    ) -> bool:
        if not thumbnail_url:
            return False

        if publication.cover_image and not overwrite:
            return False

        content = self._download_image(thumbnail_url)
        if content is None:
            return False

        path = urlsplit(thumbnail_url).path
        extension = os.path.splitext(path)[1] or ".jpg"
        slug = slugify(publication.title) or "book"
        field = publication._meta.get_field("cover_image")
        max_length = getattr(field, "max_length", 100) or 100
        prefix = (
            field.upload_to.rstrip("/") + "/"
            if isinstance(field.upload_to, str)
            else "book_covers/"
        )
        max_slug_length = max(1, max_length - len(prefix) - len(extension))
        safe_slug = slug[:max_slug_length]
        filename = f"{safe_slug}{extension}"
        publication.cover_image.save(filename, ContentFile(content), save=True)

        return True

    def _download_image(self, url: str) -> bytes | None:
        try:
            response = self.session.get(url, timeout=self.IMAGE_TIMEOUT)
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            logger.debug(
                "Failed to download cover image from %s", url, exc_info=True
            )
            return None

    def _should_fetch_full_description(self, snippet: str | None) -> bool:
        if not snippet:
            return True

        stripped = snippet.strip()
        if any(
            marker in stripped
            for marker in self.DESCRIPTION_TRUNCATION_MARKERS
        ):
            return True

        return len(stripped) < self.DESCRIPTION_MIN_LENGTH

    def _fetch_external_description(self, url: str) -> str | None:
        try:
            response = self.session.get(url, timeout=self.IMAGE_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException:
            logger.debug(
                "Failed to fetch extended description from %s",
                url,
                exc_info=True,
            )
            return None

        parser = _SimpleHTMLParser()
        parser.feed(response.text)
        parser.close()
        return self._extract_description_from_dom(parser.root)

    def _extract_description_from_dom(self, root: _HTMLNode) -> str | None:
        tab_content = self._find_node(
            root,
            lambda node: node.tag == "div"
            and node.attrs.get("id") == "tabContent",
        )

        def resolve_path(container: _HTMLNode | None) -> str | None:
            if container is None:
                return None
            first_section = self._nth_child(container, "div", 1)
            if not first_section:
                return None
            third_column = self._nth_child(first_section, "div", 3)
            if not third_column:
                return None
            paragraph = self._nth_child(third_column, "p", 1)
            if not paragraph:
                return None
            text = paragraph.get_text().strip()
            return text or None

        text = resolve_path(tab_content)
        if text:
            return text

        # Fall back to the first paragraph whose class contains "desc"
        def has_desc_class(node: _HTMLNode) -> bool:
            cls = node.attrs.get("class") or ""
            return "desc" in cls

        for scope in filter(None, [tab_content, root]):
            node = self._find_node(
                scope,
                lambda n: n.tag == "p" and has_desc_class(n),
            )
            if node:
                text = node.get_text().strip()
                if text:
                    return text

        return None

    def _find_node(
        self,
        node: _HTMLNode,
        predicate: Callable[[_HTMLNode], bool],
    ) -> _HTMLNode | None:
        if predicate(node):
            return node

        for child in node.children:
            found = self._find_node(child, predicate)
            if found:
                return found
        return None

    @staticmethod
    def _nth_child(
        node: _HTMLNode,
        tag: str,
        index: int,
    ) -> _HTMLNode | None:
        count = 0
        for child in node.children:
            if child.tag == tag:
                count += 1
                if count == index:
                    return child
        return None

    @staticmethod
    def _parse_publication_date(datetime_str: str) -> object | None:
        """
        Parse ISO 8601 datetime string to date object.
        Format: [YYYY]-[MM]-[DD]T[hh]:[mm]:[ss].000+[tz]
        """
        from datetime import datetime

        if not datetime_str:
            return None

        try:
            # Parse ISO 8601 format and extract date
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return dt.date()
        except (ValueError, AttributeError):
            logger.debug("Failed to parse publication date: %s", datetime_str)
            return None


class _HTMLNode:
    __slots__ = ("tag", "attrs", "children", "text")

    def __init__(self, tag: str, attrs: dict[str, str]):
        self.tag = tag
        self.attrs = attrs
        self.children: list[_HTMLNode] = []
        self.text: list[str] = []

    def get_text(self) -> str:
        parts: list[str] = []
        parts.extend(self.text)
        for child in self.children:
            child_text = child.get_text()
            if child_text:
                parts.append(child_text)
        return "".join(parts)


class _SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _HTMLNode("document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _HTMLNode(tag, dict(attrs))
        self.stack[-1].children.append(node)
        self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = _HTMLNode(tag, dict(attrs))
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not data:
            return
        self.stack[-1].text.append(data)


def sync_book_metadata(
    queryset: QuerySet[BookPublication],
    *,
    overwrite: bool = False,
    limit: int | None = None,
) -> SyncResult:
    """
    Convenience function for bulk synchronisation.
    """
    synchronizer = BookMetadataSynchronizer()
    return synchronizer.sync_queryset(
        queryset, overwrite=overwrite, limit=limit
    )
