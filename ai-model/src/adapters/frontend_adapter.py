"""Adapter for transforming Android frontend data to AI model entities."""

import logging
from typing import Any

from data.entities import UserProfile

logger = logging.getLogger(__name__)


class FrontendDataAdapter:
    """
    Adapter to transform Android frontend data to AI model entities.

    Expected frontend data format (from Kotlin UserProfile):
    {
        "username": "john_doe",
        "bio": "Book lover and avid reader",
        "profileUrl": "https://...",
        "reviewCount": 15,
        "followerCount": 42,
        "followingCount": 38,
        "favoriteGenres": ["Fiction", "Mystery", "Thriller"],
        "preferences": {
            "tradeLocation1": "서울시 강남구",
            "tradeLocation2": "분당구 정자동",
            "tradeSpot1": "강남역 10번 출구",
            "tradeSpot2": "정자역 카페",
            "favBook": "Murder on the Orient Express",
            "favBookNote": "Classic mystery with great plot twists",
            "favAuthor": "Agatha Christie",
            "favAuthorNote": "Master of mystery writing",
            "readingHabit": "I read mostly in the evening..."
        }
    }
    """

    @staticmethod
    def transform_user_profile(
        frontend_data: dict[str, Any], user_id: str | None = None
    ) -> UserProfile:
        """
        Transform frontend UserProfile to AI model UserProfile.

        Args:
            frontend_data: UserProfile data from Android app
            user_id: Optional user ID (if not in frontend data)

        Returns:
            UserProfile entity for AI model
        """
        # Extract basic info
        username = frontend_data.get("username", "Unknown")
        user_id = user_id or username

        # Build preferences from frontend data
        preferences: dict[str, list[str]] = {}

        # Favorite genres
        if frontend_data.get("favoriteGenres"):
            preferences["genres"] = frontend_data["favoriteGenres"]

        # Extract from preferences object
        prefs = frontend_data.get("preferences", {})

        # Favorite authors
        if prefs.get("favAuthor"):
            preferences["authors"] = [prefs["favAuthor"]]

        # Favorite books
        if prefs.get("favBook"):
            preferences["books"] = [prefs["favBook"]]

        # Parse reading habit for additional preferences
        reading_habit = prefs.get("readingHabit", "")
        if reading_habit:
            # Simple keyword extraction (can be enhanced with NLP)
            habit_keywords = FrontendDataAdapter._extract_habit_keywords(
                reading_habit
            )
            if habit_keywords:
                preferences["reading_times"] = habit_keywords

        # Calculate trust/reliability from social metrics
        review_count = frontend_data.get("reviewCount", 0)
        follower_count = frontend_data.get("followerCount", 0)

        # Simple heuristic: more reviews and followers = higher trust
        trust_score = min((review_count * 0.02) + (follower_count * 0.01), 1.0)
        trust_score = max(trust_score, 0.3)  # Minimum baseline

        reliability = min(review_count / 20.0, 1.0)
        reliability = max(reliability, 0.3)  # Minimum baseline

        # Extract location-based exclusion rules
        exclusion_rules: list[str] = []
        if prefs.get("tradeLocation1"):
            exclusion_rules.append(
                f"preferred_location:{prefs['tradeLocation1']}"
            )
        if prefs.get("tradeLocation2"):
            exclusion_rules.append(
                f"preferred_location:{prefs['tradeLocation2']}"
            )

        return UserProfile(
            user_id=user_id,
            display_name=username,
            trust_score=trust_score,
            reliability=reliability,
            preferences=preferences,
            exclusion_rules=exclusion_rules,
            risk_notes=[],
        )

    @staticmethod
    def _extract_habit_keywords(reading_habit: str) -> list[str]:
        """
        Extract reading time keywords from habit description.

        Args:
            reading_habit: Free-text reading habit description

        Returns:
            List of extracted keywords
        """
        keywords = []
        habit_lower = reading_habit.lower()

        # Time-based keywords
        time_keywords = {
            "morning": ["morning", "breakfast", "dawn"],
            "afternoon": ["afternoon", "lunch"],
            "evening": ["evening", "dinner", "night"],
            "weekend": ["weekend", "saturday", "sunday"],
            "commute": ["commute", "train", "bus", "subway"],
        }

        for category, terms in time_keywords.items():
            if any(term in habit_lower for term in terms):
                keywords.append(category)

        return keywords

    @staticmethod
    def extract_location_preferences(
        frontend_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Extract location and meeting spot preferences.

        Args:
            frontend_data: UserProfile data from Android app

        Returns:
            Dictionary with location preferences
        """
        prefs = frontend_data.get("preferences", {})

        return {
            "locations": [
                prefs.get("tradeLocation1"),
                prefs.get("tradeLocation2"),
            ],
            "meeting_spots": [
                prefs.get("tradeSpot1"),
                prefs.get("tradeSpot2"),
            ],
            "max_distance_km": 50,  # Default, should come from backend
        }

