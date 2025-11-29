"""Hybrid pipeline that combines RF ranking with LLM messaging for exchanges."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from data.entities import Item, UserProfile as ReasoningUserProfile
from llm.client import LLMClient, Message
from llm.reasoning import ReasoningGenerator, ReasoningTrajectory

from models.random_forest import (
    BookFeature,
    RandomForestBookRanker,
    RankedBook,
    ResponderTaste,
)


@dataclass
class ParticipantProfile:
    user_id: str
    name: str
    preferred_genres: Sequence[str] = field(default_factory=list)
    preferred_moods: Sequence[str] = field(default_factory=list)
    reading_purposes: Sequence[str] = field(default_factory=list)


@dataclass
class ExchangeScenario:
    requester: ParticipantProfile  # user A initiating request
    responder: ParticipantProfile  # user B receiving and countering
    requester_books: Sequence[BookFeature]
    initial_message: str = ""
    context_note: str = ""


@dataclass
class CounterProposal:
    ranked_books: list[RankedBook]
    message: str


@dataclass
class ReasonedProposal(CounterProposal):
    reasoning: ReasoningTrajectory


class LLMCounterProposalWriter:
    """Generate natural-language counter proposals for step (3) of the flow."""

    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    def compose(
        self,
        scenario: ExchangeScenario,
        ranked_books: Sequence[RankedBook],
    ) -> str:
        if not ranked_books:
            return (
                f"{scenario.responder.name}님, 당장은 교환에 맞는 책을 찾지 못했습니다."
                " 원하는 장르나 분위기를 더 알려주시면 다시 추천드릴게요."
            )

        book_lines = []
        for entry in ranked_books:
            book_lines.append(
                f"- {entry.book.title} (적합도 {entry.score:.2f})"
            )
        book_block = "\n".join(book_lines)

        prompt = (
            "아래는 중고 서적 교환 플랫폼의 DM 대화 상황입니다.\n"
            "사용자 B가 사용자 A의 책을 카운터 제안하려고 합니다."
            "제공된 책 리스트 중에서 한 권을 골라 교환 제안을 작성하세요."
            "시나리오 단계는 다음과 같습니다:\n"
            "1) A가 먼저 교환 요청\n2) B가 요청 확인\n3) B가 AI 추천을 참고하여 카운터 제안\n"
            "4) A가 최종 수락.\n"
            "B의 취향과 톤을 반영하여 자연스럽고 예의 있는 한국어 DM 형식으로 작성하세요."
            "반드시 제안 도중에 교환 이유(장르/무드/목적)를 한두 문장으로 설명하세요."
        )
        user_text = (
            f"요청자 A: {scenario.requester.name}\n"
            f"응답자 B: {scenario.responder.name}\n"
            f"B의 선호 장르: {', '.join(scenario.responder.preferred_genres)}\n"
            f"B의 선호 분위기: {', '.join(scenario.responder.preferred_moods)}\n"
            f"B의 독서 목적: {', '.join(scenario.responder.reading_purposes)}\n"
            f"추천 후보:\n{book_block}\n"
            f"초기 메시지: {scenario.initial_message}\n"
        )
        messages = [
            Message(role="system", content=prompt),
            Message(role="user", content=user_text),
        ]
        response = self.client.generate(messages, temperature=0.4, max_tokens=350)
        return response.strip()


class HybridExchangePipeline:
    """Coordinates RF ranking and LLM messaging for barter counter proposals."""

    def __init__(
        self,
        *,
        ranker: RandomForestBookRanker | None = None,
        llm_writer: LLMCounterProposalWriter | None = None,
        reasoning_generator: ReasoningGenerator | None = None,
    ) -> None:
        self.ranker = ranker or RandomForestBookRanker()
        self.writer = llm_writer or LLMCounterProposalWriter()
        self.reasoning = reasoning_generator or ReasoningGenerator()

    def generate_counter_proposal(
        self,
        scenario: ExchangeScenario,
        *,
        top_k: int = 3,
    ) -> CounterProposal:
        taste = ResponderTaste(
            preferred_genres=scenario.responder.preferred_genres,
            preferred_moods=scenario.responder.preferred_moods,
            reading_purposes=scenario.responder.reading_purposes,
        )
        ranked = self.ranker.rank_books(
            scenario.requester_books, taste, top_k=top_k
        )
        message = self.writer.compose(scenario, ranked)
        return CounterProposal(ranked_books=ranked, message=message)

    def generate_reasoned_counter_proposal(
        self,
        scenario: ExchangeScenario,
        *,
        top_k: int = 5,
        reasoning_count: int = 3,
    ) -> ReasonedProposal:
        base = self.generate_counter_proposal(scenario, top_k=top_k)
        reasoning = self._build_reasoning(
            scenario, base.ranked_books, reasoning_count
        )
        return ReasonedProposal(
            ranked_books=base.ranked_books,
            message=base.message,
            reasoning=reasoning,
        )

    def _build_reasoning(
        self,
        scenario: ExchangeScenario,
        ranked: Sequence[RankedBook],
        reasoning_count: int,
    ) -> ReasoningTrajectory:
        if not ranked:
            empty_profile = ReasoningUserProfile(
                user_id=scenario.responder.user_id,
                display_name=scenario.responder.name,
                trust_score=0.7,
                reliability=0.7,
                preferences={},
            )
            return self.reasoning.generate_book_recommendation_reasoning(
                empty_profile, [], None
            )

        subset = list(ranked[: reasoning_count or len(ranked)])
        user_profile = ReasoningUserProfile(
            user_id=scenario.responder.user_id,
            display_name=scenario.responder.name,
            trust_score=0.8,
            reliability=0.85,
            preferences={
                "genres": scenario.responder.preferred_genres,
                "moods": scenario.responder.preferred_moods,
                "purposes": scenario.responder.reading_purposes,
            },
        )
        items = [
            self._to_reasoning_item(entry, scenario.requester.user_id)
            for entry in subset
        ]
        return self.reasoning.generate_book_recommendation_reasoning(
            user_profile=user_profile,
            candidate_books=items,
            user_reading_history=None,
            max_recommendations=len(subset),
        )

    @staticmethod
    def _to_reasoning_item(
        entry: RankedBook, requester_id: str
    ) -> Item:
        facets = {}
        if entry.book.genres:
            facets["genre"] = entry.book.genres[0]
        if entry.book.moods:
            facets["mood"] = entry.book.moods[0]
        metadata = {
            "score": entry.score,
            "genres": entry.book.genres,
            "moods": entry.book.moods,
        }
        return Item(
            item_id=entry.book.book_id,
            owner_id=requester_id,
            title=entry.book.title,
            valuation=entry.score,
            facets=facets,
            metadata=metadata,
        )

    @staticmethod
    def to_book_feature(payload: dict) -> BookFeature:
        return BookFeature(
            book_id=str(payload.get("id")),
            title=payload.get("title", "Unknown"),
            genres=payload.get("genres", []),
            moods=payload.get("moods", []),
            popularity=float(payload.get("popularity", 0.5)),
            condition_score=float(payload.get("condition_score", 0.8)),
        )
