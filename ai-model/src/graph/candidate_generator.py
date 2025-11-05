"""Utilities to generate barter candidates from a market graph."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from data.entities import BarterContext
from graph.candidate import BarterCandidate, ParticipantOffer
from graph.market_graph import MarketGraph


@dataclass
class CandidateGenerator:
    """Generates swap candidates up to a configurable cycle length."""

    max_cycle: int = 3

    def generate(
        self, graph: MarketGraph, context: BarterContext
    ) -> list[BarterCandidate]:
        two_way = self._generate_two_way(graph, context)
        if self.max_cycle < 3:
            return two_way
        triadic = self._generate_triads(graph, context)
        return two_way + triadic

    def _generate_two_way(
        self, graph: MarketGraph, context: BarterContext
    ) -> list[BarterCandidate]:
        candidates: list[BarterCandidate] = []
        for user_a, items_a in graph.ownership_edges.items():
            for user_b, items_b in graph.ownership_edges.items():
                if user_a >= user_b:
                    continue
                matches_ab = self._match_items(
                    user_a, user_b, items_a, context, graph
                )
                matches_ba = self._match_items(
                    user_b, user_a, items_b, context, graph
                )
                if not matches_ab or not matches_ba:
                    continue
                for item_a in matches_ab:
                    for item_b in matches_ba:
                        participants = [
                            ParticipantOffer(
                                user_id=user_a,
                                give_items=[context.items[item_a]],
                                receive_items=[context.items[item_b]],
                                notes={"type": "two-way"},
                            ),
                            ParticipantOffer(
                                user_id=user_b,
                                give_items=[context.items[item_b]],
                                receive_items=[context.items[item_a]],
                                notes={"type": "two-way"},
                            ),
                        ]
                        metadata = self._base_metadata(participants, context)
                        candidates.append(
                            BarterCandidate(participants, metadata)
                        )
        return candidates

    def _generate_triads(
        self, graph: MarketGraph, context: BarterContext
    ) -> list[BarterCandidate]:
        candidates: list[BarterCandidate] = []
        users = list(graph.ownership_edges.keys())
        for idx_a, user_a in enumerate(users):
            for idx_b in range(idx_a + 1, len(users)):
                user_b = users[idx_b]
                for idx_c in range(idx_b + 1, len(users)):
                    user_c = users[idx_c]
                    path = self._find_triad(
                        user_a, user_b, user_c, graph, context
                    )
                    if not path:
                        continue
                    item_ab, item_bc, item_ca = path
                    participants = [
                        ParticipantOffer(
                            user_id=user_a,
                            give_items=[context.items[item_ca]],
                            receive_items=[context.items[item_ab]],
                            notes={"type": "triad"},
                        ),
                        ParticipantOffer(
                            user_id=user_b,
                            give_items=[context.items[item_ab]],
                            receive_items=[context.items[item_bc]],
                            notes={"type": "triad"},
                        ),
                        ParticipantOffer(
                            user_id=user_c,
                            give_items=[context.items[item_bc]],
                            receive_items=[context.items[item_ca]],
                            notes={"type": "triad"},
                        ),
                    ]
                    metadata = self._base_metadata(participants, context)
                    candidates.append(BarterCandidate(participants, metadata))
        return candidates

    def _match_items(
        self,
        owner_id: str,
        requester_id: str,
        item_ids: Sequence[str],
        context: BarterContext,
        graph: MarketGraph,
    ) -> list[str]:
        matches: list[str] = []
        request = context.active_request_for(requester_id)
        if not request:
            return matches
        for item_id in item_ids:
            if requester_id not in graph.demand_edges.get(item_id, []):
                continue
            if item_id in request.desired_item_ids or request.matches_item(
                context.items[item_id]
            ):
                matches.append(item_id)
        return matches

    def _find_triad(
        self,
        user_a: str,
        user_b: str,
        user_c: str,
        graph: MarketGraph,
        context: BarterContext,
    ) -> tuple[str, str, str] | None:
        request_a = context.active_request_for(user_a)
        request_b = context.active_request_for(user_b)
        request_c = context.active_request_for(user_c)
        if not (request_a and request_b and request_c):
            return None

        items_a = graph.ownership_edges[user_a]
        items_b = graph.ownership_edges[user_b]
        items_c = graph.ownership_edges[user_c]

        for item_ab in self._match_items(
            user_b, user_a, items_b, context, graph
        ):
            for item_bc in self._match_items(
                user_c, user_b, items_c, context, graph
            ):
                for item_ca in self._match_items(
                    user_a, user_c, items_a, context, graph
                ):
                    return item_ab, item_bc, item_ca
        return None

    def _base_metadata(
        self, participants: Sequence[ParticipantOffer], context: BarterContext
    ) -> dict[str, float]:
        metadata: dict[str, float] = {}
        for offer in participants:
            profile = context.profiles[offer.user_id]
            metadata[f"trust:{offer.user_id}"] = profile.trust_score
        metadata["logistics_cost"] = self._logistics_cost(
            participants, context
        )
        return metadata

    def _logistics_cost(
        self, participants: Sequence[ParticipantOffer], context: BarterContext
    ) -> float:
        cost = 0.0
        users = [offer.user_id for offer in participants]
        for idx, user_a in enumerate(users):
            for user_b in users[idx + 1 :]:
                cost += context.distance(user_a, user_b)
        return cost / max(len(users) - 1, 1)
