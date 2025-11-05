#!/usr/bin/env python3
"""
Simple test of OpenAI API for Korean bot-to-bot conversations.
"""

import os
from openai import OpenAI

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY not set")
    exit(1)

client = OpenAI(api_key=api_key)
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

print("=" * 60)
print("🇰🇷 한국어 책 추천 AI 테스트 (OpenAI API)")
print("=" * 60)
print(f"\n🔑 사용 모델: {model}")
print("=" * 60)

# Test 1: Mystery lover
print("\n" + "=" * 60)
print("📚 테스트 1: 미스터리 소설 애호가")
print("=" * 60)

user_context = """사용자 이름: 김민수
선호 장르: 미스터리, 스릴러, 추리소설
선호 작가: 히가시노 게이고, 아가사 크리스티
독서 이력:
  - 백야행 (히가시노 게이고)
  - 나미야 잡화점의 기적 (히가시노 게이고)
  - 그리고 아무도 없었다 (아가사 크리스티)"""

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

print("\n🤖 BookBot과 CriticBot의 DM 대화 생성 중...")

# System prompts
bookbot_system = """당신은 책 추천 전문가입니다.
지금 당신은 책 비평가와 인스타그램 DM으로 대화하고 있습니다.
상대방은 AI가 아니라 실제 사람입니다.

책을 추천할 때는 책 제목과 함께 1-2가지 이유를 간단히 설명하세요.
친근하고 자연스럽게 대화하되, 각 메시지는 2-3문장으로 작성하세요.
반말을 사용하세요.

예시:
용의자 X의 헌신 추천해! 히가시노 게이고 작품이라 백야행 좋아했으면 딱일 거야. 반전도 엄청나고 추리 과정이 정말 재밌거든."""

criticbot_system = """당신은 책 비평가입니다.
지금 당신은 책 추천 전문가와 인스타그램 DM으로 대화하고 있습니다.
상대방은 AI가 아니라 실제 사람입니다.

추천받은 책에 대해 질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
친근하고 자연스럽게 대화하되, 각 메시지는 2-3문장으로 작성하세요.
반말을 사용하세요.

예시:
좋긴 한데, 다른 작가 작품도 고려해봤어? 김영하 작품도 좋을 것 같은데."""

conversation = []

# Turn 1: BookBot recommends
prompt1 = f"""{user_context}

추천 후보:
{chr(10).join(f'- {book}' for book in candidates)}

비평가에게 DM으로 책을 추천하세요.
책 제목과 함께 왜 이 책이 좋은지 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

response1 = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": bookbot_system},
        {"role": "user", "content": prompt1}
    ],
    temperature=0.7,
    max_tokens=150
)
msg1 = response1.choices[0].message.content
conversation.append(("BookBot", msg1))

# Turn 2: CriticBot responds
prompt2 = f"""추천 전문가의 추천:
{msg1}

{user_context}

추천 전문가에게 DM으로 응답하세요.
질문하거나 다른 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

response2 = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": criticbot_system},
        {"role": "user", "content": prompt2}
    ],
    temperature=0.7,
    max_tokens=150
)
msg2 = response2.choices[0].message.content
conversation.append(("CriticBot", msg2))

# Turn 3: BookBot refines
prompt3 = f"""내 추천:
{msg1}

비평가의 의견:
{msg2}

비평가에게 DM으로 응답하세요.
답변하거나 다른 책을 추천할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

response3 = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": bookbot_system},
        {"role": "user", "content": prompt3}
    ],
    temperature=0.7,
    max_tokens=150
)
msg3 = response3.choices[0].message.content
conversation.append(("BookBot", msg3))

# Turn 4: CriticBot follow-up
conv_history = f"추천 전문가: {msg1}\n\n나: {msg2}\n\n추천 전문가: {msg3}"
prompt4 = f"""대화 내용:
{conv_history}

{user_context}

추천 전문가에게 DM으로 응답하세요.
추가 질문이나 의견을 제시할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

response4 = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": criticbot_system},
        {"role": "user", "content": prompt4}
    ],
    temperature=0.8,
    max_tokens=150
)
msg4 = response4.choices[0].message.content
conversation.append(("CriticBot", msg4))

# Turn 5: BookBot final
conv_history = f"{conv_history}\n\n비평가: {msg4}"
prompt5 = f"""대화 내용:
{conv_history}

비평가에게 DM으로 최종 응답하세요.
최종 추천이나 정리할 때 1-2가지 이유를 간단히 설명하세요.
2-3문장으로 작성하세요."""

response5 = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": bookbot_system},
        {"role": "user", "content": prompt5}
    ],
    temperature=0.7,
    max_tokens=150
)
msg5 = response5.choices[0].message.content
conversation.append(("BookBot", msg5))

# Display conversation
print(f"\n💬 BookBot ↔️ CriticBot 대화 ({len(conversation)}개 메시지):")
print("-" * 60)
for speaker, message in conversation:
    icon = "📚" if speaker == "BookBot" else "🔍"
    print(f"\n{icon} {speaker}")
    print(f"  {message}")
print("\n" + "-" * 60)

# Generate final summary and recommendation
print("\n" + "=" * 60)
print("📝 최종 요약 및 추천 생성 중...")
print("=" * 60)

conv_summary = "\n".join([f"{speaker}: {msg}" for speaker, msg in conversation])
final_prompt = f"""다음은 책 추천 전문가와 비평가의 대화입니다:

{conv_summary}

사용자 정보:
{user_context}

위 대화를 바탕으로 사용자에게 보여줄 최종 추천 요약을 작성하세요.
다음 형식으로 작성하세요:

1. 추천 책 목록 (2-3권)
2. 각 책에 대한 짧은 추천 이유 (1-2문장)
3. 전체적인 추천 코멘트 (2-3문장)

친근하고 자연스러운 한국어로 작성하세요."""

final_response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "당신은 책 추천 전문가입니다. 대화 내용을 바탕으로 사용자에게 최종 추천을 정리해서 전달합니다."},
        {"role": "user", "content": final_prompt}
    ],
    temperature=0.7,
    max_tokens=500
)
final_summary = final_response.choices[0].message.content

print("\n" + "=" * 60)
print("📖 최종 추천 요약")
print("=" * 60)
print(f"\n{final_summary}\n")

print("=" * 60)
print("✅ 테스트 완료!")
print("=" * 60)

