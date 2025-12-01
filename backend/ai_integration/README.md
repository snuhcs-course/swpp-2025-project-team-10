# AI Integration for Book Bartering

이 문서는 백엔드와 AI 모델 간의 통합 구조를 설명합니다.

## 구조 개요

```
backend/
├── ai_integration/
│   ├── __init__.py
│   └── services.py          # AI 추천 서비스 레이어
├── barter/
│   └── views.py             # AI 기반 교환 추천 통합
└── books/
    ├── ai_views.py          # 탐색 탭 AI 엔드포인트
    └── urls.py              # AI 엔드포인트 라우팅
```

## 주요 기능

### 1. 교환 추천 (Barter Recommendations)

**목적**: A가 B에게 교환을 신청할 때, B의 취향에 맞는 A의 책 1~3권을 AI가 추천

**데이터 흐름**:
```
사용자 요청 → create_barter_request (barter/views.py)
            ↓
    AIRecommendationService.recommend_books_for_barter()
            ↓
    컨텍스트 수집:
    - A의 교환 가능한 책들 (is_for_barter=True, trade_status='available')
    - B의 위시리스트
    - B의 취향 정보 (favorite_genres, authors, books, moods, purposes)
    - B의 서재 (이미 소유한 책 - 추천에서 제외)
            ↓
    AI 모델 호출 (TODO: 실제 구현 필요)
            ↓
    추천된 책 ID 반환 (최대 3개)
```

**API 변경사항**:
- `POST /barter/requests/create/`
  - 기존: 랜덤으로 3권 선택
  - 개선: AI가 B의 취향에 맞는 책 추천

**전달되는 컨텍스트**:
```python
{
    'requester': {
        'id': str,
        'username': str,
        'available_books': [
            {
                'id': str,
                'title': str,
                'authors': [str],
                'genres': [str],
                'description': str,
                'condition': str,
                'pages': int,
                'language': str
            }
        ]
    },
    'recipient': {
        'id': str,
        'username': str,
        'requested_book': {...},
        'wishlist': [
            {
                'id': str,
                'title': str,
                'authors': [str],
                'genres': [str],
                'priority': int,
                'notes': str
            }
        ],
        'taste': {
            'favorite_genres': [str],
            'favorite_authors': [str],
            'favorite_books': [str],
            'preferred_length': str,
            'preferred_moods': [str],
            'reading_purposes': [str]
        },
        'owned_book_ids': [str],      # B가 이미 소유한 책 ID (제외용)
        'owned_book_titles': [str]    # B가 이미 소유한 책 제목 (참고용)
    }
}
```

### 2. 탐색 탭 추천 (Exploration Recommendations)

**목적**: 사용자의 위시리스트와 취향을 기반으로 관심 있을 만한 책 추천

**데이터 흐름**:
```
사용자 요청 → GET /explore/ (또는 기존 호환: /library/explore/)
            ↓
    AIRecommendationService.recommend_books_for_exploration()
            ↓
    컨텍스트 수집:
    - 사용자의 위시리스트
    - 사용자의 취향 정보
    - 사용자가 이미 소유한 책들 (제외용)
            ↓
    AI 모델 호출 (TODO: 실제 구현 필요)
            ↓
    추천된 책 정보 반환 (최대 10개)
```

**엔드포인트**:
- `GET /explore/?limit=10` (권장)
- `GET /library/explore/?limit=10` (기존 호환 경로)
  - 응답:
    ```json
    {
        "recommendations": [
            {
                "id": "uuid",
                "title": "책 제목",
                "authors": ["저자1", "저자2"],
                "genres": ["장르1", "장르2"],
                "owner": {
                    "id": "uuid",
                    "username": "username"
                },
                "condition": "good",
                "cover_image": "url"
            }
        ]
    }
    ```

**전달되는 컨텍스트**:
```python
{
    'user': {
        'id': str,
        'username': str,
        'wishlist': [
            {
                'id': str,
                'title': str,
                'authors': [str],
                'genres': [str],
                'priority': int,
                'notes': str
            }
        ],
        'taste': {
            'favorite_genres': [str],
            'favorite_authors': [str],
            'favorite_books': [str],
            'preferred_length': str,
            'preferred_moods': [str],
            'reading_purposes': [str]
        },
        'owned_book_ids': [str]  # 이미 소유한 책 제외용
    }
}
```

## AI 모델 통합 가이드

### 현재 상태
- ✅ 백엔드 서비스 레이어 구현 완료
- ✅ 컨텍스트 데이터 수집 로직 구현
- ✅ API 엔드포인트 구현
- ⏳ 실제 AI 모델 호출 부분은 TODO (임시로 랜덤 선택)

### AI 모델 통합 절차

1. **ai-model 모듈을 Python path에 추가** (이미 구현됨)
   ```python
   # backend/ai_integration/services.py
   AI_MODEL_PATH = Path(settings.BASE_DIR).parent / "ai-model" / "src"
   sys.path.insert(0, str(AI_MODEL_PATH))
   ```

2. **교환 추천 통합**
   ```python
   # ai_integration/services.py의 recommend_books_for_barter() 함수에서:
   
   from pipeline.recommender import BarterRecommender
   from data.entities import BarterContext, Item, UserProfile, TradeRequest
   
   # 컨텍스트 데이터를 AI 모델 엔티티로 변환
   items = {}
   profiles = {}
   requests = []
   
   # 변환 로직 구현...
   
   context = BarterContext(
       items=items,
       profiles=profiles,
       requests=requests
   )

   recommender = BarterRecommender()
   recommendations = recommender.recommend(context, limit=limit)
   
   return [rec.candidate.item_id for rec in recommendations]
   ```

   또는 `.env`에 `AI_MODEL_BASE_URL`을 설정하면 GPU 서버의 FastAPI
   (`POST /api/recommendations/books`)를 호출하여 책 ID와 추천 이유를 함께 받습니다.
   네트워크 오류가 발생하면 자동으로 로컬 파이프라인/랜덤 선택으로 폴백합니다.

3. **탐색 추천 통합**
   ```python
   # 별도의 ExplorationRecommender 또는 기존 추천 로직 활용
   # 위시리스트와 취향 정보를 기반으로 추천
   ```

### 디버깅 엔드포인트

컨텍스트 데이터 확인용:
```bash
POST /ai/barter-context/ (또는 /library/ai/barter-context/ 호환)
{
    "recipient_id": "user-uuid",
    "requested_book_id": "book-uuid"
}
```

## 추가 고려사항

### 1. 추천 품질 향상을 위한 추가 데이터
현재 전달되는 데이터 외에 추가로 고려할 수 있는 요소:

**교환 추천**:
- B의 독서 이력 (읽은 책, 평점)
- A와 B의 과거 교환 이력
- 책의 상태 (condition) 중요도
- 지리적 거리 (trade_place_name, trade_address)

**탐색 추천**:
- 사용자의 독서 이력
- 인기도/트렌드 정보
- 비슷한 취향의 사용자들이 선호하는 책

### 2. 성능 최적화
- 컨텍스트 데이터 캐싱
- 추천 결과 캐싱 (일정 시간)
- 배치 추천 처리

### 3. 폴백 전략
현재 구현된 폴백:
- AI 추천 실패 시 → 랜덤 선택
- 추천된 책이 없을 시 → 빈 리스트 반환

### 4. 모니터링
추가 필요 사항:
- 추천 성공률 로깅
- 추천 품질 메트릭
- AI 모델 응답 시간

## 테스트

### 교환 추천 테스트
```bash
# 교환 요청 생성 (AI 추천 사용)
POST /barter/requests/create/
{
    "recipient_id": "recipient-uuid",
    "requested_book_id": "book-uuid"
}
```

### 탐색 추천 테스트
```bash
# 탐색 탭 추천 조회
GET /explore/?limit=10
```

### 컨텍스트 확인
```bash
# 디버깅용 컨텍스트 조회
POST /ai/barter-context/
{
    "recipient_id": "recipient-uuid",
    "requested_book_id": "book-uuid"
}
```
