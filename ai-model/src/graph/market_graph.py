"""Market graph construction utilities."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from data.entities import BarterContext, Item, TradeRequest


@dataclass
class MarketGraph:
    """Simplified bipartite representation of barter opportunities."""

    ownership_edges: dict[str, list[str]]
    demand_edges: dict[str, list[str]]
    compatibility: dict[tuple[str, str], float]

    def owners_of(self, item_id: str) -> list[str]:
        return [
            owner
            for owner, items in self.ownership_edges.items()
            if item_id in items
        ]

    def interested_users(self, item_id: str) -> list[str]:
        return self.demand_edges.get(item_id, [])

    def compatible(self, item_a: str, item_b: str) -> float:
        return self.compatibility.get((item_a, item_b), 0.0)


class MarketGraphBuilder:
    """Constructs a market graph from raw context data."""

    def __init__(self, value_gap_tolerance: float = 0.25) -> None:
        self.value_gap_tolerance = value_gap_tolerance

    def build(self, context: BarterContext) -> MarketGraph:
        ownership_edges: dict[str, list[str]] = defaultdict(list)
        demand_edges: dict[str, list[str]] = defaultdict(list)
        compatibility: dict[tuple[str, str], float] = {}

        for item in context.items.values():
            ownership_edges[item.owner_id].append(item.item_id)

        for request in context.requests:
            for item in context.items.values():
                if self._matches_request(item, request):
                    demand_edges[item.item_id].append(request.user_id)

        item_list = list(context.items.values())
        for idx, item_a in enumerate(item_list):
            for item_b in item_list[idx + 1 :]:
                comp = self._compatibility_score(item_a, item_b)
                if comp > 0:
                    compatibility[(item_a.item_id, item_b.item_id)] = comp
                    compatibility[(item_b.item_id, item_a.item_id)] = comp

        return MarketGraph(
            ownership_edges=dict(ownership_edges),
            demand_edges=dict(demand_edges),
            compatibility=compatibility,
        )

    def _matches_request(self, item: Item, request: TradeRequest) -> bool:
        if item.owner_id == request.user_id:
            return False
        if (
            request.desired_item_ids
            and item.item_id in request.desired_item_ids
        ):
            return True
        if not request.desired_facets:
            return False
        for facet, allowed_values in request.desired_facets.items():
            if item.facets.get(facet) not in allowed_values:
                return False
        return True

    def _compatibility_score(self, item_a: Item, item_b: Item) -> float:
        if item_a.owner_id == item_b.owner_id:
            return 0.0
        facets = {"category", "condition", "delivery"}
        matches = sum(
            1
            for facet in facets
            if item_a.facets.get(facet) == item_b.facets.get(facet)
        )
        if matches == 0:
            return 0.0
        value_ratio = min(item_a.valuation, item_b.valuation) / max(
            item_a.valuation, item_b.valuation
        )
        if value_ratio < 1 - self.value_gap_tolerance:
            return 0.0
        return (matches / len(facets)) * value_ratio
