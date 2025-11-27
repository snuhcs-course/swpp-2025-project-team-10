"""CLI walkthrough for the RF + LLM hybrid barter workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import typer
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv(ROOT / ".env", override=False)

from models.random_forest import BookFeature, ResponderTaste, compute_feature_vector
from pipeline.hybrid_exchange import (
    ExchangeScenario,
    HybridExchangePipeline,
    ParticipantProfile,
)

app = typer.Typer(add_completion=False)

default_payload: Dict[str, Any] = {
    "requester": {
        "id": "user-a",
        "name": "Alice",
        "preferred_genres": ["NOVEL"],
        "preferred_moods": ["IMMERSIVE"],
        "reading_purposes": ["ESCAPISM"],
    },
    "responder": {
        "id": "user-b",
        "name": "Bob",
        "preferred_genres": ["SCIENCE_TECH", "NOVEL"],
        "preferred_moods": ["IMMERSIVE", "SERIOUS"],
        "reading_purposes": ["INSPIRATION", "STUDY"],
    },
    "requester_books": [
        {
            "id": "bk-001",
            "title": "Project Hail Mary",
            "genres": ["SCIENCE_TECH"],
            "moods": ["IMMERSIVE"],
            "popularity": 0.95,
            "condition_score": 0.9,
        },
        {
            "id": "bk-002",
            "title": "파친코",
            "genres": ["HISTORY_PHILOSOPHY"],
            "moods": ["SERIOUS"],
            "popularity": 0.82,
            "condition_score": 0.75,
        },
        {
            "id": "bk-003",
            "title": "The Midnight Library",
            "genres": ["NOVEL"],
            "moods": ["WARM", "CALM"],
            "popularity": 0.78,
            "condition_score": 0.8,
        },
        {
            "id": "bk-004",
            "title": "달러구트 꿈 백화점",
            "genres": ["NOVEL"],
            "moods": ["WARM"],
            "popularity": 0.7,
            "condition_score": 0.85,
        },
    ],
    "initial_message": "안녕하세요! 제 책들 중에 마음에 드는 것이 있을까요?",
}


def load_payload(payload_path: Path | None) -> Dict[str, Any]:
    if payload_path is None:
        return default_payload
    if not payload_path.exists():
        raise typer.BadParameter(f"Payload file {payload_path} does not exist")
    return json.loads(payload_path.read_text(encoding="utf-8"))


def to_profile(data: Dict[str, Any]) -> ParticipantProfile:
    return ParticipantProfile(
        user_id=str(data.get("id")),
        name=data.get("name", "Unknown"),
        preferred_genres=data.get("preferred_genres", []),
        preferred_moods=data.get("preferred_moods", []),
        reading_purposes=data.get("reading_purposes", []),
    )


def to_books(entries: List[Dict[str, Any]]) -> List[BookFeature]:
    books: List[BookFeature] = []
    for entry in entries:
        books.append(
            BookFeature(
                book_id=str(entry.get("id")),
                title=entry.get("title", "Unknown"),
                genres=entry.get("genres", []),
                moods=entry.get("moods", []),
                popularity=float(entry.get("popularity", 0.5)),
                condition_score=float(entry.get("condition_score", 0.8)),
            )
        )
    return books


def summarize_rf_step(scenario: ExchangeScenario, *, top_k: int, pipeline: HybridExchangePipeline) -> None:
    taste = ResponderTaste(
        preferred_genres=scenario.responder.preferred_genres,
        preferred_moods=scenario.responder.preferred_moods,
        reading_purposes=scenario.responder.reading_purposes,
    )
    typer.echo("\n[Step 1] RF Feature Extraction 🚀")
    for book in scenario.requester_books:
        features = compute_feature_vector(book, taste)
        typer.echo(
            f"  - {book.title}: genre_overlap={features[0]:.2f}, mood_overlap={features[1]:.2f}, "
            f"popularity={features[2]:.2f}, condition={features[3]:.2f}"
        )

    ranked = pipeline.ranker.rank_books(scenario.requester_books, taste, top_k=top_k)
    typer.echo("\n[Step 2] RF Ranking Results 🧮")
    for idx, entry in enumerate(ranked, start=1):
        typer.echo(f"  {idx}. {entry.book.title} — predicted acceptance {entry.score:.3f}")
    return ranked


def summarize_llm_step(pipeline: HybridExchangePipeline, scenario: ExchangeScenario, *, top_k: int) -> None:
    typer.echo("\n[Step 3] LLM Counter Proposal ✉️")
    proposal = pipeline.generate_counter_proposal(scenario, top_k=top_k)
    typer.echo("AI DM to requester:\n" + proposal.message + "\n")

    typer.echo("[Step 4] Two-LLM Reasoning 🧠🗣️")
    reasoned = pipeline.generate_reasoned_counter_proposal(scenario, top_k=top_k)
    if reasoned.reasoning.recommendations:
        typer.echo("Multi-book picks with reasons:")
        for rec in reasoned.reasoning.recommendations:
            score = f"{rec.score:.2f}" if rec.score is not None else "n/a"
            typer.echo(f"  - {rec.title} (score={score}) → {rec.reason}")
        typer.echo("")
    typer.echo("Conversation:")
    for turn in reasoned.reasoning.conversation:
        typer.echo(f"  [{turn.speaker.upper()}] {turn.message}")
    typer.echo("\nFinal joint recommendation: " + reasoned.reasoning.final_recommendation)
    typer.echo(f"Confidence: {reasoned.reasoning.confidence_score:.2f}\n")


@app.command()
def run(
    payload_file: Path = typer.Option(
        None,
        "--payload",
        "-p",
        help="Path to a JSON payload mirroring the backend request format.",
    ),
    top_k: int = typer.Option(4, min=1, max=5, help="How many books to rank."),
):
    """Walk through the exchange workflow end-to-end."""
    payload = load_payload(payload_file)
    scenario = ExchangeScenario(
        requester=to_profile(payload["requester"]),
        responder=to_profile(payload["responder"]),
        requester_books=to_books(payload["requester_books"]),
        initial_message=payload.get("initial_message", ""),
        context_note=payload.get("context_note", ""),
    )
    typer.echo("=== Hybrid Exchange Demo ===")
    typer.echo(
        f"Requester A: {scenario.requester.name}\nResponder B: {scenario.responder.name}\n"
        f"Initial message: {scenario.initial_message}\n"
    )
    pipeline = HybridExchangePipeline()
    summarize_rf_step(scenario, top_k=top_k, pipeline=pipeline)
    summarize_llm_step(pipeline, scenario, top_k=top_k)


if __name__ == "__main__":
    app()
