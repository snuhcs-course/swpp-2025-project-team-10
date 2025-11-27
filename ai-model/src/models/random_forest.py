"""Lightweight Random Forest ranker used for barter recommendations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)

DEFAULT_CHECKPOINT = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "checkpoints"
    / "rf_ranker.pkl"
)


@dataclass
class BookFeature:
    """Minimal book descriptor consumed by the Random Forest ranker."""

    book_id: str
    title: str
    genres: Sequence[str]
    moods: Sequence[str]
    popularity: float = 0.5
    condition_score: float = 0.8


@dataclass
class ResponderTaste:
    """Profile for the responder (user B) in the barter scenario."""

    preferred_genres: Sequence[str]
    preferred_moods: Sequence[str]
    reading_purposes: Sequence[str]


@dataclass
class RankedBook:
    book: BookFeature
    score: float


def compute_feature_vector(
    book: BookFeature, taste: ResponderTaste
) -> np.ndarray:
    genre_overlap = _overlap_ratio(book.genres, taste.preferred_genres)
    mood_overlap = _overlap_ratio(book.moods, taste.preferred_moods)
    purpose_bonus = 1.0 if taste.reading_purposes else 0.5
    return np.array(
        [genre_overlap, mood_overlap, book.popularity, book.condition_score],
        dtype=np.float32,
    ) * np.array([1.0, 1.0, purpose_bonus, 1.0], dtype=np.float32)


class RandomForestBookRanker:
    """Ranks owner's books by predicting responder acceptance probability."""

    def __init__(
        self,
        model: RandomForestRegressor | None = None,
        *,
        checkpoint: str | Path | None = DEFAULT_CHECKPOINT,
    ) -> None:
        if model is not None:
            self.model = model
        else:
            self.model = self._load_or_train(checkpoint)

    def _load_or_train(self, checkpoint: str | Path | None) -> RandomForestRegressor:
        if checkpoint:
            path = Path(checkpoint)
            if path.exists():
                logger.info("Loading RF checkpoint from %s", path)
                return joblib.load(path)
        logger.warning("RF checkpoint missing – training fallback model")
        model = self._train_default_model()
        if checkpoint:
            path = Path(checkpoint)
            path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, path)
            logger.info("Saved fallback RF checkpoint to %s", path)
        return model

    def _train_default_model(self) -> RandomForestRegressor:
        rng = np.random.default_rng(42)
        X = rng.random((512, 4))
        weights = np.array([0.45, 0.3, 0.15, 0.1])
        y = X.dot(weights) + rng.normal(scale=0.03, size=512)
        model = RandomForestRegressor(n_estimators=200, random_state=13)
        model.fit(X, y)
        return model

    def rank_books(
        self,
        books: Iterable[BookFeature],
        taste: ResponderTaste,
        *,
        top_k: int = 3,
    ) -> list[RankedBook]:
        ranked: list[RankedBook] = []
        for book in books:
            features = compute_feature_vector(book, taste)
            prediction = float(self.model.predict(features.reshape(1, -1))[0])
            ranked.append(RankedBook(book=book, score=prediction))
        ranked.sort(key=lambda entry: entry.score, reverse=True)
        return ranked[:top_k]


def _overlap_ratio(source: Sequence[str], preferred: Sequence[str]) -> float:
    if not source or not preferred:
        return 0.0
    src = {value.lower() for value in source}
    pref = {value.lower() for value in preferred}
    return len(src & pref) / max(len(src), 1)
