"""
Test LLM integration with local model and save examples as YAML.

This script runs actual tests with the local LLM model and saves
the outputs as YAML files for documentation and verification.
"""

import os
import sys
from pathlib import Path

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from adapters.backend_adapter import BackendDataAdapter
from adapters.frontend_adapter import FrontendDataAdapter
from data.entities import Item, UserProfile
from llm.reasoning import ReasoningGenerator
from visualization.conversation_formatter import (
    ConversationFormatter,
)


def setup_environment():
    """Set up environment for local LLM testing."""
    os.environ["USE_LOCAL_MODEL"] = "true"
    os.environ["LOCAL_MODEL_PATH"] = "models/gemma3-4b-it"
    os.environ["REASONING_MAX_TURNS"] = "3"
    os.environ["LOG_LEVEL"] = "INFO"


def save_yaml(data: dict, filename: str, examples_dir: Path):
    """Save data as YAML file."""
    output_path = examples_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
    print(f"✅ Saved: {output_path}")
    return output_path


def test_example_1_mystery_lover():
    """Example 1: Mystery book lover with strong preferences."""
    print("\n" + "=" * 70)
    print("Example 1: Mystery Book Lover")
    print("=" * 70)

    # Backend user data
    user_data = {
        "id": 101,
        "username": "mystery_maven",
        "location": "Seoul, Gangnam-gu",
        "reputation_score": 92,
        "successful_trades": 18,
    }

    user_taste = {
        "favorite_genres": ["mystery", "thriller", "detective"],
        "favorite_authors": [
            "Agatha Christie",
            "Arthur Conan Doyle",
            "Dan Brown",
        ],
        "favorite_books": [
            "Murder on the Orient Express",
            "The Hound of the Baskervilles",
        ],
        "preferred_moods": ["suspenseful", "intellectual", "engaging"],
        "reading_purposes": ["entertainment", "mental_stimulation"],
        "preferred_length": "medium",
    }

    user_preferences = {
        "max_barter_distance": 30,
        "preferred_meeting_locations": "Gangnam Station Exit 10, Coex Mall",
    }

    # Transform to AI model format
    user_profile = BackendDataAdapter.transform_user_profile(
        user_data, user_taste, user_preferences
    )

    # Candidate books
    candidate_books = [
        Item(
            item_id="book_101",
            owner_id="owner_201",
            title="The Da Vinci Code",
            valuation=0.92,
            facets={
                "author": "Dan Brown",
                "genre": "mystery",
                "condition": "good",
            },
            metadata={
                "author": "Dan Brown",
                "year": "2003",
                "pages": 454,
            },
        ),
        Item(
            item_id="book_102",
            owner_id="owner_202",
            title="Gone Girl",
            valuation=0.88,
            facets={
                "author": "Gillian Flynn",
                "genre": "thriller",
                "condition": "like_new",
            },
            metadata={
                "author": "Gillian Flynn",
                "year": "2012",
                "pages": 432,
            },
        ),
        Item(
            item_id="book_103",
            owner_id="owner_203",
            title="The Girl with the Dragon Tattoo",
            valuation=0.90,
            facets={
                "author": "Stieg Larsson",
                "genre": "thriller",
                "condition": "good",
            },
            metadata={
                "author": "Stieg Larsson",
                "year": "2005",
                "pages": 465,
            },
        ),
    ]

    reading_history = [
        "Murder on the Orient Express",
        "And Then There Were None",
        "The Hound of the Baskervilles",
        "Angels & Demons",
    ]

    # Generate reasoning
    generator = ReasoningGenerator()
    trajectory = generator.generate_book_recommendation_reasoning(
        user_profile=user_profile,
        candidate_books=candidate_books,
        user_reading_history=reading_history,
    )

    # Format for frontend
    formatted = ConversationFormatter.format_reasoning_trajectory(trajectory)
    android_format = ConversationFormatter.format_for_android(formatted)

    # Prepare YAML output
    example_data = {
        "example_id": "example_1_mystery_lover",
        "description": "Mystery book lover with strong genre preferences",
        "input": {
            "user_profile": {
                "user_id": user_profile.user_id,
                "display_name": user_profile.display_name,
                "trust_score": float(user_profile.trust_score),
                "reliability": float(user_profile.reliability),
                "preferences": {
                    k: list(v) for k, v in user_profile.preferences.items()
                },
            },
            "candidate_books": [
                {
                    "title": book.title,
                    "author": book.metadata.get("author"),
                    "genre": book.facets.get("genre"),
                    "valuation": float(book.valuation),
                }
                for book in candidate_books
            ],
            "reading_history": reading_history,
        },
        "output": {
            "recommended_books": trajectory.recommended_books,
            "confidence_score": float(trajectory.confidence_score),
            "conversation": [
                {
                    "turn": i + 1,
                    "speaker": turn.speaker,
                    "reasoning": turn.reasoning,
                    "message": turn.message,
                }
                for i, turn in enumerate(trajectory.conversation)
            ],
            "final_recommendation": trajectory.final_recommendation,
        },
        "frontend_format": android_format,
    }

    return example_data


def test_example_2_casual_reader():
    """Example 2: Casual reader with diverse interests."""
    print("\n" + "=" * 70)
    print("Example 2: Casual Reader with Diverse Interests")
    print("=" * 70)

    # Frontend user data (from Android app)
    frontend_data = {
        "username": "bookworm_jane",
        "bio": "Love reading all kinds of books!",
        "profileUrl": "https://example.com/profile.jpg",
        "reviewCount": 8,
        "followerCount": 25,
        "followingCount": 30,
        "favoriteGenres": ["Fiction", "Romance", "Self-Help"],
        "preferences": {
            "tradeLocation1": "서울시 강남구",
            "tradeLocation2": "분당구 정자동",
            "tradeSpot1": "강남역 10번 출구",
            "tradeSpot2": "정자역 카페",
            "favBook": "The Alchemist",
            "favBookNote": "Inspiring and thought-provoking",
            "favAuthor": "Paulo Coelho",
            "favAuthorNote": "Philosophical and deep",
            "readingHabit": "I read mostly in the evening before bed, helps me relax",
        },
    }

    # Transform from frontend format
    user_profile = FrontendDataAdapter.transform_user_profile(
        frontend_data, user_id="user_202"
    )

    # Candidate books
    candidate_books = [
        Item(
            item_id="book_201",
            owner_id="owner_301",
            title="The Notebook",
            valuation=0.75,
            facets={
                "author": "Nicholas Sparks",
                "genre": "romance",
                "condition": "good",
            },
            metadata={"author": "Nicholas Sparks", "year": "1996"},
        ),
        Item(
            item_id="book_202",
            owner_id="owner_302",
            title="Atomic Habits",
            valuation=0.85,
            facets={
                "author": "James Clear",
                "genre": "self-help",
                "condition": "like_new",
            },
            metadata={"author": "James Clear", "year": "2018"},
        ),
    ]

    reading_history = ["The Alchemist", "Eat Pray Love", "The Secret"]

    # Generate reasoning
    generator = ReasoningGenerator()
    trajectory = generator.generate_book_recommendation_reasoning(
        user_profile=user_profile,
        candidate_books=candidate_books,
        user_reading_history=reading_history,
    )

    # Format for frontend
    formatted = ConversationFormatter.format_reasoning_trajectory(trajectory)

    # Prepare YAML output
    example_data = {
        "example_id": "example_2_casual_reader",
        "description": "Casual reader with diverse interests from frontend",
        "input": {
            "user_profile": {
                "user_id": user_profile.user_id,
                "display_name": user_profile.display_name,
                "trust_score": float(user_profile.trust_score),
                "preferences": {
                    k: list(v) for k, v in user_profile.preferences.items()
                },
            },
            "candidate_books": [
                {
                    "title": book.title,
                    "author": book.metadata.get("author"),
                    "genre": book.facets.get("genre"),
                }
                for book in candidate_books
            ],
            "reading_history": reading_history,
        },
        "output": {
            "recommended_books": trajectory.recommended_books,
            "confidence_score": float(trajectory.confidence_score),
            "conversation": [
                {
                    "turn": i + 1,
                    "speaker": turn.speaker,
                    "message": turn.message,
                }
                for i, turn in enumerate(trajectory.conversation)
            ],
            "final_recommendation": trajectory.final_recommendation,
        },
    }

    return example_data


def test_example_3_barter_negotiation():
    """Example 3: Barter negotiation between two users."""
    print("\n" + "=" * 70)
    print("Example 3: Barter Negotiation")
    print("=" * 70)

    from agents.negotiation import NegotiationMediator
    from data.entities import BarterContext
    from graph.candidate import BarterCandidate, ParticipantOffer

    # Create users
    user1 = UserProfile(
        user_id="user_301",
        display_name="Alice_BookCollector",
        trust_score=0.88,
        reliability=0.92,
        preferences={"genres": ["mystery", "thriller"]},
    )

    user2 = UserProfile(
        user_id="user_302",
        display_name="Bob_SciFiFan",
        trust_score=0.82,
        reliability=0.85,
        preferences={"genres": ["sci-fi", "fantasy"]},
    )

    # Create books
    book1 = Item(
        item_id="book_301",
        owner_id="user_301",
        title="The Da Vinci Code",
        valuation=0.90,
        facets={"genre": "mystery", "condition": "good"},
        metadata={"author": "Dan Brown"},
    )

    book2 = Item(
        item_id="book_302",
        owner_id="user_302",
        title="Dune",
        valuation=0.88,
        facets={"genre": "sci-fi", "condition": "like_new"},
        metadata={"author": "Frank Herbert"},
    )

    # Create context
    context = BarterContext(
        items={"book_301": book1, "book_302": book2},
        profiles={"user_301": user1, "user_302": user2},
        requests=[],
        distance_matrix={("user_301", "user_302"): 5.2},
    )

    # Create candidate
    candidate = BarterCandidate(
        participants=[
            ParticipantOffer(
                user_id="user_301",
                give_items=[book1],
                receive_items=[book2],
            ),
            ParticipantOffer(
                user_id="user_302",
                give_items=[book2],
                receive_items=[book1],
            ),
        ],
        metadata={"swap_type": "two_way"},
    )

    # Mediate with LLM
    mediator = NegotiationMediator(use_llm=True)
    outcome = mediator.mediate(candidate, context, fairness=0.87)

    # Prepare YAML output
    example_data = {
        "example_id": "example_3_barter_negotiation",
        "description": "Two-way barter negotiation with LLM mediation",
        "input": {
            "participants": [
                {
                    "user_id": user1.user_id,
                    "display_name": user1.display_name,
                    "offering": book1.title,
                    "receiving": book2.title,
                },
                {
                    "user_id": user2.user_id,
                    "display_name": user2.display_name,
                    "offering": book2.title,
                    "receiving": book1.title,
                },
            ],
            "distance_km": 5.2,
            "fairness_score": 0.87,
        },
        "output": {
            "match_score": float(outcome.match_score),
            "rationale": outcome.rationale,
            "trust_warnings": outcome.trust_warnings,
            "conversation": outcome.conversation_history or [],
        },
    }

    return example_data


def main():
    """Run all tests and save examples."""
    setup_environment()

    examples_dir = Path(__file__).parent.parent / "examples"
    examples_dir.mkdir(exist_ok=True)

    print("\n" + "=" * 70)
    print("Testing LLM Integration with Local Model")
    print("Saving Examples as YAML Files")
    print("=" * 70)

    # Run examples
    try:
        example1 = test_example_1_mystery_lover()
        save_yaml(example1, "example_1_mystery_lover.yaml", examples_dir)
    except Exception as e:
        print(f"❌ Example 1 failed: {e}")

    try:
        example2 = test_example_2_casual_reader()
        save_yaml(example2, "example_2_casual_reader.yaml", examples_dir)
    except Exception as e:
        print(f"❌ Example 2 failed: {e}")

    try:
        example3 = test_example_3_barter_negotiation()
        save_yaml(example3, "example_3_barter_negotiation.yaml", examples_dir)
    except Exception as e:
        print(f"❌ Example 3 failed: {e}")

    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print(f"📁 Examples saved in: {examples_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()

