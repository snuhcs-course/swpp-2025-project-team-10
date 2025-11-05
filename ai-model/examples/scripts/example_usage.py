"""
Example usage of the AI model with LLM integration.

This script demonstrates how to:
1. Load user data from backend format
2. Generate book recommendations with reasoning trajectory
3. Format the conversation for frontend display
"""

import json
import os
from pathlib import Path

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from adapters.backend_adapter import BackendDataAdapter
from data.entities import Item, UserProfile
from llm.reasoning import ReasoningGenerator
from visualization.conversation_formatter import (
    ConversationFormatter,
)


def example_book_recommendation():
    """Example: Generate book recommendation with reasoning trajectory."""
    print("=" * 60)
    print("Example: Book Recommendation with LLM Reasoning")
    print("=" * 60)

    # Sample user data (as would come from Django backend)
    user_data = {
        "id": 1,
        "username": "book_lover_42",
        "location": "Seoul, Gangnam-gu",
        "reputation_score": 85,
        "successful_trades": 12,
    }

    user_taste = {
        "favorite_genres": ["mystery", "thriller", "fiction"],
        "favorite_authors": ["Agatha Christie", "Dan Brown"],
        "favorite_books": ["Murder on the Orient Express"],
        "preferred_moods": ["suspenseful", "engaging"],
        "reading_purposes": ["entertainment", "relaxation"],
    }

    user_preferences = {"max_barter_distance": 50}

    # Transform to AI model format
    user_profile = BackendDataAdapter.transform_user_profile(
        user_data, user_taste, user_preferences
    )

    print(f"\nUser Profile: {user_profile.display_name}")
    print(f"Trust Score: {user_profile.trust_score:.2f}")
    print(f"Preferences: {user_profile.preferences}")

    # Sample candidate books
    candidate_books = [
        Item(
            item_id="book_1",
            owner_id="owner_1",
            title="The Da Vinci Code",
            valuation=0.9,
            facets={"author": "Dan Brown", "genre": "mystery"},
            metadata={"author": "Dan Brown", "year": "2003"},
        ),
        Item(
            item_id="book_2",
            owner_id="owner_2",
            title="Gone Girl",
            valuation=0.85,
            facets={"author": "Gillian Flynn", "genre": "thriller"},
            metadata={"author": "Gillian Flynn", "year": "2012"},
        ),
        Item(
            item_id="book_3",
            owner_id="owner_3",
            title="The Girl with the Dragon Tattoo",
            valuation=0.88,
            facets={"author": "Stieg Larsson", "genre": "thriller"},
            metadata={"author": "Stieg Larsson", "year": "2005"},
        ),
    ]

    # User's reading history
    reading_history = [
        "Murder on the Orient Express",
        "And Then There Were None",
        "The Hound of the Baskervilles",
    ]

    print("\n" + "-" * 60)
    print("Generating Reasoning Trajectory...")
    print("-" * 60)

    # Generate reasoning trajectory
    generator = ReasoningGenerator()
    trajectory = generator.generate_book_recommendation_reasoning(
        user_profile=user_profile,
        candidate_books=candidate_books,
        user_reading_history=reading_history,
    )

    print(f"\nRecommended Books: {trajectory.recommended_books}")
    print(f"Confidence Score: {trajectory.confidence_score:.2f}")

    print("\n" + "=" * 60)
    print("Conversation Between AI Agents:")
    print("=" * 60)

    for i, turn in enumerate(trajectory.conversation, 1):
        speaker_label = (
            "📚 BookBot (Recommender)"
            if turn.speaker == "recommender"
            else "🔍 CriticBot (Evaluator)"
        )
        print(f"\n[Turn {i}] {speaker_label}")
        print(f"Reasoning: {turn.reasoning}")
        print(f"Message: {turn.message[:200]}...")

    print("\n" + "=" * 60)
    print("Final Recommendation:")
    print("=" * 60)
    print(trajectory.final_recommendation)

    # Format for frontend
    print("\n" + "-" * 60)
    print("Formatting for Frontend Display...")
    print("-" * 60)

    formatted = ConversationFormatter.format_reasoning_trajectory(trajectory)
    android_format = ConversationFormatter.format_for_android(formatted)

    print(f"\nConversation ID: {android_format['conversationId']}")
    print(f"Number of Messages: {len(android_format['messages'])}")
    print(f"Confidence Level: {android_format['confidenceLevel']}")

    # Save to JSON file
    output_file = Path(__file__).parent / "example_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(android_format, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Full output saved to: {output_file}")

    return trajectory, formatted


def example_barter_negotiation():
    """Example: Barter negotiation with LLM conversation."""
    print("\n\n" + "=" * 60)
    print("Example: Barter Negotiation with LLM")
    print("=" * 60)

    from agents.negotiation import NegotiationMediator
    from data.entities import BarterContext
    from graph.candidate import BarterCandidate, ParticipantOffer

    # Create sample context
    user1 = UserProfile(
        user_id="user_1",
        display_name="Alice",
        trust_score=0.85,
        reliability=0.9,
        preferences={"genres": ["mystery", "thriller"]},
    )

    user2 = UserProfile(
        user_id="user_2",
        display_name="Bob",
        trust_score=0.78,
        reliability=0.85,
        preferences={"genres": ["fiction", "sci-fi"]},
    )

    book1 = Item(
        item_id="book_1",
        owner_id="user_1",
        title="The Da Vinci Code",
        valuation=0.9,
        facets={"genre": "mystery"},
    )

    book2 = Item(
        item_id="book_2",
        owner_id="user_2",
        title="Dune",
        valuation=0.88,
        facets={"genre": "sci-fi"},
    )

    context = BarterContext(
        items={"book_1": book1, "book_2": book2},
        profiles={"user_1": user1, "user_2": user2},
        requests=[],
    )

    # Create barter candidate
    candidate = BarterCandidate(
        participants=[
            ParticipantOffer(
                user_id="user_1",
                give_items=[book1],
                receive_items=[book2],
                given_value=0.9,
                received_value=0.88,
            ),
            ParticipantOffer(
                user_id="user_2",
                give_items=[book2],
                receive_items=[book1],
                given_value=0.88,
                received_value=0.9,
            ),
        ],
        swap_type="two_way",
    )

    # Mediate with LLM (set use_llm=True to enable)
    mediator = NegotiationMediator(use_llm=True)
    outcome = mediator.mediate(candidate, context, fairness=0.85)

    print(f"\nMatch Score: {outcome.match_score:.2f}")
    print(f"Rationale: {outcome.rationale}")

    if outcome.conversation_history:
        print("\n" + "=" * 60)
        print("Negotiation Conversation:")
        print("=" * 60)

        for i, turn in enumerate(outcome.conversation_history, 1):
            speaker = turn.get("speaker", "unknown")
            message = turn.get("message", "")
            print(f"\n[Turn {i}] {speaker.upper()}")
            print(message[:200] + "...")

    print("\n✅ Negotiation complete!")


if __name__ == "__main__":
    # Set environment variable to use local model
    os.environ["USE_LOCAL_MODEL"] = "true"

    # Run examples
    trajectory, formatted = example_book_recommendation()

    # Uncomment to run barter negotiation example
    # example_barter_negotiation()

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)

