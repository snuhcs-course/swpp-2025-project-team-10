# 개발 환경 설정 가이드

이 가이드는 SWPP AI Application 프로젝트의 개발 환경을 설정하는 방법을 설명합니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [초기 설정](#초기-설정)
- [백엔드 설정](#백엔드-설정)
- [프론트엔드 설정](#프론트엔드-설정)
- [AI 모델 설정](#ai-모델-설정)
- [개발 도구](#개발-도구)
- [검증](#검증)
- [문제 해결](#문제-해결)

## 🔧 사전 요구사항

개발을 시작하기 전에 다음 도구들을 설치해야 합니다:

### 필수 도구

#### Git
```bash
# macOS
brew install git

# Ubuntu
sudo apt install git

# 설치 확인
git --version  # 2.30 이상이어야 함
```

#### Python 3.8+ 및 uv
```bash
# macOS
brew install python@3.11

# Ubuntu
sudo apt install python3.11 python3.11-pip python3.11-venv

# uv 설치 (빠른 Python 패키지 관리자)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 pip로 설치
pip install uv

# 설치 확인
python3 --version  # 3.8 이상이어야 함
uv --version       # uv 버전 표시
```

#### Node.js 18+
```bash
# macOS
brew install node@18

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 설치 확인
node --version  # v18.0.0 이상이어야 함
npm --version   # 8.0.0 이상이어야 함
```

#### Docker 및 Docker Compose
```bash
# macOS
brew install --cask docker

# Ubuntu
sudo apt install docker.io docker-compose

# 설치 확인
docker --version
docker-compose --version
```

### 선택적 도구

#### Java 17+ (Android 개발용)
```bash
# macOS
brew install openjdk@17

# Ubuntu
sudo apt install openjdk-17-jdk

# 설치 확인
java --version  # 17.0.0 이상이어야 함
```

#### Android Studio
- [공식 웹사이트](https://developer.android.com/studio)에서 다운로드
- Android SDK 및 도구 설치
- 환경 변수 설정

## 🚀 초기 설정

### 1. 저장소 클론
```bash
git clone https://github.com/snuhcs-course/swpp-2025-project-team-10.git
cd swpp-2025-project-team-10
```

### 2. 자동 설정 스크립트 실행
```bash
# 개발 환경 자동 설정
./scripts/setup/setup_dev_environment.sh

# 스크립트가 다음을 수행합니다:
# - Python 가상환경 생성 (uv 사용)
# - 의존성 설치
# - Pre-commit hooks 설정
# - 개발 도구 구성
```

### 3. 환경 변수 설정
```bash
# 환경 변수 파일 복사
cp .env.example .env

# 필요한 값들로 .env 파일 편집
# - 데이터베이스 연결 정보
# - API 키
# - 시크릿 키
```

## 🐍 백엔드 설정

### 1. Python 가상환경 활성화
```bash
# 가상환경 활성화
source venv/bin/activate

# Windows에서는:
# venv\Scripts\activate
```

### 2. uv로 의존성 설치
```bash
# uv를 사용한 개발 의존성 설치 (더 빠름)
uv pip install -e ".[dev]"

# 또는 requirements 파일에서 설치
uv pip install -r backend/requirements.txt
uv pip install -r backend/requirements-dev.txt

# 대안: uv로 생성 및 동기화
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip sync requirements.txt
```

### 3. 데이터베이스 설정
```bash
# PostgreSQL 설치
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 생성
createdb swpp_ai_app

# .env 파일에 데이터베이스 자격 증명 편집
```

### 4. 데이터베이스 마이그레이션 실행
```bash
cd backend
alembic upgrade head
```

### 5. 백엔드 서버 시작
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 서버가 http://localhost:8000에서 실행됩니다
# API 문서는 http://localhost:8000/docs에서 확인 가능
```

## 📱 프론트엔드 설정

### 1. Android Studio 설정
```bash
# Android Studio 실행
# SDK Manager에서 다음 설치:
# - Android SDK Platform 34
# - Android SDK Build-Tools 34.0.0
# - Android Emulator
```

### 2. 환경 변수 설정
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# 변경사항 적용
source ~/.bashrc  # 또는 source ~/.zshrc
```

### 3. 프로젝트 빌드
```bash
cd frontend

# Gradle wrapper 권한 설정
chmod +x gradlew

# 프로젝트 빌드
./gradlew build

# 디버그 APK 생성
./gradlew assembleDebug
```

### 4. 에뮬레이터 또는 기기에서 실행
```bash
# 에뮬레이터 시작
emulator -avd <your_avd_name>

# 앱 설치 및 실행
./gradlew installDebug
```

## 🤖 AI 모델 설정

### 1. uv로 AI/ML 의존성 설치
```bash
# 가상환경 먼저 활성화
source venv/bin/activate

# uv를 사용한 AI 의존성 설치 (더 빠름)
uv pip install -e ".[ai]"

# GPU 지원용 (선택적, CUDA 필요)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 대안: uv로 AI 환경 관리
uv venv ai-env
source ai-env/bin/activate
uv pip install -r ai-model/requirements.txt
```

### 2. 사전 훈련된 모델 다운로드
```bash
cd ai-model

# 필요한 모델 다운로드 (시간이 걸릴 수 있음)
python scripts/download_models.py

# 모델 파일 확인
ls models/  # 모델 파일들이 있어야 함
```

### 3. Jupyter 환경 설정
```bash
# Jupyter 커널 설치
python -m ipykernel install --user --name swpp-ai-app --display-name "SWPP AI App"

# Jupyter Lab 시작
jupyter lab
```

## 🛠️ 개발 도구

### 1. 코드 포매터
```bash
# Pre-commit hooks 설치 (설정 스크립트에서 이미 완료)
pre-commit install

# 수동으로 포맷팅 실행
./scripts/formatters/format_python.py
./scripts/formatters/format_kotlin.sh
./scripts/formatters/format_all.sh
```

### 2. 코드 품질 도구
```bash
# Python 린팅
flake8 backend/ ai-model/
mypy backend/ ai-model/

# Kotlin 린팅
cd frontend
./gradlew ktlintCheck
./gradlew detekt
```

### 3. 테스팅 도구
```bash
# Python 테스트
pytest backend/tests/ ai-model/tests/

# Kotlin 테스트
cd frontend
./gradlew test

# 모든 테스트 실행
make test
```

## ✅ 검증

### 1. 환경 검증
```bash
# 모든 서비스 시작
make dev

# 또는 개별적으로:
# 백엔드: uvicorn src.main:app --reload
# 프론트엔드: ./gradlew installDebug
# AI 모델: python ai-model/src/serve.py
```

### 2. 헬스 체크
```bash
# 백엔드 API 확인
curl http://localhost:8000/health

# 데이터베이스 연결 확인
curl http://localhost:8000/db/health

# AI 모델 서비스 확인
curl http://localhost:8001/health
```

### 3. 테스트 실행
```bash
# 전체 테스트 스위트
make test

# 커버리지 포함
make test-coverage

# 특정 컴포넌트만
make test-python
make test-kotlin
```

## 🔧 문제 해결

### 일반적인 문제들

#### Python 의존성 문제
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
uv pip install -e ".[dev,ai]"
```

#### uv 설치 문제
```bash
# uv 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATH에 추가
export PATH="$HOME/.cargo/bin:$PATH"

# pip으로 대체 설치
pip install uv
```

#### 데이터베이스 연결 문제
```bash
# PostgreSQL 서비스 확인
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Ubuntu

# 연결 테스트
psql -h localhost -U postgres -d swpp_ai_app
```

#### Android 빌드 문제
```bash
# Gradle 캐시 정리
cd frontend
./gradlew clean

# SDK 경로 확인
echo $ANDROID_HOME

# 권한 문제 해결
chmod +x gradlew
```

#### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :8000  # 백엔드
lsof -i :8001  # AI 모델

# 프로세스 종료
kill -9 <PID>
```

### 로그 확인
```bash
# 백엔드 로그
tail -f backend/logs/app.log

# Docker 로그
docker-compose logs -f

# 시스템 로그
journalctl -f  # Linux
```

### 성능 최적화
```bash
# Python 패키지 캐시 정리
uv cache clean

# Docker 이미지 정리
docker system prune

# Gradle 캐시 정리
./gradlew clean
```

## 📚 추가 리소스

### 문서
- [개발 규칙](CONVENTIONS.md)
- [Git 워크플로우](GIT_WORKFLOW.md)
- [테스팅 가이드](TESTING.md)
- [API 문서](../api/backend-api.md)

### 도구 문서
- [uv 문서](https://github.com/astral-sh/uv)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Android 개발 가이드](https://developer.android.com/guide)
- [PyTorch 문서](https://pytorch.org/docs/)

### 커뮤니티
- [프로젝트 GitHub](https://github.com/snuhcs-course/swpp-2025-project-team-10)
- [이슈 트래커](https://github.com/snuhcs-course/swpp-2025-project-team-10/issues)
- [토론](https://github.com/snuhcs-course/swpp-2025-project-team-10/discussions)

---

**개발 환경 설정이 완료되었습니다! 이제 [개발 규칙](CONVENTIONS.md)을 읽고 코딩을 시작하세요!** 🚀
