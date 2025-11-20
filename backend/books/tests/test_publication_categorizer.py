import json

import books.services.publication_categories as publication_categories
from accounts.models import BookGenre, BookLength, BookMood, ReadingPurpose
from books.services.publication_categories import (
    PublicationCategorizer,
    PublicationClassification,
    PublicationPayload,
    keyword_present,
)


class _StubLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def generate(
        self, *args, **kwargs
    ):  # pragma: no cover - exercised via categorizer
        self.calls += 1
        return self.response


def _payload(
    description: str = "mystery case", genres: list[str] | None = None
):
    return PublicationPayload(
        identifier="test",
        title="Sample",
        description=description,
        authors=["Author"],
        genres=genres or ["Mystery"],
    )


class _BatchLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.kwargs = {}

    def generate(self, *_, **kwargs):
        self.kwargs = kwargs
        return self.response


class _Message:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


def test_categorizer_prefers_llm_response():
    llm = _StubLLM('[{"label": "Psychological Fiction", "score": 0.91}]')
    categorizer = PublicationCategorizer(llm_client=llm, enable_llm=False)

    result = categorizer.classify(_payload())

    assert llm.calls == 1
    assert result.category_scores[0]["label"] == "Psychological Fiction"
    assert result.category_scores[0]["score"] == 0.91
    assert result.taste_profile["genres"], "Expected taste profile fallback"


def test_categorizer_falls_back_to_heuristics():
    categorizer = PublicationCategorizer(enable_llm=False)

    result = categorizer.classify(
        _payload(
            description="A hopeful coming-of-age story",
            genres=["Coming Of Age"],
        )
    )

    assert result.category_scores, "Expected heuristic categories"
    top = result.category_scores[0]
    assert 0 <= top["score"] <= 1
    assert result.taste_profile["genres"]
    assert result.taste_profile["moods"]


def test_classify_many_batches_and_fills_missing_entries(monkeypatch):
    """
    Batch classification should use LLM output when available and fall back
    to heuristics for any publications not present in the payload.
    """
    monkeypatch.setattr(publication_categories, "Message", _Message)
    batch_payload = json.dumps(
        [
            {
                "id": "one",
                "categories": [{"label": "Mystery & Thriller", "score": 0.82}],
                "tasteProfile": {
                    "genres": ["NOVEL"],
                    "moods": ["MYSTERIOUS"],
                    "purposes": ["ESCAPISM"],
                    "length": "LONG",
                },
            }
        ]
    )
    llm = _BatchLLM(batch_payload)
    categorizer = PublicationCategorizer(llm_client=llm)
    books = [
        PublicationPayload(
            identifier="one",
            title="Galactic Secrets",
            description="Space thriller with mystery elements",
            authors=["A. Writer"],
            genres=["Science"],
        ),
        PublicationPayload(
            identifier="two",
            title="Quiet essays",
            description="Gentle reflections on daily life",
            authors=["B. Writer"],
            genres=["Essay"],
        ),
    ]

    result = categorizer.classify_many(books)

    assert llm.kwargs["max_tokens"] == min(1500, 260 + len(books) * 140)
    assert result["one"].category_scores[0]["label"] == "Mystery & Thriller"
    assert result["one"].taste_profile["length"] == str(BookLength.LONG)
    # Second payload is missing from the LLM response -> heuristic fallback
    assert "two" in result
    assert result["two"].category_scores
    assert result["two"].taste_profile["genres"]


def test_parse_llm_response_normalises_scores_and_taste():
    categorizer = PublicationCategorizer(enable_llm=False)
    payload = PublicationPayload(
        identifier="normalize",
        title="Deep Work",
        description="Serious and calm guidance for focused study sessions",
        authors=["Cal Newport"],
        genres=["Non-fiction"],
    )
    raw = json.dumps(
        {
            "categoryScores": [
                {"name": "Focus", "confidence": "1.4"},
                {"label": "Noise", "score": -3},
                "ignore-me",
            ],
            "taste": {
                "genres": "Novel|Essay|Invalid",
                "moods": ["calm", "SERIOUS", "calm"],
                "purposes": ["study", "unknown"],
                "bookLength": "long",
            },
        }
    )

    classification = categorizer._parse_llm_response(raw, payload)

    assert classification is not None
    assert classification.category_scores[0]["score"] == 1.0
    assert classification.category_scores[-1]["score"] == 0.0
    assert classification.taste_profile["genres"] == [
        str(BookGenre.NOVEL),
        str(BookGenre.ESSAY),
    ]
    assert classification.taste_profile["moods"] == [
        str(BookMood.CALM),
        str(BookMood.SERIOUS),
    ]
    assert classification.taste_profile["purposes"] == [
        str(ReadingPurpose.STUDY)
    ]
    assert classification.taste_profile["length"] == str(BookLength.LONG)


def test_extract_json_handles_wrapped_payload():
    raw = 'Some noise before {"hello": "world"} trailing tokens'

    snippet = PublicationCategorizer._extract_json(raw)

    assert snippet == '{"hello": "world"}'


def test_heuristic_classification_sets_defaults_when_empty():
    categorizer = PublicationCategorizer(enable_llm=False)
    publication = PublicationPayload(
        identifier="empty",
        title="Untitled",
        description="",
        authors=[],
        genres=[],
    )

    classification = categorizer._heuristic_classification(publication)

    assert classification.category_scores[0]["label"] == "General Interest"
    assert classification.taste_profile["genres"] == [str(BookGenre.NOVEL)]
    assert classification.taste_profile["length"] == str(BookLength.MEDIUM)


def test_publication_classification_default_values():
    classification = PublicationClassification([], {})

    classification.ensure_defaults()

    assert classification.category_scores[0]["label"] == "General Interest"
    assert classification.taste_profile["genres"] == [str(BookGenre.NOVEL)]
    assert classification.taste_profile["moods"] == [str(BookMood.SERIOUS)]
    assert classification.taste_profile["purposes"] == [
        str(ReadingPurpose.INSPIRATION)
    ]
    assert classification.taste_profile["length"] == str(BookLength.MEDIUM)


def test_keyword_present_matches_substrings():
    assert keyword_present("Science fiction", ("science",))
    assert not keyword_present("Romantic comedy", ("mystery",))
