# AI Model Examples / AI 모델 예제

This directory contains example scenarios and scripts demonstrating the AI model's capabilities for book recommendations and barter negotiations.

이 디렉토리는 AI 모델의 책 추천 및 물물교환 협상 기능을 보여주는 예제 시나리오와 스크립트를 포함합니다.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── scenarios/                   # Example YAML outputs / 예제 YAML 출력
│   ├── example_1_mystery_lover.yaml
│   ├── example_2_casual_reader.yaml
│   ├── example_3_barter_negotiation.yaml
│   └── korean_example_1_mystery_lover.yaml  # 한국어 예제
└── scripts/                     # Example and test scripts / 예제 및 테스트 스크립트
    ├── example_usage.py         # Complete usage examples
    ├── manual_test_with_local_llm.py  # Manual testing with real model
    ├── test_real_model.py       # Quick model verification
    └── test_korean_examples.py  # 한국어 예제 테스트
```

---

## 📋 Scenarios (`scenarios/`)

### Overview

| File | Size | Description |
|------|------|-------------|
| `example_1_mystery_lover.yaml` | 4.0K | Mystery book lover with strong genre preferences |
| `example_2_casual_reader.yaml` | 1.6K | Casual reader with diverse interests (from frontend) |
| `example_3_barter_negotiation.yaml` | 1.3K | Two-way barter negotiation with LLM mediation |

### Example Scenarios

**Example 1: Mystery Lover** - User with strong mystery/thriller preferences (Backend data source)  
**Example 2: Casual Reader** - User with diverse reading interests (Frontend data source)  
**Example 3: Barter Negotiation** - Two users exchanging books with distance-based matching

---

## 🔧 Scripts (`scripts/`)

### 1. `example_usage.py`
Complete usage examples with mock LLM responses (runs instantly).

**Usage**: `python examples/scripts/example_usage.py`

### 2. `manual_test_with_local_llm.py`
Manual testing with real Gemma3-4b-it model (requires model files, slow).

**Usage**: `python examples/scripts/manual_test_with_local_llm.py`

### 3. `test_real_model.py`

Quick model verification with device detection.

**Usage**: `python examples/scripts/test_real_model.py`

### 4. `test_korean_examples.py` 🇰🇷

한국어 책 추천 예제 테스트 (로컬 LLM 사용).

**사용법**: `python examples/scripts/test_korean_examples.py`

**특징**:
- 한국어 프롬프트 및 응답
- 간결한 대화 (2-3문장)
- 한국 도서 및 작가 예제
- 실시간 LLM 추론

---

## 🚀 Quick Start

```bash
# View example outputs / 예제 출력 보기
cat examples/scenarios/example_1_mystery_lover.yaml
cat examples/scenarios/korean_example_1_mystery_lover.yaml  # 한국어

# Run examples (instant, uses mocks) / 예제 실행 (즉시, 목 사용)
python examples/scripts/example_usage.py

# Test with real model (slow, requires model) / 실제 모델 테스트 (느림, 모델 필요)
python examples/scripts/manual_test_with_local_llm.py

# Test Korean examples / 한국어 예제 테스트
python examples/scripts/test_korean_examples.py
```

---

## 📚 Related Documentation

- [../README.md](../README.md) - Main AI model documentation
- [../IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) - Implementation details
- [../src/](../src/) - Source code
