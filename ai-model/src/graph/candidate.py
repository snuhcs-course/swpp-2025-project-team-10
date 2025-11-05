"""Candidate barter structures produced from the market graph."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from data.entities import Item


@dataclass
class ParticipantOffer:
    """Represents what a participant gives and receives in a trade."""

    user_id: str
    give_items: Sequence[Item]
    receive_items: Sequence[Item]
    notes: dict[str, str] = field(default_factory=dict)

    @property
    def given_value(self) -> float:
        return sum(item.valuation for item in self.give_items)

    @property
    def received_value(self) -> float:
        return sum(item.valuation for item in self.receive_items)

    @property
    def net_gain(self) -> float:
        return self.received_value - self.given_value


@dataclass
class BarterCandidate:
    """Concrete trade candidate, potentially involving multiple users."""

    participants: Sequence[ParticipantOffer]
    metadata: dict[str, float] = field(default_factory=dict)

    def participant_ids(self) -> list[str]:
        return [offer.user_id for offer in self.participants]

    def min_trust(self) -> float:
        return min(
            self.metadata.get(f"trust:{p.user_id}", 1.0)
            for p in self.participants
        )

    def total_utility_gain(self) -> float:
        return sum(max(offer.net_gain, 0.0) for offer in self.participants)

    def fairness_delta(self) -> float:
        gains = [offer.net_gain for offer in self.participants]
        if not gains:
            return 0.0
        return max(gains) - min(gains)

    def logistics_cost(self) -> float:
        return self.metadata.get("logistics_cost", 0.0)


def flatten_items(participants: Iterable[ParticipantOffer]) -> list[Item]:
    items: list[Item] = []
    for offer in participants:
        items.extend(offer.receive_items)
        items.extend(offer.give_items)
    return items
