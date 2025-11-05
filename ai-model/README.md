# AI Model - Book Recommendation & Barter System

This directory contains the AI model implementation for the book bartering social network, featuring LLM-based reasoning trajectories and intelligent barter recommendations.

## 🎯 Features

### 1. **LLM-Based Reasoning Trajectories** 🇰🇷
- Two-LLM conversation system simulating expert discussion
- **BookBot (Recommender)**: Analyzes user preferences and proposes recommendations
- **CriticBot (Evaluator)**: Questions and validates recommendations
- Transparent reasoning process displayed as chat conversation
- **Korean language support** with compact 2-3 sentence responses

### 2. **Book Recommendation Engine**
- Analyzes user preferences, reading history, and taste profiles
- Generates personalized book recommendations
- Provides confidence scores and detailed explanations

### 3. **Barter Negotiation System**
- Multi-objective ranking (utility, fairness, preference, logistics)
- LLM-mediated negotiation between users
- Trust and risk assessment

### 4. **Data Adapters**
- Backend adapter: Django models → AI entities
- Frontend adapter: Kotlin/Android data → AI entities
- Seamless integration with existing systems

## 📁 Project Structure

```
ai-model/
├── src/                       # Main source code (flattened structure)
│   ├── llm/                    # LLM integration
│   │   ├── client.py          # Unified LLM client (OpenAI + local)
│   │   ├── config.py          # Configuration management
│   │   └── reasoning.py       # Two-LLM reasoning trajectory
│   ├── adapters/              # Data transformation
│   │   ├── backend_adapter.py # Django → AI entities
│   │   └── frontend_adapter.py# Kotlin → AI entities
│   ├── agents/                # Negotiation agents
│   │   └── negotiation.py     # LLM-based negotiation
│   ├── visualization/         # Frontend formatting
│   │   └── conversation_formatter.py
│   ├── data/                  # Core entities
│   │   └── entities.py
│   ├── graph/                 # Market graph & candidates
│   ├── models/                # Ranking models
│   └── pipeline/              # Recommendation pipeline
├── tests/                     # Unit tests (mocked, CI-friendly)
│   ├── test_llm_integration.py
│   ├── test_market_graph.py
│   └── test_recommender.py
├── examples/                  # Example scenarios and scripts
│   ├── README.md              # Examples documentation
│   ├── scenarios/             # Example YAML outputs
│   │   ├── example_1_mystery_lover.yaml
│   │   ├── example_2_casual_reader.yaml
│   │   └── example_3_barter_negotiation.yaml
│   └── scripts/               # Example and test scripts
│       ├── example_usage.py   # Complete usage examples
│       ├── manual_test_with_local_llm.py  # Manual testing with real model
│       └── test_real_model.py # Quick model verification
├── models/                    # Local LLM models
│   └── gemma3-4b-it/          # Gemma3 4B model
└── .env.pub                   # Environment template
```

## 🚀 Quick Start

### 1. Environment Setup

Copy `.env.pub` to `.env` and configure:

```bash
cp .env.pub .env
```

Edit `.env`:
```bash
# For production with OpenAI
USE_LOCAL_MODEL=false
OPENAI_API_KEY=your_api_key_here

# For development/testing with local model
USE_LOCAL_MODEL=true
LOCAL_MODEL_PATH=models/gemma3-4b-it
```

### 2. Install Dependencies

```bash
# Using pip
pip install openai pyyaml

# Or using uv (recommended)
uv pip install openai pyyaml
```

### 3. Run Examples

```bash
# Run example usage (instant, uses mocks)
python examples/scripts/example_usage.py

# Test with real local model (slow, requires model)
python examples/scripts/manual_test_with_local_llm.py

# Quick model verification
python examples/scripts/test_real_model.py
```

## 💡 Usage Examples

### Example 1: Book Recommendation with Reasoning

```python
from ai_model.adapters.backend_adapter import BackendDataAdapter
from ai_model.llm.reasoning import ReasoningGenerator
from ai_model.visualization.conversation_formatter import ConversationFormatter

# Transform user data from backend
user_profile = BackendDataAdapter.transform_user_profile(
    user_data, user_taste, user_preferences
)

# Generate reasoning trajectory
generator = ReasoningGenerator()
trajectory = generator.generate_book_recommendation_reasoning(
    user_profile=user_profile,
    candidate_books=candidate_books,
    user_reading_history=reading_history
)

# Format for frontend display
formatted = ConversationFormatter.format_reasoning_trajectory(trajectory)
android_format = ConversationFormatter.format_for_android(formatted)
```

### Example 2: Barter Negotiation

```python
from ai_model.agents.negotiation import NegotiationMediator

# Create negotiation mediator with LLM
mediator = NegotiationMediator(use_llm=True)

# Mediate barter
outcome = mediator.mediate(candidate, context, fairness=0.85)

# Access conversation history
for turn in outcome.conversation_history:
    print(f"{turn['speaker']}: {turn['message']}")
```

## 📊 Example Outputs

All example outputs are saved as YAML files in `examples/scenarios/`:

### Example 1: Mystery Lover
- **User**: Loves mystery and thriller books
- **Preferences**: Agatha Christie, Dan Brown, suspenseful stories
- **Output**: 3-turn conversation between BookBot and CriticBot
- **Confidence**: 0.90 (HIGH)

### Example 2: Casual Reader
- **User**: Diverse interests (Fiction, Romance, Self-Help)
- **Source**: Frontend (Android app) data
- **Output**: Personalized recommendations with reasoning

### Example 3: Barter Negotiation
- **Scenario**: Alice (mystery fan) ↔ Bob (sci-fi fan)
- **Books**: "The Da Vinci Code" ↔ "Dune"
- **Output**: LLM-mediated negotiation conversation

## 🔧 Configuration

### LLM Settings

```python
# In .env
REASONING_MAX_TURNS=3              # Conversation turns
OPENAI_TEMPERATURE=0.7             # Creativity level
OPENAI_MAX_TOKENS=2000             # Response length
```

### System Prompts

```python
REASONING_SYSTEM_PROMPT_RECOMMENDER="You are a book recommendation expert..."
REASONING_SYSTEM_PROMPT_CRITIC="You are a critical evaluator..."
```

## 🧪 Testing

### Unit Tests (CI-Friendly)

The unit tests use mocks and don't require actual model inference, making them suitable for GitHub Actions:

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_llm_integration.py -v
```

### Manual Testing with Real Model

For testing with actual model inference (requires local model):

```bash
# Quick test of model inference
python examples/scripts/test_real_model.py

# Generate example YAML files with real model
python examples/scripts/manual_test_with_local_llm.py

# Run example usage (with mocks)
python examples/scripts/example_usage.py
```

**Note**: Manual tests require the local model to be downloaded and placed in `models/gemma3-4b-it/`.

### Test Coverage

- ✅ LLM client initialization (OpenAI + local) - mocked
- ✅ Reasoning trajectory generation - mocked
- ✅ Data adapter transformations
- ✅ Conversation formatting
- ✅ Negotiation mediation - mocked
- ✅ Real model inference - manual tests only

## 📱 Frontend Integration

The conversation format is optimized for Android RecyclerView:

```json
{
  "conversationId": "conv_abc123",
  "messages": [
    {
      "id": "msg_1",
      "speaker": "BookBot",
      "speakerRole": "recommender",
      "message": "Based on your love for mystery...",
      "viewType": "MESSAGE_LEFT",
      "backgroundColor": "#E3F2FD",
      "avatarType": "ai_recommender"
    }
  ],
  "confidenceLevel": "HIGH"
}
```

## 🔄 Data Flow

```
Frontend (Kotlin) → Backend (Django) → AI Model
     ↓                    ↓                ↓
UserProfile.kt    →  User/UserTaste  →  UserProfile
                         models            entity
                            ↓
                     BackendDataAdapter
                            ↓
                    ReasoningGenerator
                            ↓
                   ConversationFormatter
                            ↓
                    Android JSON format
```

## 🎨 Conversation Visualization

The two-LLM conversation creates an engaging, transparent reasoning process:

```
[Turn 1] 📚 BookBot (Recommender)
"Based on your preference for mystery and thriller genres,
and your enjoyment of Agatha Christie's work, I recommend..."

[Turn 2] 🔍 CriticBot (Evaluator)
"Let me evaluate this recommendation. While the genre matches,
have we considered the user's preference for 'suspenseful' moods?"

[Turn 3] 📚 BookBot (Recommender)
"Good point! Refining my recommendation to emphasize
suspenseful elements..."
```

## 🚧 Current Status

- ✅ LLM client wrapper (OpenAI + local)
- ✅ Two-LLM reasoning trajectory
- ✅ Data adapters (backend + frontend)
- ✅ Conversation formatting
- ✅ Negotiation agents with LLM
- ✅ Example outputs (YAML)
- ✅ Real local model inference (transformers)
- ✅ Multi-device support (CUDA, MPS, CPU)
- 🔜 Backend API endpoints
- 🔜 Real-time recommendation service

## 📝 Notes

- **Real Model Inference**: Local model now uses actual transformers inference with Gemma3-4b-it.
- **Device Support**: Automatically detects and uses CUDA (NVIDIA), MPS (Apple Silicon), or CPU.
- **OpenAI API**: Set `USE_LOCAL_MODEL=false` and provide `OPENAI_API_KEY` for production.
- **Performance**: Local model inference is slower than API calls but provides full control and privacy.
- **Model Location**: Model is stored in `ai-model/models/gemma3-4b-it/`.

## 🤝 Contributing

When adding new features:
1. Update data entities in `data/entities.py`
2. Add adapters for new data sources
3. Create tests in `tests/`
4. Generate example outputs in `examples/scenarios/`
5. Update this README

## 📚 References

- [SUMMARY.md](SUMMARY.md) - Detailed architecture documentation
- [examples/README.md](examples/README.md) - Examples documentation
- [examples/scripts/example_usage.py](examples/scripts/example_usage.py) - Complete usage examples
- [examples/scripts/manual_test_with_local_llm.py](examples/scripts/manual_test_with_local_llm.py) - Manual testing with real model

