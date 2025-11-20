"""LLM-enabled categorisation utilities for book publications."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from accounts.models import BookGenre, BookLength, BookMood, ReadingPurpose

try:  # pragma: no cover - optional dependency
    from llm.client import LLMClient, Message  # type: ignore
except ImportError:  # pragma: no cover - exercised in tests
    LLMClient = None  # type: ignore
    Message = None  # type: ignore

logger = logging.getLogger(__name__)

BOOK_GENRE_KEYS: list[str] = [choice[0] for choice in BookGenre.choices]
BOOK_MOOD_KEYS: list[str] = [choice[0] for choice in BookMood.choices]
BOOK_LENGTH_KEYS: list[str] = [choice[0] for choice in BookLength.choices]
READING_PURPOSE_KEYS: list[str] = [
    choice[0] for choice in ReadingPurpose.choices
]

GENRE_KEYWORDS: dict[str, tuple[str, ...]] = {
    str(BookGenre.NOVEL): (
        "novel",
        "fiction",
        "문학",
        "서사",
        "스토리",
        "story",
        "romance",
    ),
    str(BookGenre.ESSAY): (
        "essay",
        "에세이",
        "随筆",
        "산문",
        "에세이집",
    ),
    str(BookGenre.POETRY): (
        "poetry",
        "poem",
        "시집",
        "lyrics",
        "lyrical",
    ),
    str(BookGenre.SELF_HELP): (
        "self-help",
        "자기계발",
        "growth",
        "습관",
        "회복",
        "동기",
    ),
    str(BookGenre.SCIENCE_TECH): (
        "science",
        "과학",
        "기술",
        "space",
        "우주",
        "physics",
        "data",
        "robot",
    ),
    str(BookGenre.HUMANITIES_SOCIAL): (
        "humanities",
        "social",
        "사회",
        "문화",
        "anthropology",
        "인문",
        "sociology",
    ),
    str(BookGenre.HISTORY_PHILOSOPHY): (
        "history",
        "역사",
        "철학",
        "사상",
        "dynasty",
        "과거",
    ),
    str(BookGenre.ART_LANGUAGE): (
        "art",
        "예술",
        "design",
        "언어",
        "language",
        "문체",
    ),
    str(BookGenre.ECONOMICS_BUSINESS): (
        "economics",
        "경제",
        "business",
        "경영",
        "finance",
        "startup",
    ),
}

MOOD_KEYWORDS: dict[str, tuple[str, ...]] = {
    str(BookMood.WARM): (
        "warm",
        "따뜻",
        "healing",
        "위로",
        "comfort",
    ),
    str(BookMood.SERIOUS): (
        "serious",
        "진지",
        "grave",
        "무게",
        "철학적",
    ),
    str(BookMood.HUMOROUS): (
        "humor",
        "humorous",
        "lighthearted",
        "재미",
        "웃음",
    ),
    str(BookMood.TOUCHING): (
        "touching",
        "감동",
        "heartfelt",
        "moving",
    ),
    str(BookMood.IMMERSIVE): (
        "immersive",
        "몰입",
        "thrilling",
        "intense",
    ),
    str(BookMood.CALM): (
        "calm",
        "차분",
        "잔잔",
        "quiet",
        "묵직",
    ),
    str(BookMood.MYSTERIOUS): (
        "mysterious",
        "mystery",
        "신비",
        "enigmatic",
    ),
    str(BookMood.SHARP): (
        "sharp",
        "insightful",
        "예리",
        "분석적",
    ),
    str(BookMood.ENERGETIC): (
        "energetic",
        "역동",
        "활기",
        "dynamic",
    ),
}

PURPOSE_KEYWORDS: dict[str, tuple[str, ...]] = {
    str(ReadingPurpose.STUDY): (
        "study",
        "학습",
        "공부",
        "지식",
        "research",
    ),
    str(ReadingPurpose.HEALING): (
        "healing",
        "회복",
        "휴식",
        "치유",
        "웰빙",
    ),
    str(ReadingPurpose.INSPIRATION): (
        "inspiration",
        "영감",
        "motivation",
        "창작",
    ),
    str(ReadingPurpose.LIGHT_READING): (
        "light",
        "가벼운",
        "쉬운",
        "재미",
        "여가",
    ),
    str(ReadingPurpose.DEEP_READING): (
        "deep",
        "심층",
        "몰입",
        "철학",
    ),
    str(ReadingPurpose.NEW_PERSPECTIVE): (
        "perspective",
        "관점",
        "통찰",
        "새로운 시각",
    ),
    str(ReadingPurpose.CULTURE): (
        "culture",
        "교양",
        "문화",
        "society",
    ),
    str(ReadingPurpose.PROBLEM_SOLVING): (
        "problem",
        "solution",
        "문제 해결",
        "전략",
    ),
    str(ReadingPurpose.ESCAPISM): (
        "escape",
        "도피",
        "상상",
        "환상",
    ),
}

LENGTH_KEYWORDS: dict[str, tuple[str, ...]] = {
    str(BookLength.SHORT): (
        "short story",
        "short",
        "에세이",
        "간결",
        "compact",
    ),
    str(BookLength.LONG): (
        "epic",
        "대하",
        "장편",
        "saga",
        "comprehensive",
        "long",
    ),
}


@dataclass(slots=True)
class PublicationPayload:
    """Light-weight representation of a book publication."""

    identifier: str
    title: str
    description: str
    authors: list[str]
    genres: list[str]
    cover_image: str | None = None


@dataclass(slots=True)
class PublicationClassification:
    """Container for LLM classification plus taste profile metadata."""

    category_scores: list[dict[str, float]]
    taste_profile: dict[str, object]

    def ensure_defaults(self) -> None:
        if not self.category_scores:
            self.category_scores = [
                {"label": "General Interest", "score": 0.45}
            ]
        if (
            "genres" not in self.taste_profile
            or not self.taste_profile["genres"]
        ):
            self.taste_profile["genres"] = [str(BookGenre.NOVEL)]
        if (
            "moods" not in self.taste_profile
            or not self.taste_profile["moods"]
        ):
            self.taste_profile["moods"] = [str(BookMood.SERIOUS)]
        if (
            "purposes" not in self.taste_profile
            or not self.taste_profile["purposes"]
        ):
            self.taste_profile["purposes"] = [str(ReadingPurpose.INSPIRATION)]
        if not self.taste_profile.get("length"):
            self.taste_profile["length"] = str(BookLength.MEDIUM)


class PublicationCategorizer:
    """Generate category scores for publications via LLM with heuristic fallback."""

    KEYWORD_MAP: dict[str, tuple[str, ...]] = {
        "Mystery & Thriller": (
            "mystery",
            "thriller",
            "범죄",
            "살인",
            "추리",
            "suspense",
            "detective",
        ),
        "Science Fiction": (
            "sf",
            "space",
            "우주",
            "외계",
            "dystopia",
            "robot",
            "time travel",
        ),
        "Fantasy": (
            "fantasy",
            "dragon",
            "magic",
            "마법",
            "myth",
            "quest",
        ),
        "Romance": (
            "romance",
            "사랑",
            "연애",
            "relationship",
            "heart",
        ),
        "Historical Fiction": (
            "historical",
            "조선",
            "dynasty",
            "전쟁",
            "역사",
            "시대",
        ),
        "Literary Fiction": (
            "literary",
            "coming-of-age",
            "identity",
            "서정",
            "청춘",
        ),
        "Self-Help & Growth": (
            "self-help",
            "growth",
            "마인드",
            "습관",
            "회복",
            "치유",
        ),
        "Non-fiction": (
            "에세이",
            "essay",
            "memoir",
            "biography",
            "논픽션",
        ),
    }

    def __init__(
        self,
        llm_client: Any | None = None,
        *,
        enable_llm: bool = True,
    ) -> None:
        self.enable_llm = enable_llm
        self.llm_client = llm_client or self._maybe_init_llm()

    def classify(
        self, publication: PublicationPayload
    ) -> PublicationClassification:
        """Return LLM classification plus enriched taste metadata."""
        if self.llm_client is not None:
            try:
                return self._classify_with_llm(publication)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "LLM classification failed: %s", exc, exc_info=True
                )
        return self._heuristic_classification(publication)

    def classify_many(
        self, publications: Sequence[PublicationPayload]
    ) -> dict[str, PublicationClassification]:
        """Classify multiple publications in a single pass when possible."""
        if not publications:
            return {}
        if len(publications) == 1:
            classification = self.classify(publications[0])
            return {publications[0].identifier: classification}

        if self.llm_client is None:
            return {
                payload.identifier: self._heuristic_classification(payload)
                for payload in publications
            }

        try:
            return self._classify_batch_with_llm(publications)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning(
                "Batch LLM classification failed, retrying individually: %s",
                exc,
                exc_info=True,
            )
            return {
                payload.identifier: self.classify(payload)
                for payload in publications
            }

    # ------------------------------------------------------------------
    # LLM helpers
    # ------------------------------------------------------------------

    def _maybe_init_llm(self) -> Any | None:
        if not self.enable_llm or LLMClient is None:
            return None
        try:
            return LLMClient()
        except Exception as exc:  # pragma: no cover - depends on env setup
            logger.info("LLM client unavailable: %s", exc)
            return None

    def _classify_with_llm(
        self, publication: PublicationPayload
    ) -> PublicationClassification:
        if Message is None:
            messages: list[dict[str, str]] = [
                {
                    "role": "system",
                    "content": (
                        "You are a book taxonomy expert helping a reading "
                        "preference survey. Always reply with valid JSON."
                    ),
                },
                {"role": "user", "content": self._build_prompt(publication)},
            ]
        else:
            messages = [
                Message(
                    role="system",
                    content=(
                        "You are a book taxonomy expert helping a reading preference "
                        "survey. Always reply with valid JSON."
                    ),
                ),
                Message(role="user", content=self._build_prompt(publication)),
            ]
        raw = self.llm_client.generate(
            messages, temperature=0.2, max_tokens=400
        )
        logger.debug(
            "LLM response (single) for %s: %s",
            publication.identifier,
            raw,
        )
        classification = self._parse_llm_response(raw, publication)
        if classification is None:
            return self._heuristic_classification(publication)
        classification.ensure_defaults()
        return classification

    def _classify_batch_with_llm(
        self, publications: Sequence[PublicationPayload]
    ) -> dict[str, PublicationClassification]:
        assert Message is not None, "LLM Message dataclass missing"
        payload_map = {payload.identifier: payload for payload in publications}
        author_blocks = []
        for payload in publications:
            authors = ", ".join(payload.authors) or "Unknown"
            genres = ", ".join(payload.genres) or "Unspecified"
            description = (payload.description or "")[:220] or "No description"
            author_blocks.append(
                "\n".join(
                    [
                        f"ID: {payload.identifier}",
                        f"Title: {payload.title}",
                        f"Authors: {authors}",
                        f"Genres: {genres}",
                        f"Description: {description}",
                    ]
                )
            )

        schema = (
            "Return JSON array where each object has keys 'id', 'categories' "
            "(list of {'label': str, 'score': float}) and 'tasteProfile' "
            "(with the allowed values described earlier)."
        )
        prompt = (
            f"You will receive {len(publications)} books. {schema}"
            " Use only the canonical keys and reply with JSON.\n\n"
            + "\n\n".join(author_blocks)
        )
        max_tokens = min(1500, 260 + len(publications) * 140)
        messages = [
            Message(
                role="system",
                content=(
                    "You are a book taxonomy expert helping a reading preference "
                    "survey. Always reply with valid JSON."
                ),
            ),
            Message(role="user", content=prompt),
        ]
        raw = self.llm_client.generate(
            messages, temperature=0.2, max_tokens=max_tokens
        )
        logger.debug(
            "LLM response (batch size %s): %s",
            len(publications),
            raw,
        )
        snippet = self._extract_json(raw)
        if not snippet:
            raise ValueError("Batch LLM response did not contain JSON")

        payload = json.loads(snippet)
        if isinstance(payload, dict):
            payload_items = [payload]
        elif isinstance(payload, list):
            payload_items = payload
        else:
            raise ValueError("Unexpected batch payload structure")

        classifications: dict[str, PublicationClassification] = {}
        for entry in payload_items:
            if not isinstance(entry, dict):
                continue
            identifier = str(
                entry.get("id")
                or entry.get("identifier")
                or entry.get("book_id")
                or ""
            ).strip()
            if identifier not in payload_map:
                continue
            classification = self._parse_llm_response(
                json.dumps(entry), payload_map[identifier]
            )
            if classification is None:
                classification = self._heuristic_classification(
                    payload_map[identifier]
                )
            else:
                classification.ensure_defaults()
            classifications[identifier] = classification

        for payload in publications:
            if payload.identifier not in classifications:
                classifications[payload.identifier] = (
                    self._heuristic_classification(payload)
                )

        return classifications

    def _build_prompt(self, publication: PublicationPayload) -> str:
        author_str = ", ".join(publication.authors) or "Unknown"
        genre_str = ", ".join(publication.genres) or "Unspecified"
        schema = (
            "Return JSON with keys 'categories' and 'tasteProfile'. "
            "'categories' is a list (max 3) of objects with 'label' "
            "and 'score' between 0 and 1. "
            "'tasteProfile' must include:\n"
            f"- genres: up to 3 values chosen from {', '.join(BOOK_GENRE_KEYS)}\n"
            f"- moods: up to 3 values chosen from {', '.join(BOOK_MOOD_KEYS)}\n"
            f"- length: one of {', '.join(BOOK_LENGTH_KEYS)}\n"
            f"- purposes: up to 3 values chosen from {', '.join(READING_PURPOSE_KEYS)}\n"
            "Respond with JSON only."
        )
        return (
            f"{schema}\n"
            f"Title: {publication.title}\n"
            f"Authors: {author_str}\n"
            f"Genres: {genre_str}\n"
            f"Description: {publication.description[:1200]}\n"
        )

    def _parse_llm_response(
        self, raw: str, publication: PublicationPayload
    ) -> PublicationClassification | None:
        snippet = self._extract_json(raw)
        if not snippet:
            return None
        try:
            payload = json.loads(snippet)
        except json.JSONDecodeError:
            return None

        if isinstance(payload, list):
            categories = self._normalise_category_scores(payload)
            taste = self._heuristic_taste_profile(publication)
            return PublicationClassification(categories, taste)

        if isinstance(payload, dict):
            categories_raw = (
                payload.get("categories")
                or payload.get("categoryScores")
                or payload.get("scores")
                or payload.get("labels")
            )
            taste_raw = (
                payload.get("tasteProfile") or payload.get("taste") or {}
            )
            categories = self._normalise_category_scores(categories_raw)
            taste = self._normalise_taste_profile(taste_raw)
            if not categories:
                categories = self._heuristic_category_scores(publication)
            if not taste:
                taste = self._heuristic_taste_profile(publication)
            return PublicationClassification(categories, taste)

        return None

    @staticmethod
    def _extract_json(raw: str) -> str | None:
        snippet = raw.strip()
        if snippet.startswith("{") or snippet.startswith("["):
            return snippet
        match = re.search(r"(\{.*\}|\[\s*\{.*\}\s*\])", raw, re.DOTALL)
        return match.group(1) if match else None

    # ------------------------------------------------------------------
    # Heuristic fallback
    # ------------------------------------------------------------------

    def _heuristic_classification(
        self, publication: PublicationPayload
    ) -> PublicationClassification:
        categories = self._heuristic_category_scores(publication)
        taste = self._heuristic_taste_profile(publication)
        classification = PublicationClassification(categories, taste)
        classification.ensure_defaults()
        return classification

    def _heuristic_category_scores(
        self, publication: PublicationPayload
    ) -> list[dict[str, float]]:
        haystack = self._haystack(publication)
        matches: list[dict[str, float]] = []
        for label, keywords in self.KEYWORD_MAP.items():
            keyword_hits = sum(
                haystack.count(keyword.lower()) for keyword in keywords
            )
            genre_bonus = sum(
                1
                for genre in publication.genres
                if keyword_present(genre, keywords)
            )
            score_raw = keyword_hits + genre_bonus
            if score_raw == 0:
                continue
            matches.append(
                {"label": label, "score": self._clamp(0.35 + score_raw * 0.12)}
            )

        if not matches:
            matches.append({"label": "General Interest", "score": 0.45})

        matches.sort(key=lambda item: item["score"], reverse=True)
        return matches[:3]

    def _heuristic_taste_profile(
        self, publication: PublicationPayload
    ) -> dict[str, object]:
        haystack = self._haystack(publication)
        genres = self._top_matches(haystack, GENRE_KEYWORDS, top_n=3)
        moods = self._top_matches(haystack, MOOD_KEYWORDS, top_n=3)
        purposes = self._top_matches(haystack, PURPOSE_KEYWORDS, top_n=3)
        length = self._detect_length(haystack)

        if not genres:
            genres = [str(BookGenre.NOVEL)]
        if not moods:
            moods = [str(BookMood.SERIOUS)]
        if not purposes:
            purposes = [str(ReadingPurpose.INSPIRATION)]

        return {
            "genres": genres,
            "moods": moods,
            "purposes": purposes,
            "length": length,
        }

    def _top_matches(
        self,
        haystack: str,
        keyword_map: dict[str, tuple[str, ...]],
        *,
        top_n: int,
    ) -> list[str]:
        matches: list[tuple[str, int]] = []
        for label, keywords in keyword_map.items():
            hits = sum(haystack.count(keyword.lower()) for keyword in keywords)
            if hits:
                matches.append((label, hits))
        matches.sort(key=lambda item: item[1], reverse=True)
        return [label for label, _ in matches[:top_n]]

    def _detect_length(self, haystack: str) -> str:
        for length, keywords in LENGTH_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return length
        return str(BookLength.MEDIUM)

    def _haystack(self, publication: PublicationPayload) -> str:
        return " ".join(
            [
                publication.title,
                publication.description,
                " ".join(publication.genres),
            ]
        ).lower()

    # ------------------------------------------------------------------
    # Normalisation helpers
    # ------------------------------------------------------------------

    def _normalise_category_scores(
        self, payload: Any
    ) -> list[dict[str, float]]:
        if not isinstance(payload, list):
            return []
        results: list[dict[str, float]] = []
        for entry in payload:
            if not isinstance(entry, dict):
                continue
            label = str(
                entry.get("label")
                or entry.get("category")
                or entry.get("name")
                or ""
            ).strip()
            if not label:
                continue
            score = entry.get("score") or entry.get("confidence") or 0.0
            try:
                score_val = float(score)
            except (TypeError, ValueError):
                score_val = 0.0
            results.append({"label": label, "score": self._clamp(score_val)})
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:3]

    def _normalise_taste_profile(self, payload: Any) -> dict[str, object]:
        if not isinstance(payload, dict):
            return {}
        genres = self._normalise_multi_choice(
            payload.get("genres"), BOOK_GENRE_KEYS
        )
        moods = self._normalise_multi_choice(
            payload.get("moods"), BOOK_MOOD_KEYS
        )
        purposes = self._normalise_multi_choice(
            payload.get("purposes"), READING_PURPOSE_KEYS
        )
        length = self._normalise_choice(
            payload.get("length") or payload.get("bookLength"),
            BOOK_LENGTH_KEYS,
        )
        taste: dict[str, object] = {}
        if genres:
            taste["genres"] = genres
        if moods:
            taste["moods"] = moods
        if purposes:
            taste["purposes"] = purposes
        if length:
            taste["length"] = length
        return taste

    def _normalise_multi_choice(
        self, values: Any, allowed: Sequence[str]
    ) -> list[str]:
        if values is None:
            return []
        if isinstance(values, str):
            candidates = re.split(r"[,\|]", values)
        elif isinstance(values, Iterable):
            candidates = list(values)
        else:
            return []
        normalised: list[str] = []
        for candidate in candidates:
            choice = self._normalise_choice(candidate, allowed)
            if choice and choice not in normalised:
                normalised.append(choice)
        return normalised

    def _normalise_choice(
        self, value: Any, allowed: Sequence[str]
    ) -> str | None:
        if value is None:
            return None
        target = self._canonicalise(str(value))
        for option in allowed:
            if target == self._canonicalise(option):
                return str(option)
        return None

    @staticmethod
    def _canonicalise(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", text.lower())

    @staticmethod
    def _clamp(value: float) -> float:
        if value < 0:
            return 0.0
        if value > 1:
            return 1.0
        return round(value, 3)


def keyword_present(genre: str, keywords: Iterable[str]) -> bool:
    """Return True if any keyword fragment is present within the genre string."""
    lower = genre.lower()
    return any(keyword.lower() in lower for keyword in keywords)
