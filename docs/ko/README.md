# SWPP AI Application - 한국어 문서

SWPP AI Application 프로젝트의 한국어 문서에 오신 것을 환영합니다. 이 포괄적인 가이드는 AI 기반 모바일 애플리케이션을 이해하고, 개발하고, 기여하는 데 도움이 될 것입니다.

## 📋 목차

- [빠른 시작](#빠른-시작)
- [프로젝트 개요](#프로젝트-개요)
- [개발 가이드라인](#개발-가이드라인)
- [버전 관리](#버전-관리)
- [API 문서](#api-문서)
- [배포](#배포)
- [지원](#지원)

## 🚀 빠른 시작

### 새로운 개발자를 위한 가이드
1. **환경 설정**: [development/SETUP.md](development/SETUP.md)에서 시작하세요
2. **코딩 표준**: [development/CONVENTIONS.md](development/CONVENTIONS.md)를 검토하세요
3. **Git 워크플로우**: [development/GIT_WORKFLOW.md](development/GIT_WORKFLOW.md)에서 워크플로우를 이해하세요
4. **테스팅**: [development/TESTING.md](development/TESTING.md)에서 테스팅 실습을 학습하세요

### 버전 관리를 위한 가이드
1. **커밋 규칙**: [version-control/COMMIT_RULES.md](version-control/COMMIT_RULES.md)에서 커밋 표준을 학습하세요
2. **PR 가이드라인**: [version-control/PR_RULES.md](version-control/PR_RULES.md)에서 PR 프로세스를 따르세요
3. **브랜치 전략**: [version-control/BRANCH_STRATEGY.md](version-control/BRANCH_STRATEGY.md)에서 브랜치 전략을 이해하세요

### 필수 명령어
```bash
# 개발 환경 설정
./scripts/setup/setup_dev_environment.sh

# 커밋 전 코드 포맷팅
make format

# 테스트 실행
make test

# 개발 시작
make dev
```

## 📋 프로젝트 개요

### 🏗️ 아키텍처

이것은 세 가지 주요 구성 요소를 가진 AI 기반 모바일 애플리케이션입니다:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   프론트엔드     │    │    백엔드       │    │   AI 모델      │
│   (Kotlin)      │◄──►│   (FastAPI)     │◄──►│   (PyTorch)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🛠️ 기술 스택

#### 백엔드
- **Python 3.8+** FastAPI 프레임워크 사용
- **PostgreSQL** 데이터 지속성을 위한 데이터베이스
- **Redis** 캐싱 및 메시지 큐잉
- **Celery** 백그라운드 작업 처리
- **SQLAlchemy** ORM

#### 프론트엔드
- **Kotlin** 안드로이드 개발
- **Android SDK** (API 레벨 21+)
- **Jetpack Compose** 모던 UI
- **Retrofit** API 통신

#### AI/ML
- **PyTorch** 딥러닝 모델
- **Transformers** NLP 기능
- **NumPy & Pandas** 데이터 처리
- **Jupyter** 모델 개발

#### DevOps
- **uv** Python 패키지 관리
- **Docker** 컨테이너화
- **GitHub Actions** CI/CD
- **Pre-commit hooks** 코드 품질 관리

## 📚 개발 가이드라인

### 핵심 문서
- **[CONVENTIONS.md](development/CONVENTIONS.md)** - 코딩 표준 및 모범 사례 (**필독**)
- **[GIT_WORKFLOW.md](development/GIT_WORKFLOW.md)** - Git 워크플로우 및 브랜치 전략 (**필독**)
- **[SETUP.md](development/SETUP.md)** - 완전한 개발 환경 설정
- **[TESTING.md](development/TESTING.md)** - 테스팅 가이드라인 및 실습

### 코드 품질 표준
- **Python**: Black, isort, flake8, mypy, bandit
- **Kotlin**: ktlint, detekt
- **Pre-commit hooks**: 자동 코드 품질 검사
- **테스트 커버리지**: 최소 80% 커버리지 필요

## 🔄 버전 관리

### 필수 문서
- **[COMMIT_RULES.md](version-control/COMMIT_RULES.md)** - 커밋 메시지 표준 및 규칙
- **[PR_RULES.md](version-control/PR_RULES.md)** - 풀 리퀘스트 가이드라인 및 템플릿
- **[BRANCH_STRATEGY.md](version-control/BRANCH_STRATEGY.md)** - 상세 브랜치 전략

### 브랜치 전략 개요
- **`main`**: 프로덕션 준비 코드 (보호됨)
- **`dev`**: 기능 통합 브랜치 (보호됨)
- **`feature/*`**: 새로운 기능 및 개선사항
- **`bugfix/*`**: 버그 수정
- **`hotfix/*`**: 중요한 프로덕션 수정

### 워크플로우 요약
1. `dev`에서 기능 브랜치 생성
2. 커밋 메시지 규칙 준수
3. 코드 포매터 및 테스트 실행
4. `dev` 브랜치로 PR 생성
5. 코드 리뷰 승인 받기
6. 통합 테스트를 위해 `dev`로 병합
7. 프로덕션을 위해 `main`으로 배포

## 📖 API 문서

### 백엔드 API
- **[backend-api.md](api/backend-api.md)** - REST API 엔드포인트 및 스키마
- **OpenAPI/Swagger**: 백엔드 실행 시 `/docs`에서 사용 가능
- **인증**: JWT 기반 인증 시스템

### AI 모델 API
- **[ai-model-api.md](api/ai-model-api.md)** - ML 모델 추론 엔드포인트
- **모델 서빙**: FastAPI 기반 모델 서빙
- **배치 처리**: Celery 기반 백그라운드 처리

## 🚀 배포

### 개발 환경
- **로컬 개발**: uv를 사용한 가상 환경
- **Docker Compose**: 다중 서비스 로컬 환경
- **핫 리로드**: 자동 코드 리로딩

### 프로덕션
- **[DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - 프로덕션 배포 절차
- **[INFRASTRUCTURE.md](deployment/INFRASTRUCTURE.md)** - 인프라 설정 및 요구사항
- **컨테이너화**: 모든 서비스를 위한 Docker 이미지
- **모니터링**: Prometheus 및 Grafana 통합

## 🔧 개발 도구

### 코드 포매터
```bash
# Python 코드 포맷팅
./scripts/formatters/format_python.py

# Kotlin 코드 포맷팅
./scripts/formatters/format_kotlin.sh

# 모든 코드 포맷팅
./scripts/formatters/format_all.sh
```

### 테스팅
```bash
# 모든 테스트 실행
make test

# Python 테스트만 실행
make test-python

# Kotlin 테스트만 실행
make test-kotlin

# 커버리지와 함께 실행
make test-coverage
```

### 패키지 관리
```bash
# uv로 의존성 설치
uv pip install -r requirements.txt

# 새 의존성 추가
uv add package-name

# 의존성 업데이트
uv pip compile requirements.in
```

## 📊 프로젝트 상태

- ✅ 프로젝트 구조 및 도구 설정
- ✅ 개발 환경 구성
- ✅ 코드 품질 도구 및 pre-commit hooks
- ✅ 포괄적인 문서 (한국어/영어)
- ✅ 버전 관리 가이드라인 및 템플릿
- 🚧 백엔드 API 개발
- 🚧 AI 모델 구현
- 🚧 프론트엔드 모바일 애플리케이션
- ⏳ 통합 테스팅
- ⏳ 프로덕션 배포

## 📞 지원

### 도움 받기
1. **문서**: 먼저 이 문서를 확인하세요
2. **이슈 검색**: 기존 GitHub 이슈를 살펴보세요
3. **이슈 생성**: 버그 리포트나 기능 요청을 위해 이슈 템플릿을 사용하세요
4. **팀 토론**: 질문을 위해 GitHub Discussions를 사용하세요
5. **직접 연락**: 긴급한 사안은 팀 멤버에게 연락하세요

### 이슈 템플릿
- **버그 리포트**: 버그 및 이슈 보고용
- **기능 요청**: 새로운 기능 제안용
- **문서**: 문서 개선용
- **질문**: 일반적인 질문 및 토론용

## 🤝 기여하기

### 시작하기 전에
1. 코딩 표준을 위해 [CONVENTIONS.md](development/CONVENTIONS.md)를 읽으세요
2. 워크플로우를 위해 [GIT_WORKFLOW.md](development/GIT_WORKFLOW.md)를 이해하세요
3. 커밋 표준을 위해 [COMMIT_RULES.md](version-control/COMMIT_RULES.md)를 검토하세요
4. 풀 리퀘스트 가이드라인을 위해 [PR_RULES.md](version-control/PR_RULES.md)를 확인하세요

### 기여 프로세스
1. 저장소 포크 (외부 기여자인 경우)
2. 기능 브랜치 생성: `git checkout -b feature/your-feature-name`
3. 코딩 규칙을 따르고 테스트 작성
4. 관례적 커밋 메시지로 커밋
5. 브랜치 푸시 및 풀 리퀘스트 생성
6. 코드 리뷰 피드백 처리
7. 승인 후 병합

### 코드 리뷰 체크리스트
- [ ] 코드가 프로젝트 규칙을 따름
- [ ] 테스트가 작성되고 통과함
- [ ] 문서가 업데이트됨
- [ ] 보안 취약점이 없음
- [ ] 성능 고려사항이 처리됨
- [ ] 커밋 메시지가 규칙을 따름

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스됩니다 - 자세한 내용은 [LICENSE](../../LICENSE) 파일을 참조하세요.

---

**기여할 준비가 되셨나요? [개발 설정 가이드](development/SETUP.md)에서 시작하세요!** 🚀
