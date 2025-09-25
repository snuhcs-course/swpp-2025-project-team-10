# 개발 규칙 및 코딩 표준

이 문서는 SWPP AI Application 프로젝트의 코딩 표준, 모범 사례, 개발 규칙을 정의합니다.

## 📋 목차

- [일반 원칙](#일반-원칙)
- [Python 코딩 표준](#python-코딩-표준)
- [Kotlin 코딩 표준](#kotlin-코딩-표준)
- [데이터베이스 규칙](#데이터베이스-규칙)
- [API 설계 원칙](#api-설계-원칙)
- [보안 가이드라인](#보안-가이드라인)
- [성능 고려사항](#성능-고려사항)
- [문서화 표준](#문서화-표준)

## 🎯 일반 원칙

### 코드 품질 원칙
1. **가독성**: 코드는 명확하고 이해하기 쉬워야 합니다
2. **일관성**: 프로젝트 전체에서 일관된 스타일을 유지합니다
3. **단순성**: 복잡함보다는 단순함을 추구합니다
4. **재사용성**: 중복을 피하고 재사용 가능한 컴포넌트를 작성합니다
5. **테스트 가능성**: 모든 코드는 테스트 가능하게 작성합니다

### 개발 워크플로우
1. **기능 브랜치**: 모든 개발은 기능 브랜치에서 수행
2. **코드 리뷰**: 모든 변경사항은 코드 리뷰를 거침
3. **자동화된 테스트**: CI/CD 파이프라인에서 자동 테스트 실행
4. **문서 업데이트**: 코드 변경 시 관련 문서도 함께 업데이트

## 🐍 Python 코딩 표준

### 스타일 가이드
- **PEP 8** 준수
- **Black** 포매터 사용 (라인 길이: 88자)
- **isort** 임포트 정렬
- **Type hints** 모든 함수와 메서드에 사용

### 코드 구조
```python
"""모듈 독스트링: 모듈의 목적과 사용법 설명."""

from typing import Optional, List, Dict
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import User
from .schemas import UserCreate, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스 클래스."""
    
    def __init__(self, db: Session) -> None:
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """새로운 사용자를 생성합니다.
        
        Args:
            user_data: 사용자 생성 데이터
            
        Returns:
            생성된 사용자 정보
            
        Raises:
            HTTPException: 사용자 생성 실패 시
        """
        try:
            # 구현 로직
            pass
        except Exception as e:
            logger.error(f"사용자 생성 실패: {e}")
            raise HTTPException(status_code=500, detail="사용자 생성 실패")
```

### 명명 규칙
- **변수/함수**: `snake_case`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **모듈**: `lowercase` 또는 `snake_case`
- **패키지**: `lowercase`

### 에러 처리
```python
# 좋은 예
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"특정 오류 발생: {e}")
    raise HTTPException(status_code=400, detail="요청 처리 실패")
except Exception as e:
    logger.error(f"예상치 못한 오류: {e}")
    raise HTTPException(status_code=500, detail="내부 서버 오류")

# 나쁜 예
try:
    result = risky_operation()
except:  # 너무 광범위한 예외 처리
    pass  # 에러 무시
```

### 로깅
```python
import logging

logger = logging.getLogger(__name__)

# 로그 레벨 사용
logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고 메시지")
logger.error("오류 발생")
logger.critical("심각한 오류")

# 구조화된 로깅
logger.info(
    "사용자 생성 완료",
    extra={
        "user_id": user.id,
        "email": user.email,
        "action": "user_created"
    }
)
```

### 테스팅
```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """UserService 테스트 클래스."""
    
    @pytest.fixture
    def user_service(self, db_session):
        return UserService(db_session)
    
    async def test_create_user_success(self, user_service):
        """사용자 생성 성공 테스트."""
        # Given
        user_data = UserCreate(email="test@example.com", name="테스트")
        
        # When
        result = await user_service.create_user(user_data)
        
        # Then
        assert result.email == "test@example.com"
        assert result.name == "테스트"
    
    async def test_create_user_failure(self, user_service):
        """사용자 생성 실패 테스트."""
        # Given
        invalid_data = UserCreate(email="", name="")
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(invalid_data)
        
        assert exc_info.value.status_code == 400
```

## 📱 Kotlin 코딩 표준

### 스타일 가이드
- **Kotlin 공식 스타일 가이드** 준수
- **ktlint** 포매터 사용
- **detekt** 정적 분석 도구 사용

### 코드 구조
```kotlin
/**
 * 사용자 관련 데이터를 관리하는 Repository 클래스
 */
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao
) {
    
    /**
     * 사용자 정보를 가져옵니다.
     * 
     * @param userId 사용자 ID
     * @return 사용자 정보 또는 null
     */
    suspend fun getUser(userId: String): Result<User> = try {
        val response = apiService.getUser(userId)
        if (response.isSuccessful) {
            response.body()?.let { user ->
                userDao.insertUser(user.toEntity())
                Result.success(user)
            } ?: Result.failure(Exception("사용자 데이터가 없습니다"))
        } else {
            Result.failure(Exception("API 호출 실패: ${response.code()}"))
        }
    } catch (e: Exception) {
        Log.e(TAG, "사용자 정보 가져오기 실패", e)
        Result.failure(e)
    }
    
    companion object {
        private const val TAG = "UserRepository"
    }
}
```

### 명명 규칙
- **변수/함수**: `camelCase`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **패키지**: `lowercase.with.dots`

### 널 안전성
```kotlin
// 좋은 예
fun processUser(user: User?): String {
    return user?.name?.takeIf { it.isNotBlank() } ?: "알 수 없는 사용자"
}

// 안전한 캐스팅
val userString = data as? String ?: return

// 엘비스 연산자 활용
val result = repository.getUser(id) ?: throw UserNotFoundException()

// 나쁜 예
fun processUser(user: User?): String {
    return user!!.name  // 강제 언래핑 위험
}
```

### 코루틴 사용
```kotlin
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()
    
    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            
            userRepository.getUser(userId)
                .onSuccess { user ->
                    _uiState.value = UserUiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UserUiState.Error(error.message ?: "오류 발생")
                }
        }
    }
}
```

### Compose UI
```kotlin
@Composable
fun UserProfile(
    user: User,
    onEditClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = user.name,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            
            Text(
                text = user.email,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Button(
                onClick = onEditClick,
                modifier = Modifier.align(Alignment.End)
            ) {
                Text("편집")
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun UserProfilePreview() {
    MyAppTheme {
        UserProfile(
            user = User(
                id = "1",
                name = "홍길동",
                email = "hong@example.com"
            ),
            onEditClick = {}
        )
    }
}
```

## 🗄️ 데이터베이스 규칙

### 테이블 명명 규칙
- **테이블명**: `snake_case` (복수형)
- **컬럼명**: `snake_case`
- **인덱스명**: `idx_table_column`
- **외래키명**: `fk_table_referenced_table`

### 스키마 설계
```sql
-- 좋은 예
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 나쁜 예
CREATE TABLE User (  -- 대문자, 단수형
    ID INT,          -- 타입 부적절
    Email TEXT,      -- 제약 조건 없음
    Name TEXT
);
```

### 마이그레이션
```python
"""사용자 테이블 생성

Revision ID: 001_create_users_table
Revises: 
Create Date: 2024-01-01 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_create_users_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """사용자 테이블 생성."""
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    """사용자 테이블 삭제."""
    op.drop_index('idx_users_email', 'users')
    op.drop_table('users')
```

## 🌐 API 설계 원칙

### RESTful API 설계
```python
# 좋은 예
GET    /api/v1/users           # 사용자 목록 조회
GET    /api/v1/users/{id}      # 특정 사용자 조회
POST   /api/v1/users           # 사용자 생성
PUT    /api/v1/users/{id}      # 사용자 전체 업데이트
PATCH  /api/v1/users/{id}      # 사용자 부분 업데이트
DELETE /api/v1/users/{id}      # 사용자 삭제

# 나쁜 예
GET    /api/getUsers           # 동사 사용
POST   /api/user/create        # 불필요한 동사
GET    /api/users/delete/{id}  # GET으로 삭제
```

### 응답 형식
```python
# 성공 응답
{
    "success": true,
    "data": {
        "id": "123",
        "name": "홍길동",
        "email": "hong@example.com"
    },
    "message": "사용자 조회 성공"
}

# 에러 응답
{
    "success": false,
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "사용자를 찾을 수 없습니다",
        "details": {
            "user_id": "123"
        }
    }
}

# 페이지네이션
{
    "success": true,
    "data": [...],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 100,
        "total_pages": 5
    }
}
```

### 상태 코드 사용
- **200 OK**: 성공적인 GET, PUT, PATCH
- **201 Created**: 성공적인 POST
- **204 No Content**: 성공적인 DELETE
- **400 Bad Request**: 잘못된 요청
- **401 Unauthorized**: 인증 필요
- **403 Forbidden**: 권한 없음
- **404 Not Found**: 리소스 없음
- **500 Internal Server Error**: 서버 오류

## 🔒 보안 가이드라인

### 인증 및 권한
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> User:
    """현재 사용자 정보를 가져옵니다."""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰"
            )
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 검증 실패"
        )

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """사용자 프로필 조회."""
    return current_user
```

### 입력 검증
```python
from pydantic import BaseModel, validator, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('이름은 2자 이상이어야 합니다')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상이어야 합니다')
        if not any(c.isupper() for c in v):
            raise ValueError('비밀번호에 대문자가 포함되어야 합니다')
        return v
```

### 민감한 정보 처리
```python
import os
from cryptography.fernet import Fernet

# 환경 변수에서 키 로드
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_sensitive_data(data: str) -> str:
    """민감한 데이터를 암호화합니다."""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """암호화된 데이터를 복호화합니다."""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

# 로그에서 민감한 정보 제외
def safe_log_user(user: User):
    logger.info(f"사용자 처리: {user.id}, 이메일: {user.email[:3]}***")
```

## ⚡ 성능 고려사항

### 데이터베이스 최적화
```python
# 좋은 예: 필요한 필드만 선택
users = session.query(User.id, User.name).filter(User.active == True).all()

# N+1 문제 해결
users = session.query(User).options(joinedload(User.posts)).all()

# 페이지네이션
def get_users_paginated(page: int, size: int):
    offset = (page - 1) * size
    return session.query(User).offset(offset).limit(size).all()

# 나쁜 예: 모든 데이터 로드
users = session.query(User).all()  # 메모리 부족 위험
```

### 캐싱
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=128)
def get_user_permissions(user_id: str) -> List[str]:
    """사용자 권한을 캐시와 함께 조회합니다."""
    cache_key = f"user_permissions:{user_id}"
    
    # Redis에서 캐시 확인
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 데이터베이스에서 조회
    permissions = fetch_permissions_from_db(user_id)
    
    # 캐시에 저장 (1시간)
    redis_client.setex(cache_key, 3600, json.dumps(permissions))
    
    return permissions
```

## 📚 문서화 표준

### 코드 문서화
```python
def calculate_user_score(
    user_id: str,
    include_bonus: bool = False,
    weight_factor: float = 1.0
) -> float:
    """사용자 점수를 계산합니다.
    
    사용자의 활동 데이터를 기반으로 점수를 계산하며,
    선택적으로 보너스 점수와 가중치를 적용할 수 있습니다.
    
    Args:
        user_id: 점수를 계산할 사용자 ID
        include_bonus: 보너스 점수 포함 여부 (기본값: False)
        weight_factor: 점수 가중치 (기본값: 1.0)
        
    Returns:
        계산된 사용자 점수 (0.0 ~ 100.0)
        
    Raises:
        UserNotFoundException: 사용자를 찾을 수 없는 경우
        ValueError: weight_factor가 0 이하인 경우
        
    Example:
        >>> score = calculate_user_score("user123", include_bonus=True)
        >>> print(f"사용자 점수: {score}")
        사용자 점수: 85.5
    """
    if weight_factor <= 0:
        raise ValueError("가중치는 0보다 커야 합니다")
    
    # 구현 로직...
    pass
```

### API 문서화
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="SWPP AI Application API",
    description="AI 기반 모바일 애플리케이션 백엔드 API",
    version="1.0.0"
)

class UserResponse(BaseModel):
    """사용자 응답 모델."""
    id: str
    name: str
    email: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "name": "홍길동",
                "email": "hong@example.com"
            }
        }

@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="사용자 조회",
    description="사용자 ID로 특정 사용자 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 조회 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
        500: {"description": "서버 내부 오류"}
    }
)
async def get_user(user_id: str):
    """사용자 정보를 조회합니다."""
    # 구현 로직...
    pass
```

---

**이 규칙들을 따라 일관되고 고품질의 코드를 작성하세요! 궁금한 점이 있으면 팀에 문의하세요.** 💻
