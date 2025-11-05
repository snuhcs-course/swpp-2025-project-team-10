"""
Quick test script to verify real local model inference works.

This script tests the LLM client with the actual Gemma3-4b-it model
to ensure transformers integration is working correctly.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm.client import LLMClient, Message
from llm.config import LLMConfig


def test_basic_inference():
    """Test basic model inference."""
    print("=" * 70)
    print("Testing Real Local Model Inference")
    print("=" * 70)

    # Set environment to use local model
    os.environ["USE_LOCAL_MODEL"] = "true"
    os.environ["LOCAL_MODEL_PATH"] = "models/gemma3-4b-it"
    os.environ["LOG_LEVEL"] = "INFO"

    print("\n1. Initializing LLM client...")
    try:
        config = LLMConfig.from_env()
        print(f"   Model path: {config.local_model_path}")
        print(f"   Using local model: {config.use_local_model}")

        client = LLMClient(config)
        print(f"   ✅ Client initialized successfully!")
        print(f"   Device: {client.device}")
        print(f"   Model type: {client.model_type}")

    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False

    # Test 1: Simple chat
    print("\n2. Testing simple chat interface...")
    try:
        response = client.chat(
            system_prompt="You are a helpful book recommendation assistant.",
            user_message="Recommend a mystery book in one sentence.",
            temperature=0.7,
        )
        print(f"   User: Recommend a mystery book in one sentence.")
        print(f"   Assistant: {response}")
        print(f"   ✅ Simple chat works!")

    except Exception as e:
        print(f"   ❌ Simple chat failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Multi-message conversation
    print("\n3. Testing multi-message conversation...")
    try:
        messages = [
            Message(
                role="system",
                content="You are a book expert. Be concise.",
            ),
            Message(
                role="user",
                content="What makes a good mystery novel?",
            ),
        ]

        response = client.generate(messages, temperature=0.7, max_tokens=100)
        print(f"   User: What makes a good mystery novel?")
        print(f"   Assistant: {response[:200]}...")
        print(f"   ✅ Multi-message conversation works!")

    except Exception as e:
        print(f"   ❌ Multi-message conversation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Book recommendation scenario
    print("\n4. Testing book recommendation scenario...")
    try:
        messages = [
            Message(
                role="system",
                content=(
                    "You are a book recommendation expert. "
                    "Analyze user preferences and suggest books."
                ),
            ),
            Message(
                role="user",
                content=(
                    "User loves mystery and thriller books. "
                    "Favorite authors: Agatha Christie, Dan Brown. "
                    "Recently read: Murder on the Orient Express. "
                    "Recommend 2 books in a brief paragraph."
                ),
            ),
        ]

        response = client.generate(messages, temperature=0.7, max_tokens=150)
        print(f"   Scenario: Mystery lover seeking recommendations")
        print(f"   Response: {response}")
        print(f"   ✅ Book recommendation scenario works!")

    except Exception as e:
        print(f"   ❌ Book recommendation scenario failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 70)
    print("✅ All tests passed! Real model inference is working.")
    print("=" * 70)
    return True


def test_device_detection():
    """Test device detection logic."""
    print("\n" + "=" * 70)
    print("Testing Device Detection")
    print("=" * 70)

    try:
        import torch

        print(f"\nCUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device: {torch.cuda.get_device_name(0)}")

        print(f"MPS available: {hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()}")

        # Show what device will be used
        os.environ["USE_LOCAL_MODEL"] = "true"
        os.environ["LOCAL_MODEL_PATH"] = "models/gemma3-4b-it"

        config = LLMConfig.from_env()
        client = LLMClient(config)

        print(f"\nSelected device: {client.device}")
        print(f"Model dtype: {next(client.model.parameters()).dtype}")

    except Exception as e:
        print(f"❌ Device detection failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Real Model Inference Tests\n")

    # Test device detection first
    test_device_detection()

    # Run main tests
    success = test_basic_inference()

    if success:
        print("\n✅ All tests completed successfully!")
        print("\nYou can now use the AI model with real local inference.")
        print("Next steps:")
        print("  1. Run: python tests/test_with_local_llm.py")
        print("  2. Run: python example_usage.py")
        print("  3. Integrate with backend API")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

