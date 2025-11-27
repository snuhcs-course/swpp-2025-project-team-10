"""Reasoning trajectory generation using two-LLM conversation."""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Iterable

from data.entities import Item, UserProfile
from llm.client import ConversationTurn, LLMClient
from llm.config import LLMConfig

logger = logging.getLogger(__name__)


@dataclass
class BookRecommendation:
    """Lightweight view of a recommended book with a reason."""

    book_id: str
    title: str
    reason: str
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.book_id,
            "title": self.title,
            "reason": self.reason,
            "score": self.score,
            "metadata": self.metadata,
        }


@dataclass
class ReasoningTrajectory:
    """
    A reasoning trajectory showing the conversation between two LLMs.

    This represents a dialogue between a recommender LLM and a critic LLM,
    simulating a thoughtful discussion about book recommendations.
    """

    user_id: str
    recommended_books: list[str] = field(default_factory=list)  # Book titles
    conversation: list[ConversationTurn] = field(default_factory=list)
    final_recommendation: str = ""
    confidence_score: float = 0.0
    recommendations: list[BookRecommendation] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.recommended_books and self.recommendations:
            self.recommended_books = [rec.title for rec in self.recommendations]
        if not self.recommendations and self.recommended_books:
            self.recommendations = [
                BookRecommendation(book_id=title, title=title, reason="")
                for title in self.recommended_books
            ]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "recommended_books": self.recommended_books,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "conversation": [
                {
                    "speaker": turn.speaker,
                    "message": turn.message,
                    "reasoning": turn.reasoning,
                }
                for turn in self.conversation
            ],
            "final_recommendation": self.final_recommendation,
            "confidence_score": self.confidence_score,
        }


class ReasoningGenerator:
    """
    Generate reasoning trajectories using two-LLM conversation.

    This class orchestrates a conversation between two LLM agents:
    1. Recommender: Proposes book recommendations based on user data
    2. Critic: Questions and validates the recommendations

    The conversation format makes the reasoning transparent and
    engaging for users.
    """

    def __init__(self, config: LLMConfig | None = None):
        """Initialize reasoning generator."""
        self.config = config or LLMConfig.from_env()
        self.recommender_client = LLMClient(self.config)
        self.critic_client = LLMClient(self.config)

        # Load system prompts from environment or use defaults (Korean, DM-style)
        self.recommender_prompt = os.getenv(
            "REASONING_SYSTEM_PROMPT_RECOMMENDER",
            "당신은 책 추천 전문가입니다. "
            "지금 당신은 책 비평가와 인스타그램 DM으로 대화하고 있습니다. "
            "상대방은 AI가 아니라 실제 사람입니다. "
            "책을 추천할 때는 책 제목과 함께 1-2가지 이유를 간단히 설명하세요. "
            "친근하고 자연스럽게 대화하되, 각 메시지는 2-3문장으로 작성하세요. "
            "반말을 사용하세요.\n\n"
            "예시:\n"
            "용의자 X의 헌신 추천해! 히가시노 게이고 작품이라 백야행 좋아했으면 딱일 거야. "
            "반전도 엄청나고 추리 과정이 정말 재밌거든.",
        )

        self.critic_prompt = os.getenv(
            "REASONING_SYSTEM_PROMPT_CRITIC",
            "당신은 책 비평가입니다. "
            "지금 당신은 책 추천 전문가와 인스타그램 DM으로 대화하고 있습니다. "
            "상대방은 AI가 아니라 실제 사람입니다. "
            "추천받은 책에 대해 질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요. "
            "친근하고 자연스럽게 대화하되, 각 메시지는 2-3문장으로 작성하세요. "
            "반말을 사용하세요.\n\n"
            "예시:\n"
            "좋긴 한데, 다른 작가 작품도 고려해봤어? 김영하 작품도 좋을 것 같은데.",
        )

        self.max_turns = int(os.getenv("REASONING_MAX_TURNS", "5"))
        self.recommendation_count = int(os.getenv("RECOMMENDATION_COUNT", "3"))

    def generate_book_recommendation_reasoning(
        self,
        user_profile: UserProfile,
        candidate_books: list[Item],
        user_reading_history: list[str] | None = None,
        max_recommendations: int | None = None,
    ) -> ReasoningTrajectory:
        """
        Generate reasoning trajectory for book recommendations.

        Args:
            user_profile: User's profile with preferences
            candidate_books: List of candidate books to recommend
            user_reading_history: Optional reading history
            max_recommendations: Optional override for how many books to return

        Returns:
            ReasoningTrajectory with conversation and final recommendation
        """
        limit = max_recommendations or self.recommendation_count

        # Prepare context for LLMs
        context = self._prepare_context(
            user_profile, candidate_books, user_reading_history
        )

        # Initialize conversation
        conversation: list[ConversationTurn] = []

        # Turn 1: Recommender proposes initial recommendations
        recommender_msg = self._recommender_initial_proposal(context)
        conversation.append(
            ConversationTurn(
                speaker="recommender",
                message=recommender_msg,
                reasoning="Initial analysis of user preferences",
            )
        )

        # Turn 2: Critic questions the recommendations
        critic_msg = self._critic_questions(context, recommender_msg)
        conversation.append(
            ConversationTurn(
                speaker="critic",
                message=critic_msg,
                reasoning="Validating recommendation against preferences",
            )
        )

        # Turn 3: Recommender refines based on criticism
        refined_msg = self._recommender_refines(
            context, recommender_msg, critic_msg
        )
        conversation.append(
            ConversationTurn(
                speaker="recommender",
                message=refined_msg,
                reasoning="Refined recommendation addressing concerns",
            )
        )

        # Additional turns if configured
        for turn in range(3, self.max_turns):
            if turn % 2 == 1:  # Critic's turn
                msg = self._critic_followup(context, conversation)
                conversation.append(
                    ConversationTurn(
                        speaker="critic",
                        message=msg,
                        reasoning=f"Follow-up validation (turn {turn})",
                    )
                )
            else:  # Recommender's turn
                msg = self._recommender_followup(context, conversation)
                conversation.append(
                    ConversationTurn(
                        speaker="recommender",
                        message=msg,
                        reasoning=f"Further refinement (turn {turn})",
                    )
                )

        recommendations = self._generate_recommendations_with_reasons(
            user_profile, candidate_books, context, limit
        )

        # Generate final recommendation
        final_rec = self._generate_final_recommendation(
            context, conversation, recommendations
        )

        # Calculate confidence score
        confidence = self._calculate_confidence(conversation, recommendations)

        return ReasoningTrajectory(
            user_id=user_profile.user_id,
            recommended_books=[rec.title for rec in recommendations],
            recommendations=recommendations,
            conversation=conversation,
            final_recommendation=final_rec,
            confidence_score=confidence,
        )

    def _prepare_context(
        self,
        user_profile: UserProfile,
        candidate_books: list[Item],
        reading_history: list[str] | None,
    ) -> str:
        """Prepare context string for LLMs."""
        prefs = user_profile.preferences
        pref_str = ", ".join(f"{k}: {', '.join(v)}" for k, v in prefs.items())

        books_str = "\n".join(
            f"- {book.title} by {book.metadata.get('author', 'Unknown')}"
            for book in candidate_books
        )

        history_str = (
            "\n".join(f"- {book}" for book in reading_history)
            if reading_history
            else "No reading history available"
        )

        return f"""User Profile:
- User ID: {user_profile.user_id}
- Display Name: {user_profile.display_name}
- Preferences: {pref_str}
- Trust Score: {user_profile.trust_score}

Reading History:
{history_str}

Candidate Books:
{books_str}
"""

    def _generate_recommendations_with_reasons(
        self,
        user_profile: UserProfile,
        candidate_books: list[Item],
        context: str,
        limit: int,
    ) -> list[BookRecommendation]:
        """Return top-N recommendations with reasons."""
        if not candidate_books:
            return []

        target_books = list(candidate_books[:limit])
        book_lines = "\n".join(
            self._book_metadata_summary(book) for book in target_books
        )
        prefs = user_profile.preferences or {}
        pref_desc = ", ".join(
            f"{key}={', '.join(vals)}" for key, vals in prefs.items()
        )

        prompt = f"""사용자 정보와 후보 도서를 보고 교환/추천용 리스트를 만들어.
최대 {limit}권까지 추천하고, 각 책마다 한두 문장으로 '왜 이 책이 맞는지'를 설명해.
JSON 배열로만 답해. 형식:
[
  {{"book_id": "id", "title": "제목", "reason": "짧은 한국어 설명", "score": 0.0}}
]
score는 0~1 사이 적합도 추정값이야.

사용자 취향: {pref_desc or '제공된 취향 없음'}
대화 요약 컨텍스트:
{context}

후보 도서:
{book_lines}
"""
        try:
            response = self.recommender_client.chat(
                self.recommender_prompt, prompt, temperature=0.4
            )
            parsed = self._parse_recommendation_response(
                response, target_books, limit
            )
            if parsed:
                return parsed
            logger.info("LLM returned no parsable recommendations, using fallback.")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to generate reasons with LLM: %s", exc)

        return self._fallback_recommendations(user_profile, target_books)

    def _parse_recommendation_response(
        self, raw: str, candidates: Iterable[Item], limit: int
    ) -> list[BookRecommendation]:
        """Parse LLM JSON output into BookRecommendation objects."""
        try:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            payload = raw[start:end] if start != -1 and end != 0 else raw
            data = json.loads(payload)
        except Exception:
            logger.debug("Could not parse recommendation JSON payload: %s", raw)
            return []

        by_id = {book.item_id: book for book in candidates}
        by_title = {book.title: book for book in candidates}
        recommendations: list[BookRecommendation] = []

        for entry in data:
            book_id = (
                str(entry.get("book_id"))
                if entry.get("book_id") is not None
                else str(entry.get("id"))
            )
            title = entry.get("title") or book_id
            book = by_id.get(book_id) or by_title.get(title)

            if book:
                book_id = book.item_id
                title = book.title

            raw_score = entry.get("score")
            score = None
            if raw_score is not None:
                try:
                    score = float(raw_score)
                except (TypeError, ValueError):
                    score = None

            reason = entry.get("reason") or "사용자 취향과 잘 맞는 책이에요."
            metadata = book.metadata if book else {}

            recommendations.append(
                BookRecommendation(
                    book_id=book_id,
                    title=title,
                    reason=reason,
                    score=score,
                    metadata=metadata,
                )
            )
            if len(recommendations) >= limit:
                break

        return recommendations

    def _fallback_recommendations(
        self, user_profile: UserProfile, candidates: Iterable[Item]
    ) -> list[BookRecommendation]:
        """Deterministic fallback when the LLM cannot return JSON."""
        recommendations: list[BookRecommendation] = []
        pref = user_profile.preferences or {}

        def _match(values: Iterable[str] | None, preferred: Iterable[str] | None):
            if not values or not preferred:
                return set()
            return {v for v in values if v in preferred}

        for book in candidates:
            if book.metadata.get("genres"):
                genres = book.metadata.get("genres", [])
            elif book.facets.get("genre"):
                genres = [book.facets["genre"]]
            else:
                genres = []

            if book.metadata.get("moods"):
                moods = book.metadata.get("moods", [])
            elif book.facets.get("mood"):
                moods = [book.facets["mood"]]
            else:
                moods = []

            authors = (
                [book.metadata.get("author")]
                if book.metadata.get("author")
                else []
            )

            reasons = []
            matched_genres = _match(genres, pref.get("genres"))
            if matched_genres:
                reasons.append(f"{', '.join(matched_genres)} 장르를 좋아해서 잘 맞아")

            matched_moods = _match(moods, pref.get("moods"))
            if matched_moods:
                reasons.append(f"{', '.join(matched_moods)} 무드를 찾고 있어서 추천해")

            matched_authors = _match(authors, pref.get("authors"))
            if matched_authors:
                reasons.append(f"{', '.join(matched_authors)} 작가를 선호해서 어울려")

            if not reasons:
                reasons.append("내용과 분위기가 취향과 가까워 보여")

            recommendations.append(
                BookRecommendation(
                    book_id=book.item_id,
                    title=book.title,
                    reason="; ".join(reasons),
                    score=book.valuation,
                    metadata=book.metadata,
                )
            )
        return recommendations

    @staticmethod
    def _book_metadata_summary(book: Item) -> str:
        """Compact metadata string for prompts."""
        if book.metadata.get("genres"):
            genres = book.metadata["genres"]
        elif book.facets.get("genre"):
            genres = [book.facets["genre"]]
        else:
            genres = []

        if book.metadata.get("moods"):
            moods = book.metadata["moods"]
        elif book.facets.get("mood"):
            moods = [book.facets["mood"]]
        else:
            moods = []
        author = book.metadata.get("author", "Unknown")
        score_hint = (
            float(book.valuation)
            if isinstance(book.valuation, (int, float))
            else 0.5
        )
        return (
            f"- id={book.item_id}, title={book.title}, author={author}, "
            f"genres={', '.join([g for g in genres if g])}, "
            f"moods={', '.join([m for m in moods if m])}, "
            f"score_hint={score_hint:.2f}"
        )

    def _recommender_initial_proposal(self, context: str) -> str:
        """Recommender's initial proposal (DM-style to critic)."""
        prompt = f"""사용자 정보:
{context}

비평가에게 DM으로 책을 추천하세요.
책 제목과 함께 왜 이 책이 좋은지 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요.

예시:
용의자 X의 헌신 추천해! 히가시노 게이고 작품이라 백야행 좋아했으면 딱일 거야. 반전도 엄청나고 추리 과정이 정말 재밌거든."""

        return self.recommender_client.chat(
            self.recommender_prompt, prompt, temperature=0.7
        )

    def _critic_questions(self, context: str, recommender_msg: str) -> str:
        """Critic questions the recommendations (DM-style to expert)."""
        prompt = f"""추천 전문가의 추천:
{recommender_msg}

사용자 정보:
{context}

추천 전문가에게 DM으로 응답하세요.
질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요.

예시:
좋긴 한데, 다른 작가 작품도 고려해봤어? 김영하 작품도 좋을 것 같은데."""

        return self.critic_client.chat(
            self.critic_prompt, prompt, temperature=0.8
        )

    def _recommender_refines(
        self, context: str, initial: str, criticism: str
    ) -> str:
        """Recommender refines based on criticism (DM-style to critic)."""
        prompt = f"""내 추천:
{initial}

비평가의 의견:
{criticism}

비평가에게 DM으로 응답하세요.
답변하거나 다른 책을 추천할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요.

예시:
맞아, 그것도 좋지. 오리엔트 특급 살인도 추천할게. 고전 추리소설이라 완전 재밌거든."""

        return self.recommender_client.chat(
            self.recommender_prompt, prompt, temperature=0.7
        )

    def _critic_followup(
        self, context: str, conversation: list[ConversationTurn]
    ) -> str:
        """Critic's follow-up questions."""
        conv_history = "\n\n".join(
            f"{'추천 전문가' if turn.speaker == 'recommender' else '나'}: {turn.message}"
            for turn in conversation[-3:]
        )

        prompt = f"""대화 내용:
{conv_history}

사용자 정보:
{context}

추천 전문가에게 DM으로 응답하세요.
추가 질문이나 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요.

예시:
그 책 좋네. 근데 좀 더 가벼운 책은 없을까? 너무 무거운 주제는 부담스러울 수도 있잖아."""

        return self.critic_client.chat(
            self.critic_prompt, prompt, temperature=0.8
        )

    def _recommender_followup(
        self, context: str, conversation: list[ConversationTurn]
    ) -> str:
        """Recommender's follow-up refinement."""
        conv_history = "\n\n".join(
            f"{'나' if turn.speaker == 'recommender' else '비평가'}: {turn.message}"
            for turn in conversation[-3:]
        )

        prompt = f"""대화 내용:
{conv_history}

비평가에게 DM으로 최종 응답하세요.
최종 추천이나 정리할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요.

예시:
그럼 최종적으로 용의자 X의 헌신과 오리엔트 특급 살인 추천할게. 둘 다 미스터리 장르 좋아하면 완전 만족할 거야."""

        return self.recommender_client.chat(
            self.recommender_prompt, prompt, temperature=0.7
        )

    def _generate_final_recommendation(
        self,
        context: str,
        conversation: list[ConversationTurn],
        recommendations: Iterable[BookRecommendation],
    ) -> str:
        """Generate final recommendation summary (DM-style)."""
        conv_summary = "\n".join(
            f"{'BookBot' if turn.speaker == 'recommender' else 'CriticBot'}: {turn.message}"
            for turn in conversation
        )

        rec_lines = "\n".join(
            f"- {rec.title}: {rec.reason}" for rec in recommendations
        )

        prompt = f"""BookBot과 CriticBot의 대화:
{conv_summary}

이 대화를 바탕으로 최종 추천을 요약하세요.
추천 후보와 이유:
{rec_lines or '추천 후보 없음'}

어떤 책을 왜 추천하는지 간단히 설명하세요.
2-3문장으로 작성하세요. 여러 권을 bullet로 제시해도 됩니다."""

        return self.recommender_client.chat(
            self.recommender_prompt, prompt, temperature=0.6
        )

    def _calculate_confidence(
        self,
        conversation: list[ConversationTurn],
        recommendations: Iterable[BookRecommendation] | None = None,
    ) -> float:
        """Calculate confidence score based on conversation."""
        # Simple heuristic: more turns = more refinement = higher confidence
        # In production, this could analyze sentiment or agreement
        base_confidence = 0.6
        turn_bonus = min(len(conversation) * 0.1, 0.3)
        rec_count = len(list(recommendations or []))
        rec_bonus = min(rec_count * 0.05, 0.15)
        return min(base_confidence + turn_bonus + rec_bonus, 0.95)
