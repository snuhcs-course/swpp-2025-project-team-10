"""Tests for LLM integration and reasoning trajectory generation.

Note: These tests use mocks to avoid actual model inference,
making them suitable for CI/CD environments like GitHub Actions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from adapters.backend_adapter import BackendDataAdapter
from data.entities import Item, UserProfile
from llm.client import LLMClient, Message
from llm.config import LLMConfig
from llm.reasoning import ReasoningGenerator


class TestLLMClient:
    """Test LLM client functionality (with mocks)."""

    @patch('llm.client.LLMClient._init_local_model')
    @patch('llm.client.LLMClient._init_openai_client')
    def test_client_initialization_local(self, mock_openai, mock_local):
        """Test LLM client initializes with local model."""
        config = LLMConfig(use_local_model=True)
        client = LLMClient(config)

        assert client.config.use_local_model is True
        mock_local.assert_called_once()

    @patch('llm.client.LLMClient._init_openai_client')
    def test_client_initialization_openai(self, mock_openai):
        """Test LLM client initializes with OpenAI."""
        config = LLMConfig(
            use_local_model=False, openai_api_key="test_key"
        )
        client = LLMClient(config)

        assert client is not None
        mock_openai.assert_called_once()

    @patch('llm.client.LLMClient._generate_local')
    @patch('llm.client.LLMClient._init_local_model')
    def test_generate_with_messages(self, mock_init, mock_generate):
        """Test generating response with messages."""
        mock_generate.return_value = "This is a test response."

        config = LLMConfig(use_local_model=True)
        client = LLMClient(config)
        client.model_type = "local"  # Set model_type since we mocked init

        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Hello!"),
        ]

        response = client.generate(messages)

        assert isinstance(response, str)
        assert len(response) > 0
        assert response == "This is a test response."
        mock_generate.assert_called_once()

    @patch('llm.client.LLMClient._generate_local')
    @patch('llm.client.LLMClient._init_local_model')
    def test_chat_interface(self, mock_init, mock_generate):
        """Test simple chat interface."""
        mock_generate.return_value = "I recommend 'The Da Vinci Code'."

        config = LLMConfig(use_local_model=True)
        client = LLMClient(config)
        client.model_type = "local"  # Set model_type since we mocked init

        response = client.chat(
            system_prompt="You are a book expert.",
            user_message="Recommend a mystery book.",
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Da Vinci Code" in response


class TestReasoningGenerator:
    """Test reasoning trajectory generation (with mocks)."""

    @pytest.fixture
    def sample_user_profile(self):
        """Create a sample user profile."""
        return UserProfile(
            user_id="user_123",
            display_name="John Doe",
            trust_score=0.85,
            reliability=0.9,
            preferences={
                "genres": ["mystery", "thriller"],
                "authors": ["Agatha Christie"],
                "moods": ["suspenseful"],
            },
        )

    @pytest.fixture
    def sample_books(self):
        """Create sample book items."""
        return [
            Item(
                item_id="book_1",
                owner_id="owner_1",
                title="Murder on the Orient Express",
                valuation=0.9,
                facets={"author": "Agatha Christie", "genre": "mystery"},
                metadata={"author": "Agatha Christie"},
            ),
            Item(
                item_id="book_2",
                owner_id="owner_2",
                title="The Girl with the Dragon Tattoo",
                valuation=0.85,
                facets={"author": "Stieg Larsson", "genre": "thriller"},
                metadata={"author": "Stieg Larsson"},
            ),
        ]

    @patch('llm.reasoning.LLMClient')
    def test_reasoning_generator_initialization(self, mock_client_class):
        """Test reasoning generator initializes correctly."""
        mock_client_class.return_value = Mock()

        generator = ReasoningGenerator()

        assert generator.recommender_client is not None
        assert generator.critic_client is not None
        assert generator.max_turns >= 3

    @patch('llm.reasoning.LLMClient')
    def test_generate_book_recommendation_reasoning(
        self, mock_client_class, sample_user_profile, sample_books
    ):
        """Test generating reasoning trajectory."""
        # Mock LLM responses
        mock_recommender = Mock()
        mock_critic = Mock()

        # Set up chat method to return strings (DM-style, natural conversation)
        mock_recommender.chat.side_effect = [
            "오리엔트 특급 살인 추천해! 미스터리 장르 좋아하시니까 딱일 것 같아. 반전도 엄청나고 추리 과정이 재밌거든.",  # Initial
            "그럼 용의자 X의 헌신은 어때? 히가시노 게이고 작품이라 백야행 좋아했으면 마음에 들 거야.",  # Refine 1
            "두 책 다 추천할게. 둘 다 반전이 좋고 몰입감이 엄청나거든.",  # Refine 2
            "최종적으로 오리엔트 특급 살인과 용의자 X의 헌신 추천할게. 미스터리 장르 선호도에 완벽하게 맞아.",  # Final
        ]
        mock_critic.chat.side_effect = [
            "오리엔트 특급 살인 좋긴 한데, 다른 책도 고려해봤어? 히가시노 게이고 작품도 좋을 것 같은데.",  # Question 1
            "좋네. 두 작가 다 추리소설 대가니까 만족할 것 같아.",  # Question 2
        ]

        # Make the class return different instances for recommender and critic
        mock_client_class.side_effect = [mock_recommender, mock_critic]

        generator = ReasoningGenerator()

        trajectory = generator.generate_book_recommendation_reasoning(
            user_profile=sample_user_profile,
            candidate_books=sample_books,
            user_reading_history=["The Da Vinci Code", "Gone Girl"],
        )

        # Check trajectory structure
        assert trajectory.user_id == "user_123"
        assert len(trajectory.recommended_books) == 2
        assert len(trajectory.conversation) >= 3
        assert trajectory.final_recommendation is not None
        assert isinstance(trajectory.final_recommendation, str)
        assert 0.0 <= trajectory.confidence_score <= 1.0

        # Check conversation structure
        for turn in trajectory.conversation:
            assert turn.speaker in ["recommender", "critic"]
            assert isinstance(turn.message, str)
            assert len(turn.message) > 0

    @patch('llm.reasoning.LLMClient')
    def test_prepare_context(self, mock_client_class, sample_user_profile, sample_books):
        """Test context preparation for LLM."""
        mock_client_class.return_value = Mock()
        generator = ReasoningGenerator()

        context = generator._prepare_context(
            sample_user_profile, sample_books, ["Book 1", "Book 2"]
        )

        assert "John Doe" in context
        assert "mystery" in context
        assert "Murder on the Orient Express" in context

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        from llm.client import ConversationTurn
        from llm.reasoning import ReasoningGenerator

        # Create generator without mocking for this simple test
        generator = ReasoningGenerator.__new__(ReasoningGenerator)
        generator.max_turns = 3

        # Mock conversation
        conversation = [
            ConversationTurn(
                speaker="recommender", message="Test", reasoning="Test"
            ),
            ConversationTurn(
                speaker="critic", message="Test", reasoning="Test"
            ),
            ConversationTurn(
                speaker="recommender", message="Test", reasoning="Test"
            ),
        ]

        confidence = generator._calculate_confidence(conversation)

        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.6  # Should have reasonable confidence


class TestBackendDataAdapter:
    """Test backend data adapter."""

    def test_transform_user_profile(self):
        """Test transforming backend user data to UserProfile."""
        user_data = {
            "id": 1,
            "username": "john_doe",
            "location": "Seoul, Gangnam-gu",
            "reputation_score": 85,
            "successful_trades": 12,
        }

        user_taste = {
            "favorite_genres": ["fiction", "mystery"],
            "favorite_authors": ["Agatha Christie"],
            "preferred_moods": ["suspenseful"],
        }

        profile = BackendDataAdapter.transform_user_profile(
            user_data, user_taste
        )

        assert profile.user_id == "1"
        assert profile.display_name == "john_doe"
        assert 0.0 <= profile.trust_score <= 1.0
        assert "genres" in profile.preferences
        assert "fiction" in profile.preferences["genres"]

    def test_transform_book_to_item(self):
        """Test transforming backend book data to Item."""
        book_data = {
            "id": 1,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "condition": "good",
            "owner": 5,
        }

        item = BackendDataAdapter.transform_book_to_item(book_data)

        assert item.item_id == "1"
        assert item.title == "The Great Gatsby"
        assert item.owner_id == "5"
        assert "author" in item.facets
        assert item.facets["author"] == "F. Scott Fitzgerald"
        assert 0.0 <= item.valuation <= 1.0

    def test_build_barter_context(self):
        """Test building complete barter context."""
        users = [
            {
                "id": 1,
                "username": "user1",
                "reputation_score": 80,
                "successful_trades": 10,
                "user_taste": {"favorite_genres": ["fiction"]},
                "user_preferences": {"max_barter_distance": 50},
            }
        ]

        books = [
            {
                "id": 1,
                "title": "Book 1",
                "author": "Author 1",
                "condition": "good",
                "owner": 1,
            }
        ]

        context = BackendDataAdapter.build_barter_context(users, books)

        assert len(context.profiles) == 1
        assert len(context.items) == 1
        assert "1" in context.profiles
        assert "1" in context.items


class TestConversationFormatter:
    """Test conversation formatting for frontend."""

    def test_format_reasoning_trajectory(self):
        """Test formatting reasoning trajectory."""
        from llm.client import ConversationTurn
        from llm.reasoning import ReasoningTrajectory
        from visualization.conversation_formatter import (
            ConversationFormatter,
        )

        trajectory = ReasoningTrajectory(
            user_id="user_123",
            recommended_books=["Book 1", "Book 2"],
            conversation=[
                ConversationTurn(
                    speaker="recommender",
                    message="I recommend these books...",
                    reasoning="Based on preferences",
                ),
                ConversationTurn(
                    speaker="critic",
                    message="Let me evaluate...",
                    reasoning="Checking alignment",
                ),
            ],
            final_recommendation="Final recommendation text",
            confidence_score=0.85,
        )

        formatted = ConversationFormatter.format_reasoning_trajectory(
            trajectory
        )

        assert formatted.user_id == "user_123"
        assert len(formatted.messages) == 2
        assert formatted.confidence_score == 0.85

        # Check message structure
        assert formatted.messages[0].speaker_role == "recommender"
        assert formatted.messages[1].speaker_role == "critic"

    def test_format_for_android(self):
        """Test Android-specific formatting."""
        from llm.client import ConversationTurn
        from llm.reasoning import ReasoningTrajectory
        from visualization.conversation_formatter import (
            ConversationFormatter,
        )

        trajectory = ReasoningTrajectory(
            user_id="user_123",
            recommended_books=["Book 1"],
            conversation=[
                ConversationTurn(
                    speaker="recommender",
                    message="Test",
                    reasoning="Test",
                )
            ],
            final_recommendation="Final",
            confidence_score=0.9,
        )

        formatted = ConversationFormatter.format_reasoning_trajectory(
            trajectory
        )
        android_format = ConversationFormatter.format_for_android(formatted)

        assert "conversationId" in android_format
        assert "messages" in android_format
        assert "confidenceLevel" in android_format
        assert android_format["confidenceLevel"] == "HIGH"

