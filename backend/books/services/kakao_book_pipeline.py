"""
Pipeline for retrieving book metadata from the Kakao Books Search API.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


class ExternalBookAPIError(Exception):
    """
    Raised when the external book API interaction fails.
    """


@dataclass
class ExternalBook:
    """
    Normalised representation of external book metadata.
    """

    title: str
    authors: list[str]
    translators: list[str]
    categories: list[str]
    description: str
    thumbnail_url: str | None
    isbn: str | None
    publisher: str | None
    url: str | None
    publication_date: str | None
    price: int | None
    sale_price: int | None
    status: str | None

    def to_payload(self) -> dict[str, Any]:
        """
        Return a serialisable payload that matches frontend expectations.
        """
        return {
            "title": self.title,
            "authors": self.authors,
            "translators": self.translators,
            "categories": self.categories,
            "description": self.description,
            "thumbnailUrl": self.thumbnail_url,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "url": self.url,
            "publicationDate": self.publication_date,
            "price": self.price,
            "salePrice": self.sale_price,
            "status": self.status,
        }


class KakaoBookPipeline:
    """
    Client and normalisation pipeline for the Kakao Books API.
    """

    BASE_URL = "https://dapi.kakao.com/v3/search/book"
    DEFAULT_SIZE = 10
    MAX_SIZE = 50
    MAX_PAGE = 50
    TIMEOUT_SECONDS = 10

    def __init__(
        self,
        api_key: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key or getattr(settings, "KAKAO_REST_API_KEY", None)
        if not self.api_key:
            raise ImproperlyConfigured(
                "KAKAO_REST_API_KEY is not configured. "
                "Set it in your environment variables.",
            )

        self.session = session or requests.Session()

    def fetch(
        self,
        query: str,
        *,
        page: int = 1,
        size: int = DEFAULT_SIZE,
    ) -> list[ExternalBook]:
        """
        Fetch and normalise book search results for the provided query.
        """
        if not query.strip():
            return []

        capped_size = min(max(size, 1), self.MAX_SIZE)
        capped_page = min(max(page, 1), self.MAX_PAGE)

        headers = {"Authorization": f"KakaoAK {self.api_key}"}
        params = {
            "query": query.strip(),
            "page": capped_page,
            "size": capped_size,
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Kakao book API request failed: %s", exc)
            raise ExternalBookAPIError(
                "Failed to fetch data from Kakao API",
            ) from exc

        payload = response.json()
        documents = payload.get("documents", [])

        return [self._normalise_document(document) for document in documents]

    def fetch_payload(
        self,
        query: str,
        *,
        page: int = 1,
        size: int = DEFAULT_SIZE,
    ) -> list[dict[str, Any]]:
        """
        Fetch book data and return a serialisable payload.
        """
        books = self.fetch(query, page=page, size=size)
        return [book.to_payload() for book in books]

    def _normalise_document(self, document: dict[str, Any]) -> ExternalBook:
        """
        Convert a raw Kakao document into the ExternalBook dataclass.
        """
        title = self._clean_text(document.get("title", ""))
        description = self._clean_text(document.get("contents", "")).strip()

        thumbnail = self._safe_str(document.get("thumbnail"))
        thumbnail_url = thumbnail or None

        categories = self._parse_categories(document.get("category", ""))
        authors = self._ensure_list_of_str(document.get("authors", []))
        translators = self._ensure_list_of_str(document.get("translators", []))
        publisher = self._safe_str(document.get("publisher")) or None
        isbn = self._select_isbn(document.get("isbn", ""))
        url = self._safe_str(document.get("url")) or None
        publication_date = self._safe_str(document.get("datetime")) or None
        price = document.get("price")
        sale_price = document.get("sale_price")
        status = self._safe_str(document.get("status")) or None

        return ExternalBook(
            title=title,
            authors=authors,
            translators=translators,
            categories=categories,
            description=description,
            thumbnail_url=thumbnail_url,
            isbn=isbn,
            publisher=publisher,
            url=url,
            publication_date=publication_date,
            price=price,
            sale_price=sale_price,
            status=status,
        )

    @staticmethod
    def _clean_text(value: str) -> str:
        return HTML_TAG_PATTERN.sub("", value).strip()

    @staticmethod
    def _parse_categories(value: str) -> list[str]:
        parts = [part.strip() for part in value.split(">")]
        return [part for part in parts if part]

    @staticmethod
    def _ensure_list_of_str(values: Iterable[Any]) -> list[str]:
        return [str(value).strip() for value in values if str(value).strip()]

    @staticmethod
    def _safe_str(value: Any) -> str:
        return str(value).strip() if value else ""

    @staticmethod
    def _select_isbn(value: str) -> str | None:
        if not value:
            return None

        candidates = [item.strip() for item in value.split() if item.strip()]

        isbn13 = next((item for item in candidates if len(item) == 13), None)
        if isbn13:
            return isbn13

        return next((item for item in candidates if len(item) == 10), None)
