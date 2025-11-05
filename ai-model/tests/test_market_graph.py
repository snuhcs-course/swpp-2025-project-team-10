from data.entities import (
    BarterContext,
    Item,
    TradeRequest,
    UserProfile,
)
from graph.market_graph import MarketGraphBuilder


def _profile(user_id: str) -> UserProfile:
    return UserProfile(
        user_id=user_id,
        display_name=user_id.title(),
        trust_score=0.8,
        reliability=0.9,
        preferences={},
    )


def test_market_graph_builds_edges():
    items = {
        "book_a": Item(
            item_id="book_a",
            owner_id="alice",
            title="Data Structures",
            valuation=30,
            facets={
                "category": "book",
                "condition": "good",
                "delivery": "meetup_only",
            },
        ),
        "book_b": Item(
            item_id="book_b",
            owner_id="bob",
            title="Rare Sci-Fi",
            valuation=35,
            facets={
                "category": "book",
                "condition": "like_new",
                "delivery": "meetup_only",
            },
        ),
    }
    context = BarterContext(
        items=items,
        profiles={"alice": _profile("alice"), "bob": _profile("bob")},
        requests=[
            TradeRequest(user_id="alice", desired_item_ids=["book_b"]),
            TradeRequest(user_id="bob", desired_facets={"category": ["book"]}),
        ],
    )

    graph = MarketGraphBuilder().build(context)

    assert sorted(graph.ownership_edges["alice"]) == ["book_a"]
    assert sorted(graph.demand_edges["book_b"]) == ["alice"]
    assert ("book_a", "book_b") in graph.compatibility
