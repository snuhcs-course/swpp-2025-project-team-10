# Dummy Data Generation

이 디렉토리에는 테스트용 더미 데이터를 생성하는 스크립트가 포함되어 있습니다.

## 🚀 Quick Start

### 전체 실행 순서 (처음 시작하는 경우)

```bash
# 1. backend 디렉토리로 이동
cd backend

# 2. 로그 디렉토리 생성 (에러 방지)
mkdir -p logs

# 3. 데이터베이스 마이그레이션
python manage.py migrate

# 4. 슈퍼유저 생성 (관리자 계정)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (원하는 비밀번호 입력)

# 5. 더미 데이터 생성
python create_dummy_data.py

# 6. 개발 서버 실행
python manage.py runserver
```

### 빠른 실행 (이미 설정이 완료된 경우)

```bash
cd backend
python create_dummy_data.py
```

**테스트 계정:**
- 사용자명: `user1` ~ `user20`
- 비밀번호: `testpass123`

## 개요

테스트 및 개발을 위해 다음과 같은 더미 데이터를 생성합니다:

- **사용자 (Users)**: 프로필, follower/following, GPS 위치 정보 포함
- **사용자 취향 (User Tastes)**: 좋아하는 장르, 작가, 책, 독서 목적 등
- **책 (Books)**: 다양한 조건과 가용성을 가진 책들
- **책 리뷰 (Book Reviews)**: 평점과 내용이 포함된 리뷰
- **게시물 (Posts)**: 홈 피드에 표시될 다양한 유형의 게시물
- **댓글 (Comments)**: 게시물에 대한 댓글과 좋아요
- **북셀프 (Bookshelves/Collections)**: 사용자의 책 컬렉션
- **위시리스트 (Wishlists)**: 읽고 싶은 책 목록
- **읽기 상태 (Reading Statuses)**: 읽는 중, 완독 등의 상태
- **교환 요청 (Barter Requests)**: 책 교환 요청
- **북클럽 (Book Clubs)**: 독서 모임

## 사용 방법

```bash
# backend 디렉토리로 이동
cd backend

# 더미 데이터 생성
python create_dummy_data.py
```

스크립트는 다음 데이터를 자동으로 생성합니다:
- 20명의 사용자 (user1 ~ user20)
- 50권의 책
- 30개의 리뷰
- 40개의 게시물
- 50개의 댓글
- 위시리스트, 컬렉션, 읽기 상태 등

> **참고:** 스크립트 내부의 `count` 변수를 수정하여 생성할 데이터 수를 조정할 수 있습니다.

## 생성되는 데이터 상세

### 사용자 (Users)
- 20명의 테스트 사용자 (기본값)
- 사용자명: `user1`, `user2`, ..., `user20`
- 비밀번호: 모두 `testpass123`
- 이메일: `user1@example.com`, `user2@example.com`, ...
- 프로필 정보: 이름, 자기소개, 위치, 생년월일
- GPS 위치: 서울 주변의 랜덤한 좌표
- 평판 점수와 성공적인 거래 횟수
- 각 사용자는 3-8명을 팔로우

### 사용자 취향 (User Tastes)
- 좋아하는 장르 (2-4개)
- 좋아하는 작가 (2-4명)
- 좋아하는 책 (2-3권)
- 선호하는 책 길이 (짧음/보통/두꺼움)
- 선호하는 분위기 (2-4개)
- 독서 목적 (2-3개)
- 선호하는 교환 장소 정보

### 책 (Books)
- 50권의 책 (기본값)
- 다양한 장르와 작가
- 상태: 새책, 거의 새책, 매우 좋음, 좋음, 괜찮음
- 가용성: 이용 가능, 대기 중, 교환 완료, 이용 불가
- 각 책마다 소유자, 출판사, 장르, 작가 정보
- 평균 평점과 리뷰 수

### 책 리뷰 (Book Reviews)
- 30개의 리뷰 (기본값)
- 평점 (3-5점)
- 제목과 내용
- 좋아요 (helpful votes) 0-10개

### 게시물 (Posts)
- 40개의 게시물 (기본값)
- 유형: 텍스트, 책 리뷰, 책 추천, 읽기 업데이트, 교환 성공
- 관련 책 정보 (선택적)
- 좋아요 0-15개

### 댓글 (Comments)
- 50개의 댓글 (기본값)
- 게시물에 대한 댓글
- 좋아요 0-5개

### 위시리스트 (Wishlists)
- 각 사용자당 3-7권의 책
- 우선순위 (1-5)
- 개인 메모

### 컬렉션 (Collections)
- 10명의 사용자가 각각 컬렉션 보유
- 각 컬렉션에 3-8권의 책
- 공개/비공개 설정

### 읽기 상태 (Reading Statuses)
- 각 사용자당 5-12권의 책
- 상태: 읽고 싶음, 읽는 중, 완독, 중단
- 읽은 페이지 수, 시작일, 완료일
- 개인 평점

### 교환 요청 (Barter Requests)
- 15개의 교환 요청
- 상태: 대기 중, 수락됨, 거절됨, 완료됨
- 제안된 만남 장소와 시간
- 교환할 책 정보

### 북클럽 (Book Clubs)
- 5개의 북클럽
- 각 클럽당 5-15명의 회원
- 현재 읽고 있는 책 정보

## 🔑 테스트 계정 정보

생성된 사용자로 로그인하려면:

| 항목 | 값 |
|------|-----|
| **사용자명** | `user1`, `user2`, `user3`, ..., `user20` |
| **이메일** | `user1@example.com`, `user2@example.com`, ... |
| **비밀번호** | `testpass123` (모든 사용자 동일) |

### 로그인 예시:
```
Username: user1
Password: testpass123
```

또는

```
Email: user1@example.com
Password: testpass123
```

## 주의사항

⚠️ **경고**: `--clear` 옵션을 사용하면 데이터베이스의 모든 사용자 데이터, 책, 게시물, 댓글 등이 삭제됩니다! 
슈퍼유저(관리자) 계정은 삭제되지 않으니 안심하세요.

## 개발 팁

1. **테스트 환경에서만 사용**: 이 스크립트는 개발 및 테스트 환경에서만 사용하세요.
2. **데이터 초기화**: 새로운 테스트를 시작하려면 `--clear` 옵션을 사용하세요.
3. **커스텀 데이터**: 필요에 따라 스크립트를 수정하여 특정 테스트 케이스에 맞는 데이터를 생성할 수 있습니다.

## 문제 해결

### 에러 발생 시

#### 1. `FileNotFoundError: logs/django.log` 에러
```bash
# 로그 디렉토리 생성
mkdir -p logs
```

#### 2. 마이그레이션 에러
```bash
# 마이그레이션이 모두 적용되었는지 확인
python manage.py migrate
```

#### 3. 데이터베이스 연결 에러
```bash
# 데이터베이스 연결 확인
python manage.py check
```

#### 4. 기존 데이터와 충돌 시
```bash
# --clear 옵션으로 기존 데이터 삭제 후 재생성
python manage.py create_dummy_data --clear
```

### 데이터가 생성되지 않을 때

- Django 설정이 올바른지 확인
- 필요한 앱들이 모두 INSTALLED_APPS에 등록되어 있는지 확인
- 데이터베이스에 쓰기 권한이 있는지 확인

## 스크립트 수정

더미 데이터의 내용을 커스터마이징하려면:

1. `backend/core/management/commands/create_dummy_data.py` 파일을 수정
2. 각 생성 함수 (`create_users`, `create_books`, 등)의 데이터를 변경
3. 필요한 경우 새로운 생성 함수를 추가

## 라이선스

이 스크립트는 프로젝트의 테스트 및 개발 목적으로만 사용됩니다.
