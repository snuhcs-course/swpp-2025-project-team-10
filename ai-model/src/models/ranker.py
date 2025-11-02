"""Multi-objective ranking logic for barter candidates."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from data.entities import BarterContext, UserProfile
from graph.candidate import BarterCandidate, ParticipantOffer


@dataclass
class RankScore:
    candidate: BarterCandidate
    score: float
    features: dict[str, float]


class MultiObjectiveRanker:
    """Rule-based approximation of the described multi-objective ranker."""

    def __init__(
        self,
        utility_weight: float = 0.4,
        fairness_weight: float = 0.25,
        preference_weight: float = 0.2,
        closure_weight: float = 0.1,
        risk_weight: float = 0.15,
        logistics_weight: float = 0.1,
    ) -> None:
        self.utility_weight = utility_weight
        self.fairness_weight = fairness_weight
        self.preference_weight = preference_weight
        self.closure_weight = closure_weight
        self.risk_weight = risk_weight
        self.logistics_weight = logistics_weight

    def rank(
        self, candidates: Sequence[BarterCandidate], context: BarterContext
    ) -> list[RankScore]:
        scored = [
            self._score_candidate(candidate, context)
            for candidate in candidates
        ]
        return sorted(scored, key=lambda entry: entry.score, reverse=True)

    def _score_candidate(
        self, candidate: BarterCandidate, context: BarterContext
    ) -> RankScore:
        utility = self._utility(candidate)
        fairness = self._fairness(candidate)
        preference = self._preference_alignment(candidate, context)
        risk = self._risk(candidate, context)
        logistics = self._logistics(candidate)
        closure = self._closure_likelihood(utility, fairness, risk)

        features = {
            "utility_gain": utility,
            "fairness": fairness,
            "preference_overlap": preference,
            "risk_penalty": risk,
            "logistics_cost": logistics,
            "closure_likelihood": closure,
        }

        score = (
            self.utility_weight * utility
            + self.fairness_weight * fairness
            + self.preference_weight * preference
            + self.closure_weight * closure
            - self.risk_weight * risk
            - self.logistics_weight * logistics
        )
        return RankScore(candidate=candidate, score=score, features=features)

    def _utility(self, candidate: BarterCandidate) -> float:
        total_gain = candidate.total_utility_gain()
        return self._normalize(total_gain, scale=100)

    def _fairness(self, candidate: BarterCandidate) -> float:
        delta = candidate.fairness_delta()
        return 1.0 - self._normalize(delta, scale=40)

    def _preference_alignment(
        self, candidate: BarterCandidate, context: BarterContext
    ) -> float:
        total = 0.0
        for offer in candidate.participants:
            profile = context.profiles[offer.user_id]
            total += self._offer_preference_score(offer, profile)
        return total / max(len(candidate.participants), 1)

    def _offer_preference_score(
        self, offer: ParticipantOffer, profile: UserProfile
    ) -> float:
        if not offer.receive_items:
            return 0.0
        scores = [
            profile.preference_score(item) for item in offer.receive_items
        ]
        return sum(scores) / len(scores)

    def _risk(
        self, candidate: BarterCandidate, context: BarterContext
    ) -> float:
        trust_scores = [
            context.profiles[offer.user_id].trust_score
            for offer in candidate.participants
        ]
        if not trust_scores:
            return 1.0
        min_trust = min(trust_scores)
        mean_reliability = sum(
            context.profiles[offer.user_id].reliability
            for offer in candidate.participants
        ) / len(trust_scores)
        base_penalty = max(0.0, 1.0 - min_trust)
        reliability_penalty = max(0.0, 1.0 - mean_reliability)
        return min(1.0, base_penalty * 0.7 + reliability_penalty * 0.3)

    def _logistics(self, candidate: BarterCandidate) -> float:
        cost = candidate.logistics_cost()
        return self._normalize(cost, scale=25)

    def _closure_likelihood(
        self, utility: float, fairness: float, risk: float
    ) -> float:
        # Simple logistic approximation: higher utility/fairness improve, risk lowers.
        linear = 1.5 * utility + 1.0 * fairness - 1.2 * risk
        return 1 / (1 + math.exp(-3 * (linear - 0.5)))

    def _normalize(self, value: float, scale: float) -> float:
        if value <= 0:
            return 0.0
        return min(value / scale, 1.0)
