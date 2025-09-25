# SWPP AI Application - Documentation

Welcome to the SWPP AI Application project documentation. This directory contains comprehensive documentation in both Korean and English.

## 🌐 Language Selection / 언어 선택

### 📖 English Documentation
- **[English Documentation](en/README.md)** - English documentations
- **Target Audience**: International developers, code reviewers, open source contributors

### 📖 한국어 문서
- **[한국어 문서](ko/README.md)** - 한국어 문서
- **대상**: 한국어를 사용하는 개발자, 팀 멤버, 학생

## 📁 Documentation Structure / 문서 구조

```
docs/
├── README.md                    # This file - language selection
├── en/                         # English documentation
│   ├── README.md               # English documentation overview
│   ├── development/            # Development guidelines
│   │   ├── CONVENTIONS.md      # Coding standards and conventions
│   │   ├── GIT_WORKFLOW.md     # Git workflow and branching strategy
│   │   ├── SETUP.md            # Development environment setup
│   │   └── TESTING.md          # Testing guidelines and practices
│   ├── version-control/        # Version control guidelines
│   │   ├── COMMIT_RULES.md     # Commit message rules and standards
│   │   ├── PR_RULES.md         # Pull request guidelines and templates
│   │   └── BRANCH_STRATEGY.md  # Detailed branching strategy
│   ├── api/                    # API documentation
│   │   ├── backend-api.md      # Backend API documentation
│   │   └── ai-model-api.md     # AI model API documentation
│   └── deployment/             # Deployment and infrastructure
│       ├── DEPLOYMENT.md       # Deployment procedures
│       └── INFRASTRUCTURE.md   # Infrastructure setup and requirements
└── ko/                         # Korean documentation
    ├── README.md               # 한국어 문서 개요
    ├── development/            # 개발 가이드라인
    │   ├── CONVENTIONS.md      # 코딩 표준 및 규칙
    │   ├── GIT_WORKFLOW.md     # Git 워크플로우 및 브랜치 전략
    │   ├── SETUP.md            # 개발 환경 설정
    │   └── TESTING.md          # 테스팅 가이드라인 및 실습
    ├── version-control/        # 버전 관리 가이드라인
    │   ├── COMMIT_RULES.md     # 커밋 메시지 규칙 및 표준
    │   ├── PR_RULES.md         # 풀 리퀘스트 가이드라인 및 템플릿
    │   └── BRANCH_STRATEGY.md  # 상세 브랜치 전략
    ├── api/                    # API 문서
    │   ├── backend-api.md      # 백엔드 API 문서
    │   └── ai-model-api.md     # AI 모델 API 문서
    └── deployment/             # 배포 및 인프라
        ├── DEPLOYMENT.md       # 배포 절차
        └── INFRASTRUCTURE.md   # 인프라 설정 및 요구사항
```

## 🚀 Quick Start / 빠른 시작

### For English Speakers
1. **New Developer Setup**: Start with [en/development/SETUP.md](en/development/SETUP.md)
2. **Coding Standards**: Review [en/development/CONVENTIONS.md](en/development/CONVENTIONS.md)
3. **Git Workflow**: Understand our workflow in [en/development/GIT_WORKFLOW.md](en/development/GIT_WORKFLOW.md)
4. **Commit Rules**: Learn commit standards in [en/version-control/COMMIT_RULES.md](en/version-control/COMMIT_RULES.md)
5. **PR Guidelines**: Follow PR process in [en/version-control/PR_RULES.md](en/version-control/PR_RULES.md)

### 한국어 사용자를 위한 가이드
1. **새 개발자 설정**: [ko/development/SETUP.md](ko/development/SETUP.md)에서 시작하세요
2. **코딩 표준**: [ko/development/CONVENTIONS.md](ko/development/CONVENTIONS.md)를 검토하세요
3. **Git 워크플로우**: [ko/development/GIT_WORKFLOW.md](ko/development/GIT_WORKFLOW.md)에서 워크플로우를 이해하세요
4. **커밋 규칙**: [ko/version-control/COMMIT_RULES.md](ko/version-control/COMMIT_RULES.md)에서 커밋 표준을 학습하세요
5. **PR 가이드라인**: [ko/version-control/PR_RULES.md](ko/version-control/PR_RULES.md)에서 PR 프로세스를 따르세요

## 📋 Project Overview / 프로젝트 개요

### 🏗️ Architecture / 아키텍처

This is an AI-powered application with the following components:
이것은 다음 구성 요소를 가진 AI 기반 애플리케이션입니다:

- **Backend** (`backend/`): FastAPI-based REST API server / FastAPI 기반 REST API 서버
- **Frontend** (`frontend/`): Kotlin-based mobile application / Kotlin 기반 모바일 애플리케이션
- **AI Model** (`ai-model/`): Machine learning models and training code / 머신러닝 모델 및 훈련 코드
- **Scripts** (`scripts/`): Automation and utility scripts / 자동화 및 유틸리티 스크립트
- **Tools** (`tools/`): Development tools and linting configurations / 개발 도구 및 린팅 설정

### 🛠️ Technology Stack / 기술 스택

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Kotlin, Android SDK
- **AI/ML**: PyTorch, Transformers, NumPy, Pandas
- **DevOps**: Docker, GitHub Actions, pre-commit hooks
- **Code Quality**: Black, isort, flake8, mypy, ktlint, detekt
- **Package Management**: uv for Python, Gradle for Kotlin

## 🔧 Development Tools / 개발 도구

### Code Formatters / 코드 포매터
- **Python**: `./scripts/formatters/format_python.py`
- **Kotlin**: `./scripts/formatters/format_kotlin.sh`
- **All**: `./scripts/formatters/format_all.sh`

### Pre-commit Hooks / 프리커밋 훅
Pre-commit hooks are automatically installed and will run code formatters before each commit.
프리커밋 훅이 자동으로 설치되며 각 커밋 전에 코드 포매터를 실행합니다.

## 📞 Support / 지원

For questions or issues / 질문이나 문제가 있는 경우:
1. Check the relevant documentation first / 먼저 관련 문서를 확인합니다.
2. Search existing GitHub issues / 기존 GitHub 이슈에 관련 내용이 있는지 확인합니다.
3. Create a new issue with detailed information / 자세한 정보와 이슈 티켓을 등록합니다.

## 📝 Contributing / 기여

Please read our development conventions and git workflow before contributing to the project.
프로젝트에 참여하기 전에 개발 규칙과 git 워크플로우 읽기를 권장합니다.

- **English**: [en/development/CONVENTIONS.md](en/development/CONVENTIONS.md) and [en/development/GIT_WORKFLOW.md](en/development/GIT_WORKFLOW.md)
- **한국어**: [ko/development/CONVENTIONS.md](ko/development/CONVENTIONS.md) 및 [ko/development/GIT_WORKFLOW.md](ko/development/GIT_WORKFLOW.md)
