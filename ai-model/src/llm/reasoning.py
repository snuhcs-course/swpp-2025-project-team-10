"""Reasoning trajectory generation using two-LLM conversation."""

import logging
import os
from dataclasses import asdict, dataclass

from data.entities import Item, UserProfile
from llm.client import ConversationTurn, LLMClient, Message
from llm.config import LLMConfig

logger = logging.getLogger(__name__)


@dataclass
class ReasoningTrajectory:
    """
    A reasoning trajectory showing the conversation between two LLMs.

    This represents a dialogue between a recommender LLM and a critic LLM,
    simulating a thoughtful discussion about book recommendations.
    """

    user_id: str
    recommended_books: list[str]  # Book titles
    conversation: list[ConversationTurn]
    final_recommendation: str
    confidence_score: float

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "recommended_books": self.recommended_books,
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

    def generate_book_recommendation_reasoning(
        self,
        user_profile: UserProfile,
        candidate_books: list[Item],
        user_reading_history: list[str] | None = None,
    ) -> ReasoningTrajectory:
        """
        Generate reasoning trajectory for book recommendations.

        Args:
            user_profile: User's profile with preferences
            candidate_books: List of candidate books to recommend
            user_reading_history: Optional reading history

        Returns:
            ReasoningTrajectory with conversation and final recommendation
        """
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

        # Generate final recommendation
        final_rec = self._generate_final_recommendation(
            context, conversation
        )

        # Calculate confidence score
        confidence = self._calculate_confidence(conversation)

        return ReasoningTrajectory(
            user_id=user_profile.user_id,
            recommended_books=[book.title for book in candidate_books],
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
        pref_str = ", ".join(
            f"{k}: {', '.join(v)}" for k, v in prefs.items()
        )

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

    def _critic_questions(
        self, context: str, recommender_msg: str
    ) -> str:
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
        self, context: str, conversation: list[ConversationTurn]
    ) -> str:
        """Generate final recommendation summary (DM-style)."""
        conv_summary = "\n".join(
            f"{'BookBot' if turn.speaker == 'recommender' else 'CriticBot'}: {turn.message}"
            for turn in conversation
        )

        prompt = f"""BookBot과 CriticBot의 대화:
{conv_summary}

이 대화를 바탕으로 최종 추천을 요약하세요.
어떤 책을 왜 추천하는지 간단히 설명하세요.
2-3문장으로 작성하세요."""

        return self.recommender_client.chat(
            self.recommender_prompt, prompt, temperature=0.6
        )

    def _calculate_confidence(
        self, conversation: list[ConversationTurn]
    ) -> float:
        """Calculate confidence score based on conversation."""
        # Simple heuristic: more turns = more refinement = higher confidence
        # In production, this could analyze sentiment or agreement
        base_confidence = 0.6
        turn_bonus = min(len(conversation) * 0.1, 0.3)
        return min(base_confidence + turn_bonus, 0.95)

