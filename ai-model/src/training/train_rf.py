"""Train the RandomForestBookRanker using bookbarter_db data."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import joblib
import numpy as np
import psycopg
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from models.random_forest import (
    BookFeature,
    ResponderTaste,
    compute_feature_vector,
    DEFAULT_CHECKPOINT,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CANONICAL_GENRES = [
    "NOVEL",
    "ESSAY",
    "SCIENCE_TECH",
    "HUMANITIES_SOCIAL",
    "HISTORY_PHILOSOPHY",
    "ART_LANGUAGE",
    "ECONOMICS_BUSINESS",
]

CANONICAL_MOODS = [
    "WARM",
    "SERIOUS",
    "IMMERSIVE",
    "ENERGETIC",
    "HUMOROUS",
    "MYSTERIOUS",
    "CALM",
]

CANONICAL_PURPOSES = [
    "STUDY",
    "HEALING",
    "ESCAPISM",
    "NEW_PERSPECTIVE",
    "INSPIRATION",
    "CULTURE",
    "LIGHT_READING",
]


def fetch_books(limit: int | None = None) -> list[BookFeature]:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://bookbarter:bookbarter@localhost:5432/bookbarter_db",
    )
    query = """
        SELECT id, title, taste_profile
        FROM books_book_publication
        WHERE taste_profile IS NOT NULL
    """
    if limit:
        query += f" LIMIT {int(limit)}"

    books: list[BookFeature] = []
    with psycopg.connect(database_url) as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        for pk, title, taste_raw in rows:
            if taste_raw is None:
                continue
            if isinstance(taste_raw, str):
                try:
                    taste = json.loads(taste_raw)
                except json.JSONDecodeError:
                    continue
            else:
                taste = taste_raw
            genres = taste.get("genres") or []
            moods = taste.get("moods") or []
            if not genres and not moods:
                continue
            popularity = float(taste.get("popularity", 0.6))
            condition = float(taste.get("condition", 0.8))
            books.append(
                BookFeature(
                    book_id=str(pk),
                    title=title,
                    genres=genres,
                    moods=moods,
                    popularity=popularity,
                    condition_score=condition,
                )
            )
    logger.info("Fetched %s books from Postgres", len(books))
    return books


def synthesize_taste(base: BookFeature, rng: np.random.Generator) -> ResponderTaste:
    def pick(source, count):
        if not source:
            return []
        source = list(dict.fromkeys(source))
        count = min(count, len(source))
        return list(rng.choice(source, size=count, replace=False))

    if base.genres:
        genres = pick(base.genres + CANONICAL_GENRES, 2)
    else:
        genres = pick(CANONICAL_GENRES, 2)
    if base.moods:
        moods = pick(base.moods + CANONICAL_MOODS, 2)
    else:
        moods = pick(CANONICAL_MOODS, 2)
    purposes = pick(CANONICAL_PURPOSES, 2)
    return ResponderTaste(
        preferred_genres=genres,
        preferred_moods=moods,
        reading_purposes=purposes,
    )


def generate_dataset(books: list[BookFeature], samples_per_book: int = 8):
    rng = np.random.default_rng(7)
    features: list[np.ndarray] = []
    labels: list[float] = []
    for book in books:
        for _ in range(samples_per_book):
            taste = synthesize_taste(book, rng)
            feat = compute_feature_vector(book, taste)
            genre_overlap, mood_overlap = feat[0], feat[1]
            purpose_component = 1.0 if taste.reading_purposes else 0.5
            label = (
                0.6 * genre_overlap
                + 0.3 * mood_overlap
                + 0.1 * purpose_component
                + rng.normal(scale=0.05)
            )
            features.append(feat)
            labels.append(label)
    X = np.stack(features)
    y = np.array(labels)
    return X, y


def train_and_save(checkpoint: Path = DEFAULT_CHECKPOINT):
    books = fetch_books()
    if not books:
        raise RuntimeError("No books with taste_profile available for training")
    X, y = generate_dataset(books)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=1337
    )
    model = RandomForestRegressor(n_estimators=400, random_state=21)
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    logger.info("Validation R^2: %.3f", r2_score(y_valid, preds))
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, checkpoint)
    logger.info("Saved checkpoint to %s", checkpoint)


if __name__ == "__main__":
    train_and_save()
