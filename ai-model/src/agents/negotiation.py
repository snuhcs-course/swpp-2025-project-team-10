"""Simplified negotiation agents generating grounded rationales."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from data.entities import BarterContext, Item, UserProfile
from graph.candidate import BarterCandidate, ParticipantOffer

logger = logging.getLogger(__name__)


@dataclass
class NegotiationOutcome:
    match_score: float
    rationale: str
    talking_points: dict[str, list[str]]
    trust_warnings: list[str]
    conversation_history: list[dict[str, str]] | None = None


class NegotiationMediator:
    """Produces negotiation scripts aligned with user interests."""

    def __init__(
        self, fairness_floor: float = 0.65, use_llm: bool = False
    ) -> None:
        self.fairness_floor = fairness_floor
        self.use_llm = use_llm
        self.llm_client = None

        if use_llm:
            try:
                from llm.client import LLMClient

                self.llm_client = LLMClient()
                logger.info("NegotiationMediator initialized with LLM")
            except ImportError:
                logger.warning(
                    "LLM client not available, using rule-based approach"
                )
                self.use_llm = False

    def mediate(
        self,
        candidate: BarterCandidate,
        context: BarterContext,
        fairness: float,
    ) -> NegotiationOutcome:
        if self.use_llm and self.llm_client:
            return self._mediate_with_llm(candidate, context, fairness)
        else:
            return self._mediate_rule_based(candidate, context, fairness)

    def _mediate_rule_based(
        self,
        candidate: BarterCandidate,
        context: BarterContext,
        fairness: float,
    ) -> NegotiationOutcome:
        """Original rule-based mediation."""
        talking_points: dict[str, list[str]] = {}
        trust_warnings: list[str] = []
        for offer in candidate.participants:
            profile = context.profiles[offer.user_id]
            talking_points[offer.user_id] = self._talking_points(
                offer, profile
            )
            if profile.trust_score < context.trust_threshold:
                trust_warnings.append(
                    f"{profile.display_name} has low trust score "
                    f"({profile.trust_score:.2f})."
                )
            trust_warnings.extend(profile.risk_notes)

        rationale = self._compose_rationale(candidate, context)
        match_score = max(self.fairness_floor, fairness)
        return NegotiationOutcome(
            match_score=match_score,
            rationale=rationale,
            talking_points=talking_points,
            trust_warnings=trust_warnings,
            conversation_history=None,
        )

    def _mediate_with_llm(
        self,
        candidate: BarterCandidate,
        context: BarterContext,
        fairness: float,
    ) -> NegotiationOutcome:
        """LLM-based mediation with conversation."""
        from llm.client import Message

        # Prepare context for LLM
        context_str = self._prepare_llm_context(candidate, context)

        # Generate conversation between two LLM agents
        conversation_history = []

        # Agent 1: Proposer (suggests the barter)
        proposer_prompt = (
            "You are a barter negotiation agent representing the "
            "person offering books. Explain why this barter is "
            "beneficial."
        )
        proposer_msg = self.llm_client.chat(
            proposer_prompt, context_str, temperature=0.7
        )
        conversation_history.append(
            {"speaker": "proposer", "message": proposer_msg}
        )

        # Agent 2: Evaluator (evaluates the proposal)
        evaluator_prompt = (
            "You are a critical evaluator assessing a barter proposal. "
            "Identify benefits and potential concerns."
        )
        evaluator_context = (
            f"{context_str}\n\nProposal:\n{proposer_msg}"
        )
        evaluator_msg = self.llm_client.chat(
            evaluator_prompt, evaluator_context, temperature=0.8
        )
        conversation_history.append(
            {"speaker": "evaluator", "message": evaluator_msg}
        )

        # Agent 1: Refines based on evaluation
        refine_context = (
            f"{context_str}\n\n"
            f"Initial proposal: {proposer_msg}\n\n"
            f"Evaluation: {evaluator_msg}\n\n"
            f"Provide a refined recommendation."
        )
        refined_msg = self.llm_client.chat(
            proposer_prompt, refine_context, temperature=0.7
        )
        conversation_history.append(
            {"speaker": "proposer", "message": refined_msg}
        )

        # Extract talking points from conversation
        talking_points = self._extract_talking_points_from_llm(
            conversation_history, candidate
        )

        # Check trust warnings
        trust_warnings = []
        for offer in candidate.participants:
            profile = context.profiles[offer.user_id]
            if profile.trust_score < context.trust_threshold:
                trust_warnings.append(
                    f"{profile.display_name} has low trust score "
                    f"({profile.trust_score:.2f})."
                )
            trust_warnings.extend(profile.risk_notes)

        match_score = max(self.fairness_floor, fairness)

        return NegotiationOutcome(
            match_score=match_score,
            rationale=refined_msg,
            talking_points=talking_points,
            trust_warnings=trust_warnings,
            conversation_history=conversation_history,
        )

    def _talking_points(
        self, offer: ParticipantOffer, profile: UserProfile
    ) -> list[str]:
        points: list[str] = []
        for item in offer.receive_items:
            points.append(
                f"Highlight that '{item.title}' matches your preference for "
                f"{self._facet_summary(item)}."
            )
            points.append(
                f"Emphasize valuation parity: receiving ≈{item.valuation:.0f} credits "
                f"for items you value at ≈{offer.given_value:.0f}."
            )
        if profile.preferences.get("delivery"):
            preferred = ", ".join(profile.preferences["delivery"])
            points.append(
                f"Negotiate for delivery methods you prefer ({preferred})."
            )
        if offer.notes.get("type") == "triad":
            points.append(
                "Clarify hand-off order among the triad to avoid confusion."
            )
        return points

    def _facet_summary(self, item: Item) -> str:
        facets = [
            f"{key}={value}" for key, value in sorted(item.facets.items())
        ]
        return ", ".join(facets)

    def _compose_rationale(
        self, candidate: BarterCandidate, context: BarterContext
    ) -> str:
        segments: list[str] = []
        for offer in candidate.participants:
            profile = context.profiles[offer.user_id]
            received = (
                ", ".join(item.title for item in offer.receive_items)
                or "no new items"
            )
            given = (
                ", ".join(item.title for item in offer.give_items)
                or "nothing"
            )
            preference_score = context.profiles[
                offer.user_id
            ].preference_score(
                offer.receive_items[0]
                if offer.receive_items
                else offer.give_items[0]
            )
            segments.append(
                f"{profile.display_name} receives {received} in "
                f"exchange for {given}. Preference fit ≈ "
                f"{preference_score:.2f}."
            )
        return " ".join(segments)

    def _prepare_llm_context(
        self, candidate: BarterCandidate, context: BarterContext
    ) -> str:
        """Prepare context string for LLM."""
        parts = []

        for offer in candidate.participants:
            profile = context.profiles[offer.user_id]

            # User info
            parts.append(f"User: {profile.display_name}")
            parts.append(f"Trust Score: {profile.trust_score:.2f}")

            # Preferences
            if profile.preferences:
                pref_str = ", ".join(
                    f"{k}: {', '.join(v)}"
                    for k, v in profile.preferences.items()
                )
                parts.append(f"Preferences: {pref_str}")

            # Books they're giving
            if offer.give_items:
                giving = ", ".join(item.title for item in offer.give_items)
                parts.append(f"Offering: {giving}")

            # Books they're receiving
            if offer.receive_items:
                receiving = ", ".join(
                    item.title for item in offer.receive_items
                )
                parts.append(f"Receiving: {receiving}")

            parts.append("")  # Blank line between users

        return "\n".join(parts)

    def _extract_talking_points_from_llm(
        self,
        conversation: list[dict[str, str]],
        candidate: BarterCandidate,
    ) -> dict[str, list[str]]:
        """Extract talking points from LLM conversation."""
        talking_points: dict[str, list[str]] = {}

        # Simple extraction: use the refined message
        if len(conversation) >= 3:
            refined = conversation[2]["message"]

            # Assign to each participant
            for offer in candidate.participants:
                talking_points[offer.user_id] = [
                    refined[:200] + "..."
                    if len(refined) > 200
                    else refined
                ]

        return talking_points
