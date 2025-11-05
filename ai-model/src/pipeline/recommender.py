"""End-to-end pipeline orchestrating barter recommendations."""

from __future__ import annotations

from dataclasses import dataclass

from agents.negotiation import NegotiationMediator, NegotiationOutcome
from data.entities import BarterContext
from graph.candidate import BarterCandidate
from graph.candidate_generator import CandidateGenerator
from graph.market_graph import MarketGraphBuilder
from models.ranker import MultiObjectiveRanker, RankScore


@dataclass
class Recommendation:
    candidate: BarterCandidate
    rank_score: RankScore
    negotiation: NegotiationOutcome


class BarterRecommender:
    """High-level façade aligning with the architecture specification."""

    def __init__(
        self,
        graph_builder: MarketGraphBuilder | None = None,
        candidate_generator: CandidateGenerator | None = None,
        ranker: MultiObjectiveRanker | None = None,
        mediator: NegotiationMediator | None = None,
    ) -> None:
        self.graph_builder = graph_builder or MarketGraphBuilder()
        self.candidate_generator = candidate_generator or CandidateGenerator()
        self.ranker = ranker or MultiObjectiveRanker()
        self.mediator = mediator or NegotiationMediator()

    def recommend(
        self, context: BarterContext, limit: int = 3
    ) -> list[Recommendation]:
        graph = self.graph_builder.build(context)
        candidates = self.candidate_generator.generate(graph, context)
        if not candidates:
            return []

        ranked = self.ranker.rank(candidates, context)
        recommendations: list[Recommendation] = []
        for entry in ranked[:limit]:
            negotiation = self.mediator.mediate(
                entry.candidate, context, entry.features["fairness"]
            )
            recommendations.append(
                Recommendation(
                    candidate=entry.candidate,
                    rank_score=entry,
                    negotiation=negotiation,
                )
            )
        return recommendations
