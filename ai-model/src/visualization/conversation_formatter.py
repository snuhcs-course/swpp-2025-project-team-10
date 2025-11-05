"""Format LLM conversations for frontend display."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from llm.reasoning import ReasoningTrajectory


@dataclass
class ConversationMessage:
    """A single message in the conversation display."""

    id: str
    speaker: str
    speaker_role: str  # "recommender" or "critic"
    message: str
    timestamp: str
    avatar_type: str  # "ai_recommender" or "ai_critic"
    reasoning_note: str | None = None


@dataclass
class FormattedConversation:
    """
    Formatted conversation for frontend display.

    This format is designed to be easily consumed by Android/Kotlin
    frontend for displaying as a chat-like interface.
    """

    conversation_id: str
    user_id: str
    recommended_books: list[str]
    messages: list[ConversationMessage]
    final_recommendation: str
    confidence_score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "recommended_books": self.recommended_books,
            "messages": [
                {
                    "id": msg.id,
                    "speaker": msg.speaker,
                    "speaker_role": msg.speaker_role,
                    "message": msg.message,
                    "timestamp": msg.timestamp,
                    "avatar_type": msg.avatar_type,
                    "reasoning_note": msg.reasoning_note,
                }
                for msg in self.messages
            ],
            "final_recommendation": self.final_recommendation,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class ConversationFormatter:
    """
    Format reasoning trajectories and negotiations as conversations.

    This class transforms the LLM reasoning trajectory into a
    chat-like format that can be displayed in the frontend as a
    conversation between two AI agents discussing book recommendations.
    """

    @staticmethod
    def format_reasoning_trajectory(
        trajectory: ReasoningTrajectory,
        conversation_id: str | None = None,
    ) -> FormattedConversation:
        """
        Format a reasoning trajectory as a conversation.

        Args:
            trajectory: ReasoningTrajectory from LLM
            conversation_id: Optional conversation ID

        Returns:
            FormattedConversation ready for frontend display
        """
        conv_id = conversation_id or ConversationFormatter._generate_id()

        messages = []
        for idx, turn in enumerate(trajectory.conversation):
            # Determine speaker details
            if turn.speaker == "recommender":
                speaker_name = "BookBot"
                speaker_role = "recommender"
                avatar_type = "ai_recommender"
            else:  # critic
                speaker_name = "CriticBot"
                speaker_role = "critic"
                avatar_type = "ai_critic"

            # Create message
            msg = ConversationMessage(
                id=f"{conv_id}_msg_{idx}",
                speaker=speaker_name,
                speaker_role=speaker_role,
                message=turn.message,
                timestamp=ConversationFormatter._generate_timestamp(idx),
                avatar_type=avatar_type,
                reasoning_note=turn.reasoning,
            )
            messages.append(msg)

        # Metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "num_turns": len(trajectory.conversation),
            "model_type": "llm_conversation",
        }

        return FormattedConversation(
            conversation_id=conv_id,
            user_id=trajectory.user_id,
            recommended_books=trajectory.recommended_books,
            messages=messages,
            final_recommendation=trajectory.final_recommendation,
            confidence_score=trajectory.confidence_score,
            metadata=metadata,
        )

    @staticmethod
    def format_negotiation_conversation(
        conversation_history: list[dict[str, str]],
        user_id: str,
        books: list[str],
        final_recommendation: str,
        confidence: float,
        conversation_id: str | None = None,
    ) -> FormattedConversation:
        """
        Format a negotiation conversation.

        Args:
            conversation_history: List of conversation turns
            user_id: User ID
            books: List of book titles
            final_recommendation: Final recommendation text
            confidence: Confidence score
            conversation_id: Optional conversation ID

        Returns:
            FormattedConversation ready for frontend display
        """
        conv_id = conversation_id or ConversationFormatter._generate_id()

        messages = []
        for idx, turn in enumerate(conversation_history):
            speaker = turn.get("speaker", "unknown")

            # Map speaker to display name
            if speaker == "proposer":
                speaker_name = "BarterBot"
                speaker_role = "recommender"
                avatar_type = "ai_recommender"
            elif speaker == "evaluator":
                speaker_name = "EvaluatorBot"
                speaker_role = "critic"
                avatar_type = "ai_critic"
            else:
                speaker_name = speaker.capitalize()
                speaker_role = "unknown"
                avatar_type = "ai_recommender"

            msg = ConversationMessage(
                id=f"{conv_id}_msg_{idx}",
                speaker=speaker_name,
                speaker_role=speaker_role,
                message=turn.get("message", ""),
                timestamp=ConversationFormatter._generate_timestamp(idx),
                avatar_type=avatar_type,
                reasoning_note=None,
            )
            messages.append(msg)

        metadata = {
            "generated_at": datetime.now().isoformat(),
            "num_turns": len(conversation_history),
            "model_type": "negotiation_conversation",
        }

        return FormattedConversation(
            conversation_id=conv_id,
            user_id=user_id,
            recommended_books=books,
            messages=messages,
            final_recommendation=final_recommendation,
            confidence_score=confidence,
            metadata=metadata,
        )

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique conversation ID."""
        from uuid import uuid4

        return f"conv_{uuid4().hex[:12]}"

    @staticmethod
    def _generate_timestamp(turn_index: int) -> str:
        """
        Generate timestamp for a conversation turn.

        Args:
            turn_index: Index of the turn (0, 1, 2, ...)

        Returns:
            ISO format timestamp
        """
        # Simulate timestamps with 2-second intervals
        from datetime import timedelta

        base_time = datetime.now()
        turn_time = base_time + timedelta(seconds=turn_index * 2)
        return turn_time.isoformat()

    @staticmethod
    def format_for_android(
        conversation: FormattedConversation,
    ) -> dict[str, Any]:
        """
        Format conversation specifically for Android/Kotlin consumption.

        This adds Android-specific fields and formatting.

        Args:
            conversation: FormattedConversation to format

        Returns:
            Dictionary optimized for Android RecyclerView display
        """
        return {
            "conversationId": conversation.conversation_id,
            "userId": conversation.user_id,
            "recommendedBooks": conversation.recommended_books,
            "messages": [
                {
                    "id": msg.id,
                    "speaker": msg.speaker,
                    "speakerRole": msg.speaker_role,
                    "message": msg.message,
                    "timestamp": msg.timestamp,
                    "avatarType": msg.avatar_type,
                    "reasoningNote": msg.reasoning_note,
                    # Android-specific fields
                    "viewType": (
                        "MESSAGE_LEFT"
                        if msg.speaker_role == "recommender"
                        else "MESSAGE_RIGHT"
                    ),
                    "backgroundColor": (
                        "#E3F2FD"
                        if msg.speaker_role == "recommender"
                        else "#FFF3E0"
                    ),
                }
                for msg in conversation.messages
            ],
            "finalRecommendation": conversation.final_recommendation,
            "confidenceScore": conversation.confidence_score,
            "confidenceLevel": ConversationFormatter._confidence_level(
                conversation.confidence_score
            ),
            "metadata": conversation.metadata,
        }

    @staticmethod
    def _confidence_level(score: float) -> str:
        """Convert confidence score to level."""
        if score >= 0.8:
            return "HIGH"
        elif score >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"

