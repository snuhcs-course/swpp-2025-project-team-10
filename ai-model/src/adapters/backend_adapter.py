"""Adapter for transforming Django backend data to AI model entities."""

import logging
from typing import Any

from data.entities import (
    BarterContext,
    Item,
    TradeRequest,
    UserProfile,
)

logger = logging.getLogger(__name__)


class BackendDataAdapter:
    """
    Adapter to transform Django backend data to AI model entities.

    Expected backend data format (from Django REST API):
    {
        "user": {
            "id": 1,
            "username": "john_doe",
            "location": "Seoul, Gangnam-gu",
            "reputation_score": 85,
            "successful_trades": 12,
            ...
        },
        "user_taste": {
            "favorite_genres": ["fiction", "mystery"],
            "favorite_authors": ["Agatha Christie", "Dan Brown"],
            "favorite_books": ["Murder on the Orient Express"],
            "preferred_length": "medium",
            "preferred_moods": ["suspenseful", "engaging"],
            "reading_purposes": ["entertainment", "relaxation"]
        },
        "user_preferences": {
            "max_barter_distance": 50,
            "preferred_meeting_locations": "Gangnam Station Exit 10, ..."
        },
        "books": [
            {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "...",
                "condition": "good",
                "owner": 1
            }
        ],
        "barter_requests": [
            {
                "id": 1,
                "requester": 1,
                "offered_books": [1, 2],
                "requested_books": [3],
                "status": "pending"
            }
        ]
    }
    """

    @staticmethod
    def transform_user_profile(
        user_data: dict[str, Any],
        user_taste: dict[str, Any] | None = None,
        user_preferences: dict[str, Any] | None = None,
    ) -> UserProfile:
        """
        Transform backend user data to UserProfile entity.

        Args:
            user_data: User model data from Django
            user_taste: UserTaste model data
            user_preferences: UserPreferences model data

        Returns:
            UserProfile entity
        """
        # Calculate trust score and reliability
        reputation = user_data.get("reputation_score", 0)
        successful_trades = user_data.get("successful_trades", 0)

        # Normalize to [0, 1] range
        trust_score = min(reputation / 100.0, 1.0)
        reliability = min(successful_trades / 20.0, 1.0)

        # Build preferences dictionary
        preferences: dict[str, list[str]] = {}

        if user_taste:
            # Map Django UserTaste fields to AI model preferences
            if user_taste.get("favorite_genres"):
                preferences["genres"] = user_taste["favorite_genres"]

            if user_taste.get("favorite_authors"):
                preferences["authors"] = user_taste["favorite_authors"]

            if user_taste.get("preferred_moods"):
                preferences["moods"] = user_taste["preferred_moods"]

            if user_taste.get("reading_purposes"):
                preferences["purposes"] = user_taste["reading_purposes"]

            if user_taste.get("preferred_length"):
                preferences["length"] = [user_taste["preferred_length"]]

        # Extract exclusion rules (if any)
        exclusion_rules: list[str] = []
        risk_notes: list[str] = []

        # Add location-based constraints
        if user_preferences:
            max_distance = user_preferences.get("max_barter_distance", 50)
            exclusion_rules.append(f"max_distance:{max_distance}km")

        return UserProfile(
            user_id=str(user_data["id"]),
            display_name=user_data.get("username", "Unknown"),
            trust_score=trust_score,
            reliability=reliability,
            preferences=preferences,
            exclusion_rules=exclusion_rules,
            risk_notes=risk_notes,
        )

    @staticmethod
    def transform_book_to_item(book_data: dict[str, Any]) -> Item:
        """
        Transform backend book data to Item entity.

        Args:
            book_data: Book model data from Django

        Returns:
            Item entity
        """
        # Build facets from book metadata
        facets: dict[str, str] = {}

        if book_data.get("author"):
            facets["author"] = book_data["author"]

        if book_data.get("condition"):
            facets["condition"] = book_data["condition"]

        if book_data.get("genre"):
            facets["genre"] = book_data["genre"]

        if book_data.get("publication_year"):
            facets["year"] = str(book_data["publication_year"])

        # Estimate valuation based on condition
        condition_values = {
            "new": 1.0,
            "like_new": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3,
        }
        condition = book_data.get("condition", "good")
        base_value = condition_values.get(condition, 0.7)

        return Item(
            item_id=str(book_data["id"]),
            owner_id=str(book_data.get("owner", "")),
            title=book_data.get("title", "Unknown"),
            valuation=base_value,
            facets=facets,
            metadata=book_data,  # Store full data for reference
        )

    @staticmethod
    def transform_barter_request(
        request_data: dict[str, Any]
    ) -> TradeRequest:
        """
        Transform backend barter request to TradeRequest entity.

        Args:
            request_data: BarterRequest model data from Django

        Returns:
            TradeRequest entity
        """
        # Extract desired item IDs
        desired_items = [
            str(book_id) for book_id in request_data.get("requested_books", [])
        ]

        # Extract facet preferences (if available)
        desired_facets: dict[str, list[str]] = {}

        # Map urgency
        urgency_map = {
            "urgent": "urgent",
            "flexible": "flexible",
            "specific_dates": "specific_dates",
        }
        urgency = urgency_map.get(
            request_data.get("urgency", "flexible"), "flexible"
        )

        # Logistic preferences
        meeting_type = request_data.get("preferred_meeting_type", "")
        meeting_location = request_data.get(
            "proposed_meeting_location", ""
        )
        logistics = f"{meeting_type}:{meeting_location}" if meeting_type else None

        return TradeRequest(
            user_id=str(request_data.get("requester", "")),
            desired_item_ids=desired_items,
            desired_facets=desired_facets,
            urgency=urgency,
            logistic_preferences=logistics,
        )

    @staticmethod
    def build_barter_context(
        users: list[dict[str, Any]],
        books: list[dict[str, Any]],
        barter_requests: list[dict[str, Any]] | None = None,
        distance_matrix: dict[tuple[str, str], float] | None = None,
    ) -> BarterContext:
        """
        Build complete BarterContext from backend data.

        Args:
            users: List of user data with taste and preferences
            books: List of book data
            barter_requests: Optional list of barter requests
            distance_matrix: Optional pre-computed distance matrix

        Returns:
            BarterContext ready for AI processing
        """
        # Transform users
        profiles = {}
        for user_data in users:
            user_id = str(user_data["id"])
            profile = BackendDataAdapter.transform_user_profile(
                user_data,
                user_data.get("user_taste"),
                user_data.get("user_preferences"),
            )
            profiles[user_id] = profile

        # Transform books
        items = {}
        for book_data in books:
            item = BackendDataAdapter.transform_book_to_item(book_data)
            items[item.item_id] = item

        # Transform barter requests
        requests = []
        if barter_requests:
            for req_data in barter_requests:
                request = BackendDataAdapter.transform_barter_request(
                    req_data
                )
                requests.append(request)

        return BarterContext(
            items=items,
            profiles=profiles,
            requests=requests,
            distance_matrix=distance_matrix or {},
            trust_threshold=0.4,
        )

