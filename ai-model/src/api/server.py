"""FastAPI server exposing the hybrid RF + LLM counter-proposal pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Sequence

from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from data.entities import Item, UserProfile
from llm.reasoning import ReasoningGenerator
from models.random_forest import BookFeature
from pipeline.hybrid_exchange import (
    CounterProposal,
    ExchangeScenario,
    HybridExchangePipeline,
    ParticipantProfile,
    ReasonedProposal,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

app = FastAPI(title="Hybrid Exchange API", version="0.1.0")
pipeline = HybridExchangePipeline()
reasoning_generator = ReasoningGenerator()


class BookPayload(BaseModel):
    id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    moods: List[str] = Field(default_factory=list)
    popularity: float = 0.5
    condition_score: float = Field(default=0.8, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserPayload(BaseModel):
    user_id: str = Field(..., alias="id")
    name: str
    preferred_genres: List[str] = Field(default_factory=list)
    preferred_moods: List[str] = Field(default_factory=list)
    reading_purposes: List[str] = Field(default_factory=list)
    favorite_authors: List[str] = Field(default_factory=list)
    favorite_books: List[str] = Field(default_factory=list)

    def to_profile(self) -> ParticipantProfile:
        return ParticipantProfile(
            user_id=self.user_id,
            name=self.name,
            preferred_genres=self.preferred_genres,
            preferred_moods=self.preferred_moods,
            reading_purposes=self.reading_purposes,
        )


class ExchangeRequestPayload(BaseModel):
    requester: UserPayload
    responder: UserPayload
    requester_books: List[BookPayload]
    initial_message: str = ""
    context_note: str = ""
    top_k: int = Field(3, ge=1, le=5)


class RankedBookPayload(BaseModel):
    id: str
    title: str
    score: float
    genres: List[str]
    moods: List[str]
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendedBookPayload(BaseModel):
    id: str
    title: str
    reason: str
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CounterProposalResponse(BaseModel):
    ranked_books: List[RankedBookPayload]
    message: str


class ConversationTurnPayload(BaseModel):
    speaker: str
    message: str
    reasoning: str | None = None


class ReasoningPayload(BaseModel):
    recommended_books: List[str]
    recommendations: List[RecommendedBookPayload]
    conversation: List[ConversationTurnPayload]
    final_recommendation: str
    confidence_score: float


class ReasonedProposalResponse(CounterProposalResponse):
    reasoning: ReasoningPayload


class BookRecommendationRequest(BaseModel):
    user: UserPayload
    candidate_books: List[BookPayload]
    reading_history: List[str] = Field(default_factory=list)
    max_results: int = Field(3, ge=1, le=5)


class BookRecommendationResponse(BaseModel):
    recommendations: List[RecommendedBookPayload]
    reasoning: ReasoningPayload


def _build_scenario(payload: ExchangeRequestPayload) -> ExchangeScenario:
    requester_books: Sequence[BookFeature] = [
        BookFeature(
            book_id=book.id,
            title=book.title,
            genres=book.genres,
            moods=book.moods,
            popularity=book.popularity,
            condition_score=book.condition_score,
        )
        for book in payload.requester_books
    ]
    return ExchangeScenario(
        requester=payload.requester.to_profile(),
        responder=payload.responder.to_profile(),
        requester_books=requester_books,
        initial_message=payload.initial_message,
        context_note=payload.context_note,
    )


def _to_reasoning_profile(payload: UserPayload) -> UserProfile:
    """Map request user payload to ReasoningGenerator profile."""
    preferences = {
        "genres": payload.preferred_genres,
        "moods": payload.preferred_moods,
        "purposes": payload.reading_purposes,
    }
    if payload.favorite_authors:
        preferences["authors"] = payload.favorite_authors
    return UserProfile(
        user_id=payload.user_id,
        display_name=payload.name,
        trust_score=0.8,
        reliability=0.8,
        preferences=preferences,
    )


def _to_reasoning_items(
    user: UserPayload, books: list[BookPayload]
) -> list[Item]:
    """Convert book payloads into Items understood by the LLM layer."""
    items: list[Item] = []
    for book in books:
        facets = {}
        if book.genres:
            facets["genre"] = book.genres[0]
        if book.moods:
            facets["mood"] = book.moods[0]
        metadata = {
            "genres": book.genres,
            "moods": book.moods,
            "authors": book.authors,
            **(book.metadata or {}),
        }
        items.append(
            Item(
                item_id=book.id,
                owner_id=user.user_id,
                title=book.title,
                valuation=book.popularity,
                facets=facets,
                metadata=metadata,
            )
        )
    return items


def _to_response(
    proposal: CounterProposal, reason_lookup: dict[str, str] | None = None
) -> CounterProposalResponse:
    reason_lookup = reason_lookup or {}
    ranked_payload = [
        RankedBookPayload(
            id=entry.book.book_id,
            title=entry.book.title,
            score=entry.score,
            genres=list(entry.book.genres),
            moods=list(entry.book.moods),
            reason=reason_lookup.get(entry.book.book_id),
            metadata={
                "popularity": entry.book.popularity,
                "condition_score": entry.book.condition_score,
            },
        )
        for entry in proposal.ranked_books
    ]
    return CounterProposalResponse(
        ranked_books=ranked_payload, message=proposal.message
    )


@app.post("/api/exchange/counter-proposal", response_model=CounterProposalResponse)
def generate_counter_proposal(payload: ExchangeRequestPayload):
    """Implements step (3) in the barter flow with RF + LLM."""
    scenario = _build_scenario(payload)
    proposal = pipeline.generate_counter_proposal(
        scenario, top_k=payload.top_k
    )
    return _to_response(proposal)


def _to_reasoned_response(proposal: ReasonedProposal) -> ReasonedProposalResponse:
    reasoning_payload = _build_reasoning_payload(proposal.reasoning)
    reason_lookup = {rec.id: rec.reason for rec in reasoning_payload.recommendations}
    base = _to_response(proposal, reason_lookup)
    return ReasonedProposalResponse(
        ranked_books=base.ranked_books,
        message=base.message,
        reasoning=reasoning_payload,
    )


def _build_reasoning_payload(
    trajectory,
) -> ReasoningPayload:
    recommendations = [
        RecommendedBookPayload(
            id=rec.book_id,
            title=rec.title,
            reason=rec.reason,
            score=rec.score,
            metadata=rec.metadata,
        )
        for rec in trajectory.recommendations
    ]
    conversation = [
        ConversationTurnPayload(
            speaker=turn.speaker,
            message=turn.message,
            reasoning=turn.reasoning,
        )
        for turn in trajectory.conversation
    ]
    return ReasoningPayload(
        recommended_books=trajectory.recommended_books,
        recommendations=recommendations,
        conversation=conversation,
        final_recommendation=trajectory.final_recommendation,
        confidence_score=trajectory.confidence_score,
    )


@app.post(
    "/api/exchange/reasoned-proposal",
    response_model=ReasonedProposalResponse,
)
def generate_reasoned_proposal(payload: ExchangeRequestPayload):
    scenario = _build_scenario(payload)
    proposal = pipeline.generate_reasoned_counter_proposal(
        scenario, top_k=payload.top_k
    )
    return _to_reasoned_response(proposal)


@app.post(
    "/api/recommendations/books",
    response_model=BookRecommendationResponse,
)
def generate_book_recommendations(payload: BookRecommendationRequest):
    """Return multi-book recommendations with per-book reasons."""
    profile = _to_reasoning_profile(payload.user)
    items = _to_reasoning_items(payload.user, payload.candidate_books)
    trajectory = reasoning_generator.generate_book_recommendation_reasoning(
        user_profile=profile,
        candidate_books=items,
        user_reading_history=payload.reading_history,
        max_recommendations=payload.max_results,
    )
    recommendations = [
        RecommendedBookPayload(
            id=rec.book_id,
            title=rec.title,
            reason=rec.reason,
            score=rec.score,
            metadata=rec.metadata,
        )
        for rec in trajectory.recommendations
    ]
    reasoning_payload = _build_reasoning_payload(trajectory)
    return BookRecommendationResponse(
        recommendations=recommendations, reasoning=reasoning_payload
    )


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
