from data.entities import (
    BarterContext,
    Item,
    TradeRequest,
    UserProfile,
)
from pipeline.recommender import BarterRecommender


def build_context() -> BarterContext:
    items = {
        "book_a": Item(
            item_id="book_a",
            owner_id="alice",
            title="Data Structures 101",
            valuation=32,
            facets={
                "category": "book",
                "condition": "good",
                "delivery": "meetup_only",
                "themes": "educational",
            },
        ),
        "book_b": Item(
            item_id="book_b",
            owner_id="bob",
            title="Signed Sci-Fi Classic",
            valuation=36,
            facets={
                "category": "book",
                "condition": "like_new",
                "delivery": "meetup_only",
                "themes": "collectible",
            },
        ),
        "game_c": Item(
            item_id="game_c",
            owner_id="carla",
            title="Cozy Cooperative Board Game",
            valuation=28,
            facets={
                "category": "board_game",
                "condition": "good",
                "delivery": "courier_ok",
                "themes": "cooperative",
            },
        ),
    }

    profiles = {
        "alice": UserProfile(
            user_id="alice",
            display_name="Alice",
            trust_score=0.92,
            reliability=0.96,
            preferences={
                "category": ["book", "board_game"],
                "condition": ["good", "like_new"],
                "delivery": ["meetup_only"],
            },
        ),
        "bob": UserProfile(
            user_id="bob",
            display_name="Bob",
            trust_score=0.84,
            reliability=0.88,
            preferences={
                "category": ["book", "board_game"],
                "condition": ["good", "like_new"],
                "delivery": ["meetup_only", "courier_ok"],
            },
        ),
        "carla": UserProfile(
            user_id="carla",
            display_name="Carla",
            trust_score=0.68,
            reliability=0.72,
            preferences={
                "category": ["book"],
                "condition": ["good"],
                "delivery": ["courier_ok"],
            },
        ),
    }

    requests = [
        TradeRequest(user_id="alice", desired_item_ids=["book_b"]),
        TradeRequest(user_id="bob", desired_item_ids=["game_c", "book_a"]),
        TradeRequest(user_id="carla", desired_item_ids=["book_a"]),
    ]

    distance_matrix = {
        ("alice", "bob"): 4.0,
        ("bob", "carla"): 6.0,
        ("alice", "carla"): 8.0,
    }

    return BarterContext(
        items=items,
        profiles=profiles,
        requests=requests,
        distance_matrix=distance_matrix,
        trust_threshold=0.6,
    )


def test_recommender_prefers_balanced_two_way_swap():
    context = build_context()
    recommender = BarterRecommender()

    recommendations = recommender.recommend(context, limit=2)

    assert recommendations, "Expected at least one recommendation"
    top = recommendations[0]
    participant_ids = {offer.user_id for offer in top.candidate.participants}

    # Two-way swap between Alice and Bob should be top ranked.
    assert participant_ids == {"alice", "bob"}
    assert top.rank_score.score > 0.4
    assert top.rank_score.features["fairness"] > 0.6
    assert "Data Structures" in top.negotiation.rationale
    assert top.negotiation.match_score >= top.rank_score.features["fairness"]


def test_recommender_includes_negotiation_talking_points():
    context = build_context()
    recommender = BarterRecommender()
    rec = recommender.recommend(context, limit=1)[0]

    alice_points = rec.negotiation.talking_points["alice"]
    assert any("valuation parity" in point.lower() for point in alice_points)
    assert rec.negotiation.trust_warnings == []
