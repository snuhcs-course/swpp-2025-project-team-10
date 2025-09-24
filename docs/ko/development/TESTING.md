# 테스팅 가이드라인

이 문서는 SWPP AI Application 프로젝트의 테스팅 전략, 도구, 모범 사례를 설명합니다.

## 📋 목차

- [테스팅 전략](#테스팅-전략)
- [테스트 타입](#테스트-타입)
- [Python 테스팅](#python-테스팅)
- [Kotlin 테스팅](#kotlin-테스팅)
- [AI 모델 테스팅](#ai-모델-테스팅)
- [통합 테스팅](#통합-테스팅)
- [성능 테스팅](#성능-테스팅)
- [테스트 자동화](#테스트-자동화)

## 🎯 테스팅 전략

### 테스트 피라미드
```
        /\
       /  \
      / E2E \     <- 적은 수의 End-to-End 테스트
     /______\
    /        \
   /Integration\ <- 중간 수의 통합 테스트
  /__________\
 /            \
/  Unit Tests  \   <- 많은 수의 단위 테스트
/______________\
```

### 테스트 원칙
1. **빠른 피드백**: 단위 테스트는 빠르게 실행
2. **신뢰성**: 테스트는 일관된 결과를 제공
3. **독립성**: 각 테스트는 독립적으로 실행 가능
4. **명확성**: 테스트 의도가 명확하게 드러남
5. **유지보수성**: 코드 변경 시 테스트도 쉽게 수정

### 커버리지 목표
- **전체 코드 커버리지**: 최소 80%
- **핵심 비즈니스 로직**: 95% 이상
- **API 엔드포인트**: 100%
- **유틸리티 함수**: 90% 이상

## 🧪 테스트 타입

### 1. 단위 테스트 (Unit Tests)
- **목적**: 개별 함수/메서드의 동작 검증
- **범위**: 단일 컴포넌트
- **실행 속도**: 매우 빠름 (< 1초)
- **비율**: 전체 테스트의 70%

### 2. 통합 테스트 (Integration Tests)
- **목적**: 컴포넌트 간 상호작용 검증
- **범위**: 여러 컴포넌트
- **실행 속도**: 보통 (1-10초)
- **비율**: 전체 테스트의 20%

### 3. E2E 테스트 (End-to-End Tests)
- **목적**: 전체 시스템 워크플로우 검증
- **범위**: 전체 애플리케이션
- **실행 속도**: 느림 (10초 이상)
- **비율**: 전체 테스트의 10%

## 🐍 Python 테스팅

### 테스트 도구
- **pytest**: 메인 테스트 프레임워크
- **pytest-asyncio**: 비동기 테스트 지원
- **pytest-cov**: 코드 커버리지 측정
- **pytest-mock**: 모킹 지원
- **factory-boy**: 테스트 데이터 생성

### 프로젝트 구조
```
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── conftest.py
└── pytest.ini
```

### 단위 테스트 예시
```python
import pytest
from unittest.mock import Mock, patch
from src.services.user_service import UserService
from src.models.user import User
from src.schemas.user import UserCreate

class TestUserService:
    """UserService 단위 테스트."""
    
    @pytest.fixture
    def mock_db(self):
        """데이터베이스 세션 모킹."""
        return Mock()
    
    @pytest.fixture
    def user_service(self, mock_db):
        """UserService 인스턴스 생성."""
        return UserService(mock_db)
    
    def test_create_user_success(self, user_service, mock_db):
        """사용자 생성 성공 테스트."""
        # Given
        user_data = UserCreate(
            email="test@example.com",
            name="테스트 사용자",
            password="password123"
        )
        expected_user = User(
            id="123",
            email="test@example.com",
            name="테스트 사용자"
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # When
        with patch('src.services.user_service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            result = user_service.create_user(user_data)
        
        # Then
        assert result.email == "test@example.com"
        assert result.name == "테스트 사용자"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_create_user_duplicate_email(self, user_service, mock_db):
        """중복 이메일로 사용자 생성 실패 테스트."""
        # Given
        user_data = UserCreate(
            email="existing@example.com",
            name="테스트 사용자",
            password="password123"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = User()
        
        # When & Then
        with pytest.raises(ValueError, match="이미 존재하는 이메일"):
            user_service.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_async_user_operation(self, user_service):
        """비동기 사용자 작업 테스트."""
        # Given
        user_id = "123"
        
        # When
        result = await user_service.get_user_async(user_id)
        
        # Then
        assert result is not None
```

### 통합 테스트 예시
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db, Base

# 테스트용 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """테스트용 데이터베이스 세션."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """테스트 클라이언트."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

class TestUserAPI:
    """사용자 API 통합 테스트."""
    
    def test_create_user_api(self, client):
        """사용자 생성 API 테스트."""
        # Given
        user_data = {
            "email": "test@example.com",
            "name": "테스트 사용자",
            "password": "password123"
        }
        
        # When
        response = client.post("/api/v1/users", json=user_data)
        
        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "테스트 사용자"
        assert "id" in data
    
    def test_get_user_api(self, client, db_session):
        """사용자 조회 API 테스트."""
        # Given - 사용자 미리 생성
        user = User(email="test@example.com", name="테스트 사용자")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # When
        response = client.get(f"/api/v1/users/{user.id}")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "테스트 사용자"
```

### 테스트 설정 (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --asyncio-mode=auto
markers =
    slow: 느린 테스트
    integration: 통합 테스트
    unit: 단위 테스트
```

## 📱 Kotlin 테스팅

### 테스트 도구
- **JUnit 5**: 메인 테스트 프레임워크
- **MockK**: Kotlin용 모킹 라이브러리
- **Espresso**: UI 테스트
- **Robolectric**: Android 단위 테스트
- **Turbine**: Flow 테스트

### 프로젝트 구조
```
frontend/
├── src/
│   ├── main/
│   └── test/
│       ├── java/
│       │   ├── unit/
│       │   │   ├── UserRepositoryTest.kt
│       │   │   └── UserViewModelTest.kt
│       │   └── integration/
│       │       └── ApiIntegrationTest.kt
│       └── androidTest/
│           └── ui/
│               └── UserProfileTest.kt
```

### 단위 테스트 예시
```kotlin
import io.mockk.*
import kotlinx.coroutines.test.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Assertions.*

@OptIn(ExperimentalCoroutinesApi::class)
class UserRepositoryTest {
    
    private lateinit var userRepository: UserRepository
    private lateinit var mockApiService: ApiService
    private lateinit var mockUserDao: UserDao
    
    @BeforeEach
    fun setup() {
        mockApiService = mockk()
        mockUserDao = mockk()
        userRepository = UserRepository(mockApiService, mockUserDao)
    }
    
    @Test
    fun `사용자 조회 성공 테스트`() = runTest {
        // Given
        val userId = "123"
        val expectedUser = User(
            id = userId,
            name = "테스트 사용자",
            email = "test@example.com"
        )
        
        coEvery { mockApiService.getUser(userId) } returns Response.success(expectedUser)
        coEvery { mockUserDao.insertUser(any()) } just Runs
        
        // When
        val result = userRepository.getUser(userId)
        
        // Then
        assertTrue(result.isSuccess)
        assertEquals(expectedUser, result.getOrNull())
        coVerify { mockApiService.getUser(userId) }
        coVerify { mockUserDao.insertUser(any()) }
    }
    
    @Test
    fun `사용자 조회 실패 테스트`() = runTest {
        // Given
        val userId = "123"
        val errorResponse = Response.error<User>(404, "Not Found".toResponseBody())
        
        coEvery { mockApiService.getUser(userId) } returns errorResponse
        
        // When
        val result = userRepository.getUser(userId)
        
        // Then
        assertTrue(result.isFailure)
        assertTrue(result.exceptionOrNull()?.message?.contains("API 호출 실패") == true)
    }
}

class UserViewModelTest {
    
    private lateinit var viewModel: UserViewModel
    private lateinit var mockRepository: UserRepository
    
    @BeforeEach
    fun setup() {
        mockRepository = mockk()
        viewModel = UserViewModel(mockRepository)
    }
    
    @Test
    fun `사용자 로딩 성공 테스트`() = runTest {
        // Given
        val userId = "123"
        val user = User(id = userId, name = "테스트 사용자", email = "test@example.com")
        
        coEvery { mockRepository.getUser(userId) } returns Result.success(user)
        
        // When
        viewModel.loadUser(userId)
        
        // Then
        val uiState = viewModel.uiState.value
        assertTrue(uiState is UserUiState.Success)
        assertEquals(user, (uiState as UserUiState.Success).user)
    }
    
    @Test
    fun `사용자 로딩 실패 테스트`() = runTest {
        // Given
        val userId = "123"
        val error = Exception("네트워크 오류")
        
        coEvery { mockRepository.getUser(userId) } returns Result.failure(error)
        
        // When
        viewModel.loadUser(userId)
        
        // Then
        val uiState = viewModel.uiState.value
        assertTrue(uiState is UserUiState.Error)
        assertEquals("네트워크 오류", (uiState as UserUiState.Error).message)
    }
}
```

### UI 테스트 예시
```kotlin
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class UserProfileTest {
    
    @get:Rule
    val composeTestRule = createComposeRule()
    
    @Test
    fun 사용자_프로필_표시_테스트() {
        // Given
        val user = User(
            id = "123",
            name = "홍길동",
            email = "hong@example.com"
        )
        
        // When
        composeTestRule.setContent {
            UserProfile(
                user = user,
                onEditClick = {}
            )
        }
        
        // Then
        composeTestRule
            .onNodeWithText("홍길동")
            .assertIsDisplayed()
        
        composeTestRule
            .onNodeWithText("hong@example.com")
            .assertIsDisplayed()
        
        composeTestRule
            .onNodeWithText("편집")
            .assertIsDisplayed()
            .assertHasClickAction()
    }
    
    @Test
    fun 편집_버튼_클릭_테스트() {
        // Given
        var editClicked = false
        val user = User(id = "123", name = "홍길동", email = "hong@example.com")
        
        composeTestRule.setContent {
            UserProfile(
                user = user,
                onEditClick = { editClicked = true }
            )
        }
        
        // When
        composeTestRule
            .onNodeWithText("편집")
            .performClick()
        
        // Then
        assertTrue(editClicked)
    }
}
```

## 🤖 AI 모델 테스팅

### 모델 테스트 전략
1. **데이터 검증**: 입력/출력 데이터 형식 확인
2. **모델 로딩**: 모델 파일 로딩 및 초기화 테스트
3. **추론 테스트**: 예상 입력에 대한 출력 검증
4. **성능 테스트**: 추론 속도 및 메모리 사용량 측정
5. **엣지 케이스**: 비정상 입력에 대한 처리 확인

### 모델 테스트 예시
```python
import pytest
import torch
import numpy as np
from src.models.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer:
    """감정 분석 모델 테스트."""
    
    @pytest.fixture
    def model(self):
        """모델 인스턴스 생성."""
        return SentimentAnalyzer.load_pretrained("models/sentiment_model.pt")
    
    def test_model_loading(self, model):
        """모델 로딩 테스트."""
        assert model is not None
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')
    
    def test_positive_sentiment_prediction(self, model):
        """긍정적 감정 예측 테스트."""
        # Given
        positive_text = "이 제품은 정말 훌륭합니다!"
        
        # When
        result = model.predict(positive_text)
        
        # Then
        assert result['sentiment'] == 'positive'
        assert result['confidence'] > 0.7
    
    def test_negative_sentiment_prediction(self, model):
        """부정적 감정 예측 테스트."""
        # Given
        negative_text = "이 서비스는 최악입니다."
        
        # When
        result = model.predict(negative_text)
        
        # Then
        assert result['sentiment'] == 'negative'
        assert result['confidence'] > 0.7
    
    def test_batch_prediction(self, model):
        """배치 예측 테스트."""
        # Given
        texts = [
            "좋은 제품입니다",
            "별로입니다",
            "보통입니다"
        ]
        
        # When
        results = model.predict_batch(texts)
        
        # Then
        assert len(results) == 3
        assert all('sentiment' in result for result in results)
        assert all('confidence' in result for result in results)
    
    def test_empty_input_handling(self, model):
        """빈 입력 처리 테스트."""
        # Given
        empty_text = ""
        
        # When & Then
        with pytest.raises(ValueError, match="입력 텍스트가 비어있습니다"):
            model.predict(empty_text)
    
    def test_model_performance(self, model):
        """모델 성능 테스트."""
        # Given
        test_text = "이것은 성능 테스트용 텍스트입니다."
        
        # When
        import time
        start_time = time.time()
        result = model.predict(test_text)
        end_time = time.time()
        
        # Then
        inference_time = end_time - start_time
        assert inference_time < 1.0  # 1초 이내 추론
        assert result is not None
    
    @pytest.mark.slow
    def test_model_accuracy_on_test_set(self, model):
        """테스트 세트에서 모델 정확도 테스트."""
        # Given
        test_data = load_test_dataset()
        
        # When
        predictions = []
        for text, true_label in test_data:
            pred = model.predict(text)
            predictions.append(pred['sentiment'] == true_label)
        
        # Then
        accuracy = sum(predictions) / len(predictions)
        assert accuracy > 0.85  # 85% 이상 정확도
```

## 🔗 통합 테스팅

### API 통합 테스트
```python
import pytest
import requests
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL 테스트 컨테이너."""
    with PostgresContainer("postgres:13") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    """Redis 테스트 컨테이너."""
    with RedisContainer("redis:6") as redis:
        yield redis

@pytest.fixture
def api_client(postgres_container, redis_container):
    """API 클라이언트 설정."""
    # 환경 변수 설정
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()
    os.environ["REDIS_URL"] = redis_container.get_connection_url()
    
    # 애플리케이션 시작
    from src.main import app
    with TestClient(app) as client:
        yield client

class TestUserWorkflow:
    """사용자 워크플로우 통합 테스트."""
    
    def test_complete_user_workflow(self, api_client):
        """완전한 사용자 워크플로우 테스트."""
        # 1. 사용자 생성
        user_data = {
            "email": "integration@example.com",
            "name": "통합 테스트 사용자",
            "password": "password123"
        }
        
        create_response = api_client.post("/api/v1/users", json=user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # 2. 사용자 조회
        get_response = api_client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["email"] == "integration@example.com"
        
        # 3. 사용자 업데이트
        update_data = {"name": "업데이트된 사용자"}
        update_response = api_client.patch(f"/api/v1/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "업데이트된 사용자"
        
        # 4. 사용자 삭제
        delete_response = api_client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204
        
        # 5. 삭제 확인
        get_deleted_response = api_client.get(f"/api/v1/users/{user_id}")
        assert get_deleted_response.status_code == 404
```

## ⚡ 성능 테스팅

### 부하 테스트
```python
import pytest
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """성능 테스트."""
    
    @pytest.mark.slow
    async def test_api_concurrent_requests(self):
        """API 동시 요청 성능 테스트."""
        async def make_request(session, url):
            async with session.get(url) as response:
                return response.status
        
        # Given
        url = "http://localhost:8000/api/v1/health"
        concurrent_requests = 100
        
        # When
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session, url) for _ in range(concurrent_requests)]
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
        
        # Then
        total_time = end_time - start_time
        success_rate = sum(1 for status in results if status == 200) / len(results)
        
        assert success_rate > 0.95  # 95% 이상 성공률
        assert total_time < 10.0    # 10초 이내 완료
        
        print(f"동시 요청 {concurrent_requests}개, 총 시간: {total_time:.2f}초")
        print(f"성공률: {success_rate:.2%}")
    
    def test_database_query_performance(self, db_session):
        """데이터베이스 쿼리 성능 테스트."""
        # Given
        # 테스트 데이터 생성
        users = [User(email=f"user{i}@example.com", name=f"User {i}") 
                for i in range(1000)]
        db_session.add_all(users)
        db_session.commit()
        
        # When
        import time
        start_time = time.time()
        result = db_session.query(User).filter(User.email.like("%user%")).limit(100).all()
        end_time = time.time()
        
        # Then
        query_time = end_time - start_time
        assert query_time < 0.1  # 100ms 이내
        assert len(result) == 100
```

## 🤖 테스트 자동화

### GitHub Actions 워크플로우
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Install dependencies
      run: |
        source $HOME/.cargo/env
        uv pip install -e ".[dev,test]"
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml --cov-report=html
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  kotlin-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Run tests
      run: |
        cd frontend
        ./gradlew test
        ./gradlew jacocoTestReport
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: frontend/build/reports/
```

### 테스트 실행 스크립트
```bash
#!/bin/bash
# scripts/run_tests.sh

set -e

echo "🧪 테스트 실행 시작..."

# Python 테스트
echo "🐍 Python 테스트 실행..."
cd backend
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
cd ..

# Kotlin 테스트
echo "📱 Kotlin 테스트 실행..."
cd frontend
./gradlew test
cd ..

# AI 모델 테스트
echo "🤖 AI 모델 테스트 실행..."
cd ai-model
pytest tests/ -v
cd ..

echo "✅ 모든 테스트 완료!"
```

---

**철저한 테스트를 통해 안정적이고 신뢰할 수 있는 애플리케이션을 만들어보세요! 테스트는 코드의 품질을 보장하는 가장 중요한 도구입니다.** 🚀
