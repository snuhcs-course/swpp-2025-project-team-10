#!/usr/bin/env python3
"""
한국어 예제 테스트 스크립트

로컬 LLM 모델을 사용하여 한국어 책 추천 대화를 생성하고 테스트합니다.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data.entities import Item, UserProfile
from llm.client import LLMClient
from llm.config import LLMConfig
from llm.reasoning import ReasoningGenerator
from visualization.conversation_formatter import ConversationFormatter


def test_korean_mystery_lover():
    """테스트 1: 미스터리 소설 애호가"""
    print("\n" + "=" * 60)
    print("📚 테스트 1: 미스터리 소설 애호가")
    print("=" * 60)

    # 사용자 프로필
    user_profile = UserProfile(
        user_id="user_001",
        display_name="김민수",
        trust_score=0.92,
        reliability=0.88,
        preferences={
            "genres": ["미스터리", "스릴러", "추리소설"],
            "authors": ["히가시노 게이고", "아가사 크리스티"],
            "moods": ["긴장감", "반전"],
        },
        exclusion_rules=[],
        risk_notes=[],
    )

    # 추천 후보 책들
    candidate_books = [
        Item(
            item_id="book_001",
            owner_id="owner_001",
            title="용의자 X의 헌신",
            valuation=0.95,
            facets={"author": "히가시노 게이고", "genre": "미스터리"},
            metadata={"author": "히가시노 게이고", "year": 2005},
        ),
        Item(
            item_id="book_002",
            owner_id="owner_002",
            title="오리엔트 특급 살인",
            valuation=0.90,
            facets={"author": "아가사 크리스티", "genre": "추리소설"},
            metadata={"author": "아가사 크리스티", "year": 1934},
        ),
        Item(
            item_id="book_003",
            owner_id="owner_003",
            title="살인자의 기억법",
            valuation=0.88,
            facets={"author": "김영하", "genre": "스릴러"},
            metadata={"author": "김영하", "year": 2013},
        ),
    ]

    # 독서 이력
    reading_history = ["백야행", "나미야 잡화점의 기적", "그리고 아무도 없었다"]

    # LLM 설정 (로컬 모델 사용, DM 스타일)
    config = LLMConfig(
        use_local_model=True,
        local_model_path="models/gemma3-4b-it",
        temperature=0.7,
        max_tokens=150,  # DM 스타일 + 이유 설명 (2-3문장)
    )

    # 추론 생성기
    generator = ReasoningGenerator(config)

    print(f"\n👤 사용자: {user_profile.display_name}")
    print(f"📖 선호 장르: {', '.join(user_profile.preferences['genres'])}")
    print(f"✍️  선호 작가: {', '.join(user_profile.preferences['authors'])}")
    print(f"📚 독서 이력: {', '.join(reading_history)}")
    print(f"\n🎯 추천 후보: {len(candidate_books)}권")
    for book in candidate_books:
        print(f"   - {book.title} ({book.facets.get('author', 'Unknown')})")

    print("\n🤖 BookBot과 CriticBot의 DM 대화 생성 중...")
    print("   (사용자는 두 봇의 대화를 관찰하며 추론 과정을 이해합니다)")

    # 추론 궤적 생성
    trajectory = generator.generate_book_recommendation_reasoning(
        user_profile=user_profile,
        candidate_books=candidate_books,
        user_reading_history=reading_history,
    )

    # 결과 출력 (DM 대화 형식)
    print(f"\n💬 BookBot ↔️ CriticBot 대화 ({len(trajectory.conversation)}개 메시지):")
    print("-" * 60)
    for i, turn in enumerate(trajectory.conversation, 1):
        speaker_emoji = "📚" if turn.speaker == "recommender" else "🔍"
        speaker_name = "BookBot" if turn.speaker == "recommender" else "CriticBot"
        print(f"\n{speaker_emoji} {speaker_name}")
        print(f"  {turn.message}")

    print("\n" + "-" * 60)
    print(f"\n✅ 최종 추천:")
    print(f"{trajectory.final_recommendation}")
    print(f"\n📊 신뢰도: {trajectory.confidence_score:.2f}")

    return trajectory


def test_korean_casual_reader():
    """테스트 2: 일반 독자"""
    print("\n" + "=" * 60)
    print("📚 테스트 2: 다양한 장르를 읽는 일반 독자")
    print("=" * 60)

    user_profile = UserProfile(
        user_id="user_002",
        display_name="이지은",
        trust_score=0.75,
        reliability=0.80,
        preferences={
            "genres": ["로맨스", "자기계발", "에세이"],
            "authors": ["김애란", "정유정"],
            "moods": ["감동", "위로"],
        },
        exclusion_rules=[],
        risk_notes=[],
    )

    candidate_books = [
        Item(
            item_id="book_004",
            owner_id="owner_004",
            title="달러구트 꿈 백화점",
            valuation=0.85,
            facets={"author": "이미예", "genre": "판타지"},
            metadata={"author": "이미예"},
        ),
        Item(
            item_id="book_005",
            owner_id="owner_005",
            title="아몬드",
            valuation=0.88,
            facets={"author": "손원평", "genre": "청소년소설"},
            metadata={"author": "손원평"},
        ),
    ]

    reading_history = ["82년생 김지영", "미움받을 용기"]

    config = LLMConfig(
        use_local_model=True,
        local_model_path="models/gemma3-4b-it",
        temperature=0.7,
        max_tokens=150,  # DM 스타일 + 이유 설명
    )

    generator = ReasoningGenerator(config)

    print(f"\n👤 사용자: {user_profile.display_name}")
    print(f"📖 선호 장르: {', '.join(user_profile.preferences['genres'])}")
    print(f"📚 독서 이력: {', '.join(reading_history)}")

    print("\n🤖 BookBot과 CriticBot의 DM 대화 생성 중...")

    trajectory = generator.generate_book_recommendation_reasoning(
        user_profile=user_profile,
        candidate_books=candidate_books,
        user_reading_history=reading_history,
    )

    print(f"\n💬 BookBot ↔️ CriticBot 대화 ({len(trajectory.conversation)}개 메시지):")
    print("-" * 60)
    for turn in trajectory.conversation:
        speaker_emoji = "📚" if turn.speaker == "recommender" else "🔍"
        speaker_name = "BookBot" if turn.speaker == "recommender" else "CriticBot"
        print(f"\n{speaker_emoji} {speaker_name}")
        print(f"  {turn.message}")

    print("\n" + "-" * 60)
    print(f"\n✅ 최종 추천:")
    print(f"{trajectory.final_recommendation}")
    print(f"\n📊 신뢰도: {trajectory.confidence_score:.2f}")

    return trajectory


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("🇰🇷 한국어 책 추천 AI 테스트 (BookBot ↔️ CriticBot DM)")
    print("=" * 60)
    print("\n이 스크립트는 로컬 LLM 모델을 사용하여")
    print("BookBot과 CriticBot의 DM 대화를 생성합니다.")
    print("\n💬 특징:")
    print("   - 두 봇이 서로 대화하며 책을 추천")
    print("   - 각 메시지에 추천/비평 이유 포함 (2-3문장)")
    print("   - 사용자는 대화를 관찰하며 추론 과정 이해")
    print("   - 5턴 대화로 충분한 논의")
    print("\n⚠️  주의: 로컬 모델이 필요합니다 (models/gemma3-4b-it)")
    print("=" * 60)

    try:
        # 테스트 1: 미스터리 애호가
        trajectory1 = test_korean_mystery_lover()

        # 테스트 2: 일반 독자
        trajectory2 = test_korean_casual_reader()

        # 요약
        print("\n" + "=" * 60)
        print("📊 테스트 완료 요약")
        print("=" * 60)
        print(f"\n✅ 테스트 1 - 추천 책: {', '.join(trajectory1.recommended_books)}")
        print(f"   신뢰도: {trajectory1.confidence_score:.2f}")
        print(f"   대화 메시지: {len(trajectory1.conversation)}개 (DM 스타일)")

        print(f"\n✅ 테스트 2 - 추천 책: {', '.join(trajectory2.recommended_books)}")
        print(f"   신뢰도: {trajectory2.confidence_score:.2f}")
        print(f"   대화 메시지: {len(trajectory2.conversation)}개 (DM 스타일)")

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n❌ 오류: 로컬 모델을 찾을 수 없습니다.")
        print(f"   {e}")
        print("\n💡 해결 방법:")
        print("   1. models/gemma3-4b-it 디렉토리에 모델 파일이 있는지 확인")
        print("   2. .env 파일에서 LOCAL_MODEL_PATH 설정 확인")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

