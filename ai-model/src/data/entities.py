"""Domain entities used throughout the bartering AI pipeline."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

FacetMap = Mapping[str, str]


@dataclass
class Item:
    """Represents a tradable asset owned by a user."""

    item_id: str
    owner_id: str
    title: str
    valuation: float
    facets: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, any] = field(default_factory=dict)

    def facet(self, key: str, default: str = "") -> str:
        return self.facets.get(key, default)


@dataclass
class UserProfile:
    """Simplified user profile capturing trust and preferences."""

    user_id: str
    display_name: str
    trust_score: float
    reliability: float
    preferences: dict[str, Iterable[str]] = field(default_factory=dict)
    exclusion_rules: Sequence[str] = field(default_factory=list)
    risk_notes: Sequence[str] = field(default_factory=list)

    def preference_score(self, item: Item) -> float:
        """Return a preference match score in [0, 1] for the given item."""
        if not self.preferences:
            return 0.5  # neutral baseline

        matches = 0
        total = 0
        for facet, accepted_values in self.preferences.items():
            if facet not in item.facets:
                continue
            total += 1
            if item.facets[facet] in accepted_values:
                matches += 1

        if total == 0:
            return 0.5
        return matches / total


@dataclass
class TradeRequest:
    """Represents a user's active desire for items or facets."""

    user_id: str
    desired_item_ids: Sequence[str] = field(default_factory=list)
    desired_facets: dict[str, Iterable[str]] = field(default_factory=dict)
    urgency: str = "flexible"
    logistic_preferences: str | None = None

    def matches_item(self, item: Item) -> bool:
        if item.item_id in self.desired_item_ids:
            return True

        for facet, allowed in self.desired_facets.items():
            if item.facets.get(facet) not in allowed:
                return False
        return bool(self.desired_facets)


@dataclass
class BarterContext:
    """Aggregated view of inventory, profiles, and trade signals."""

    items: Mapping[str, Item]
    profiles: Mapping[str, UserProfile]
    requests: Sequence[TradeRequest]
    distance_matrix: Mapping[tuple[str, str], float] = field(
        default_factory=dict
    )
    trust_threshold: float = 0.4

    def user_items(self, user_id: str) -> list[Item]:
        return [
            item for item in self.items.values() if item.owner_id == user_id
        ]

    def active_request_for(self, user_id: str) -> TradeRequest | None:
        for request in self.requests:
            if request.user_id == user_id:
                return request
        return None

    def users(self) -> list[str]:
        return list(self.profiles.keys())

    def distance(self, user_a: str, user_b: str) -> float:
        if user_a == user_b:
            return 0.0
        key = (user_a, user_b)
        if key in self.distance_matrix:
            return self.distance_matrix[key]
        key = (user_b, user_a)
        return self.distance_matrix.get(key, 0.0)
