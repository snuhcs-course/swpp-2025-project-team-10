from __future__ import annotations

import pytest
import requests
from books.services.kakao_book_pipeline import (
    ExternalBookAPIError,
    KakaoBookPipeline,
)
from django.test import override_settings


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError("boom")

    def json(self) -> dict:
        return self.payload


class _FakeSession:
    def __init__(
        self,
        response: _FakeResponse | None = None,
        exc: Exception | None = None,
    ) -> None:
        self.response = response
        self.exc = exc
        self.calls: list[tuple[tuple, dict]] = []

    def get(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.exc:
            raise self.exc
        return self.response


@override_settings(KAKAO_REST_API_KEY="test-key")
def test_fetch_normalises_documents_and_caps_size(monkeypatch):
    response = _FakeResponse(
        {
            "documents": [
                {
                    "title": "<b>Clean</b> Title ",
                    "contents": "<p>Desc</p>",
                    "category": "Fiction > Mystery",
                    "authors": [" Jane Doe ", ""],
                    "translators": [],
                    "thumbnail": "http://img.example.com/thumb.jpg",
                    "isbn": "1234567890 9781234567890",
                    "publisher": "Publisher ",
                    "url": " http://example.com ",
                    "datetime": "2023-05-01",
                    "price": 12000,
                    "sale_price": 9900,
                    "status": "정상",
                }
            ]
        }
    )
    session = _FakeSession(response=response)
    pipeline = KakaoBookPipeline(api_key="test-key", session=session)

    books = pipeline.fetch("  galaxy  ", page=3, size=200)

    assert len(books) == 1
    book = books[0]
    assert book.title == "Clean Title"
    assert book.description == "Desc"
    assert book.categories == ["Fiction", "Mystery"]
    assert book.authors == ["Jane Doe"]
    assert book.thumbnail_url.endswith("thumb.jpg")
    assert book.isbn == "9781234567890"
    assert session.calls[0][1]["params"]["size"] == pipeline.MAX_SIZE
    assert session.calls[0][1]["params"]["page"] == 3
    assert (
        session.calls[0][1]["headers"]["Authorization"] == "KakaoAK test-key"
    )


@override_settings(KAKAO_REST_API_KEY="another-key")
def test_fetch_returns_empty_on_blank_query():
    session = _FakeSession(response=_FakeResponse({"documents": []}))
    pipeline = KakaoBookPipeline(api_key="another-key", session=session)

    books = pipeline.fetch("   ")

    assert books == []
    assert session.calls == []


@override_settings(KAKAO_REST_API_KEY="key")
def test_fetch_wraps_request_errors():
    failure = _FakeSession(exc=requests.RequestException("timeout"))
    pipeline = KakaoBookPipeline(api_key="key", session=failure)

    with pytest.raises(ExternalBookAPIError):
        pipeline.fetch("query")


def test_select_isbn_prefers_longest_and_allows_missing():
    assert (
        KakaoBookPipeline._select_isbn("9780000000000 1234567890")
        == "9780000000000"
    )
    assert KakaoBookPipeline._select_isbn("1234567890") == "1234567890"
    assert KakaoBookPipeline._select_isbn("") is None
