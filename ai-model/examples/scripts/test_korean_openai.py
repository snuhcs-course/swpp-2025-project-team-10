#!/usr/bin/env python3
"""
Test Korean book recommendation conversations using OpenAI API.

This script demonstrates the bot-to-bot DM conversation format
with BookBot and CriticBot using OpenAI's GPT models.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import only what we need
from src.llm.client import LLMClient
from src.llm.config import LLMConfig


def test_mystery_lover():
    """Test case 1: Mystery novel enthusiast."""
    print("\n" + "=" * 60)
    print("📚 테스트 1: 미스터리 소설 애호가")
    print("=" * 60)

    # User profile
    user_context = """사용자 이름: 김민수
선호 장르: 미스터리, 스릴러, 추리소설
선호 작가: 히가시노 게이고, 아가사 크리스티
독서 이력:
  - 백야행 (히가시노 게이고)
  - 나미야 잡화점의 기적 (히가시노 게이고)
  - 그리고 아무도 없었다 (아가사 크리스티)"""

    # Candidate books
    candidates = [
        "용의자 X의 헌신 (히가시노 게이고)",
        "오리엔트 특급 살인 (아가사 크리스티)",
        "살인자의 기억법 (김영하)",
    ]

    print(f"\n👤 사용자: 김민수")
    print(f"📖 선호 장르: 미스터리, 스릴러, 추리소설")
    print(f"✍️  선호 작가: 히가시노 게이고, 아가사 크리스티")
    print(f"📚 독서 이력: 백야행, 나미야 잡화점의 기적, 그리고 아무도 없었다")
    print(f"\n🎯 추천 후보: {len(candidates)}권")
    for book in candidates:
        print(f"   - {book}")

    # Configure to use OpenAI
    config = LLMConfig(
        use_local_model=False,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.7,
        max_tokens=150,  # DM-style with reasoning
    )

    # Create LLM clients
    bookbot = LLMClient(config)
    criticbot = LLMClient(config)

    print("\n🤖 BookBot과 CriticBot의 DM 대화 생성 중...")
    print("   (사용자는 두 봇의 대화를 관찰하며 추론 과정을 이해합니다)")

    # System prompts
    bookbot_prompt = """당신은 BookBot입니다. CriticBot과 DM으로 대화하며 책을 추천합니다.
추천할 때는 책 제목과 함께 1-2가지 이유를 간단히 설명하세요.
인스타그램 DM처럼 친근하게 대화하되, 각 메시지는 2-3문장으로 작성하세요.
반드시 'CriticBot아' 또는 'CriticBot!'으로 시작하세요.

예시:
CriticBot아! 용의자 X의 헌신 추천해. 히가시노 게이고 작품이라 백야행 좋아했으면 딱일 거야. 반전도 엄청나고 추리 과정이 정말 재밌거든."""

    criticbot_prompt = """당신은 CriticBot입니다. BookBot과 DM으로 대화하며 추천을 검토합니다.
질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
인스타그램 DM처럼 친근하게 대화하되, 각 메시지는 2-3문장으로 작성하세요.
반드시 'BookBot아' 또는 'BookBot!'으로 시작하세요.

예시:
BookBot아! 좋긴 한데, 다른 작가 작품도 고려해봤어? 김영하 작품도 좋을 것 같은데."""

    # Conversation
    conversation = []

    # Turn 1: BookBot recommends
    prompt1 = f"""{user_context}

추천 후보:
{chr(10).join(f'- {book}' for book in candidates)}

CriticBot에게 DM으로 책을 추천하세요.
반드시 'CriticBot아!' 또는 'CriticBot!'으로 시작하세요.
책 제목과 함께 왜 이 책이 좋은지 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

    msg1 = bookbot.chat(bookbot_prompt, prompt1, temperature=0.7)
    conversation.append(("BookBot", msg1))

    # Turn 2: CriticBot responds
    prompt2 = f"""BookBot의 추천:
{msg1}

{user_context}

BookBot에게 DM으로 응답하세요.
반드시 'BookBot아!' 또는 'BookBot!'으로 시작하세요.
질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

    msg2 = criticbot.chat(criticbot_prompt, prompt2, temperature=0.7)
    conversation.append(("CriticBot", msg2))

    # Turn 3: BookBot refines
    prompt3 = f"""내 추천:
{msg1}

CriticBot의 의견:
{msg2}

CriticBot에게 DM으로 응답하세요.
반드시 'CriticBot아!' 또는 'CriticBot!'으로 시작하세요.
답변하거나 다른 책을 추천할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

    msg3 = bookbot.chat(bookbot_prompt, prompt3, temperature=0.7)
    conversation.append(("BookBot", msg3))

    # Turn 4: CriticBot follow-up
    conv_history = f"BOOKBOT: {msg1}\n\nCRITICBOT: {msg2}\n\nBOOKBOT: {msg3}"
    prompt4 = f"""대화 내용:
{conv_history}

{user_context}

BookBot에게 DM으로 응답하세요.
반드시 'BookBot아!' 또는 'BookBot!'으로 시작하세요.
추가 질문이나 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

    msg4 = criticbot.chat(criticbot_prompt, prompt4, temperature=0.8)
    conversation.append(("CriticBot", msg4))

    # Turn 5: BookBot final
    conv_history = f"{conv_history}\n\nCRITICBOT: {msg4}"
    prompt5 = f"""대화 내용:
{conv_history}

CriticBot에게 DM으로 최종 응답하세요.
반드시 'CriticBot아!' 또는 'CriticBot!'으로 시작하세요.
최종 추천이나 정리할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

    msg5 = bookbot.chat(bookbot_prompt, prompt5, temperature=0.7)
    conversation.append(("BookBot", msg5))

    # Display conversation
    print(f"\n💬 BookBot ↔️ CriticBot 대화 ({len(conversation)}개 메시지):")
    print("-" * 60)
    for speaker, message in conversation:
        icon = "📚" if speaker == "BookBot" else "🔍"
        print(f"\n{icon} {speaker}")
        print(f"  {message}")
    print("\n" + "-" * 60)

    return conversation


def test_general_reader():
    """Test case 2: General reader with diverse interests."""
    print("\n" + "=" * 60)
    print("📚 테스트 2: 다양한 장르를 읽는 일반 독자")
    print("=" * 60)

    # User profile
    user_context = """사용자 이름: 이지은
선호 장르: 로맨스, 자기계발, 에세이
독서 이력:
  - 82년생 김지영 (조남주)
  - 미움받을 용기 (기시미 이치로)"""

    print(f"\n👤 사용자: 이지은")
    print(f"📖 선호 장르: 로맨스, 자기계발, 에세이")
    print(f"📚 독서 이력: 82년생 김지영, 미움받을 용기")

    # Configure to use OpenAI
    config = LLMConfig(
        use_local_model=False,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.7,
        max_tokens=150,  # DM-style with reasoning
    )

    # Create LLM clients
    bookbot = LLMClient(config)
    criticbot = LLMClient(config)

    print("\n🤖 BookBot과 CriticBot의 DM 대화 생성 중...")

    # System prompts (same as test 1)
    bookbot_prompt = """당신은 BookBot입니다. CriticBot과 DM으로 대화하며 책을 추천합니다.
추천할 때는 책 제목과 함께 1-2가지 이유를 간단히 설명하세요.
인스타그램 DM처럼 친근하게 대화하되, 각 메시지는 2-3문장으로 작성하세요.
반드시 'CriticBot아' 또는 'CriticBot!'으로 시작하세요."""

    criticbot_prompt = """당신은 CriticBot입니다. BookBot과 DM으로 대화하며 추천을 검토합니다.
질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
인스타그램 DM처럼 친근하게 대화하되, 각 메시지는 2-3문장으로 작성하세요.
반드시 'BookBot아' 또는 'BookBot!'으로 시작하세요."""

    # Conversation
    conversation = []

    # Turn 1: BookBot recommends
    prompt1 = f"""{user_context}

CriticBot에게 DM으로 책을 추천하세요.
반드시 'CriticBot아!' 또는 'CriticBot!'으로 시작하세요.
책 제목과 함께 왜 이 책이 좋은지 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

    msg1 = bookbot.chat(bookbot_prompt, prompt1, temperature=0.7)
    conversation.append(("BookBot", msg1))

    # Turn 2: CriticBot responds
    prompt2 = f"""BookBot의 추천:
{msg1}

{user_context}

BookBot에게 DM으로 응답하세요.
반드시 'BookBot아!' 또는 'BookBot!'으로 시작하세요.
2-3문장으로 작성하세요."""

    msg2 = criticbot.chat(criticbot_prompt, prompt2, temperature=0.7)
    conversation.append(("CriticBot", msg2))

    # Turn 3: BookBot refines
    prompt3 = f"""CriticBot의 의견:
{msg2}

CriticBot에게 DM으로 응답하세요.
반드시 'CriticBot아!' 또는 'CriticBot!'으로 시작하세요.
2-3문장으로 작성하세요."""

    msg3 = bookbot.chat(bookbot_prompt, prompt3, temperature=0.7)
    conversation.append(("BookBot", msg3))

    # Display conversation
    print(f"\n💬 BookBot ↔️ CriticBot 대화 ({len(conversation)}개 메시지):")
    print("-" * 60)
    for speaker, message in conversation:
        icon = "📚" if speaker == "BookBot" else "🔍"
        print(f"\n{icon} {speaker}")
        print(f"  {message}")
    print("\n" + "-" * 60)

    return conversation


def main():
    """Run all test cases."""
    print("=" * 60)
    print("🇰🇷 한국어 책 추천 AI 테스트 (OpenAI API)")
    print("=" * 60)
    print("\n이 스크립트는 OpenAI API를 사용하여")
    print("BookBot과 CriticBot의 DM 대화를 생성합니다.")
    print("\n💬 특징:")
    print("   - 두 봇이 서로 대화하며 책을 추천")
    print("   - 각 메시지에 추천/비평 이유 포함 (2-3문장)")
    print("   - 사용자는 대화를 관찰하며 추론 과정 이해")
    print("   - 5턴 대화로 충분한 논의")
    print(f"\n🔑 사용 모델: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    print("=" * 60)

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ 오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 API 키를 설정해주세요.")
        sys.exit(1)

    # Run tests
    results = []

    try:
        result1 = test_mystery_lover()
        results.append(("미스터리 소설 애호가", result1))
    except Exception as e:
        print(f"\n❌ 테스트 1 실패: {e}")

    try:
        result2 = test_general_reader()
        results.append(("다양한 장르를 읽는 일반 독자", result2))
    except Exception as e:
        print(f"\n❌ 테스트 2 실패: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 테스트 완료 요약")
    print("=" * 60)

    for i, (name, conversation) in enumerate(results, 1):
        print(f"\n✅ 테스트 {i} - {name}")
        print(f"   대화 메시지: {len(conversation)}개 (DM 스타일)")

    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

