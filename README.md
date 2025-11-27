# 서로서로도서관 (Library Together)

A book bartering social network mobile application built for the SNU Software Practice (SWPP) course.

![Build Status](https://github.com/snuhcs-course/swpp-2025-project-team-10/workflows/CI/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![Kotlin](https://img.shields.io/badge/kotlin-2.0-orange)
![Django](https://img.shields.io/badge/django-5.2.7-green)

## 📖 About

**서로서로도서관 (Library Together)** is a social networking platform that enables users to:
- Exchange books with other users through a bartering system
- Build a community around book sharing and reading
- Discover new books and connect with fellow readers
- Manage personal book collections
- Track reading history and preferences

## 🚀 Quick Start

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/snuhcs-course/swpp-2025-project-team-10.git
cd swpp-2025-project-team-10

# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from pyproject (includes dev/test extras)
pip install -e ".[dev]"  # or: uv sync --extra dev, uv sync --all-extras

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### Frontend Setup

```bash
# Open Android Studio
# File -> Open -> Select the 'frontend' directory

# Or build from command line
cd frontend
./gradlew assembleDebug

# Install on connected device
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 📱 Features

- **User Authentication**: Email/password Sign up / Sign in

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (Kotlin)      │◄──►│   (Django)      │
│   Android App   │    │   REST API      │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Jetpack       │    │    SQLite       │
│   Compose UI    │    │    Database     │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11** with Django 5.2.7
- **Django REST Framework** for API
- **SQLite** for development database (PostgreSQL for production)
- **djangorestframework-simplejwt** for JWT authentication
- **django-cors-headers** for CORS support
- **drf-spectacular** for API documentation

### Frontend
- **Kotlin 2.0** for Android development
- **Android SDK** (API level 34, min 26)
- **Jetpack Compose** for modern UI
- **Retrofit** for API communication
- **OkHttp** for HTTP client
- **Credential Manager** for Google Sign-In
- **Kakao SDK** for Kakao login

### DevOps
- **GitHub Actions** for CI/CD
- **Android Emulator** for testing
- **ADB** for device management

### Code Quality
- **Pre-commit hooks** for automated code quality checks
- **Ruff** for Python linting and formatting (fast, modern)
- **ktlint** for Kotlin code formatting
- **detekt** for Kotlin static analysis

## 📋 Prerequisites

- **Python 3.11+**
- **Java 17+** (for Android development)
- **Android Studio** Hedgehog or later
- **Android SDK** (API 34)
- **Git**

## 🚀 Getting Started

### 1. Backend Setup (Django)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from pyproject (includes dev/test extras)
pip install -e ".[dev]"  # or: uv sync --extra dev / uv sync --all-extras

# Run database migrations
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

**Note:** The project currently uses SQLite for development. PostgreSQL configuration is available but commented out in `settings.py`.

### 2. Frontend Setup (Android)

#### Option A: Using Android Studio (Recommended)

1. Open Android Studio
2. Select **File → Open**
3. Navigate to and select the `frontend` directory
4. Wait for Gradle sync to complete
5. Connect an Android device or start an emulator
6. Click **Run** (▶️) button

#### Option B: Command Line

```bash
# Navigate to frontend directory
cd frontend

# Build debug APK
./gradlew assembleDebug

# Install on connected device
adb install app/build/outputs/apk/debug/app-debug.apk

# Or install and launch
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.example.librarytogether/.feature.auth.LoginActivity
```

### 3. Testing on Physical Device

For best results, test on a physical Android device:

```bash
# Enable USB debugging on your device
# Connect device via USB

# Verify device is connected
adb devices

# Update backend URL in RetrofitClient.kt
# Change BASE_URL to your computer's IP address
# Example: "http://192.168.1.100:8000/"

# Make sure your device and computer are on the same network
# Allow Python through firewall if needed
```

### 4. Configuration

The project uses default configurations for development. No `.env` file is required for basic setup.

**Backend Configuration** (`backend/core/settings.py`):
- Database: SQLite (default) - `db.sqlite3`
- Debug mode: Enabled
- CORS: Allowed for all origins in development
- Allowed hosts: Configured for localhost and local network IPs

**Frontend Configuration** (`frontend/app/src/main/java/com/example/librarytogether/network/RetrofitClient.kt`):
- Base URL: `http://10.0.2.2:8000/` (for emulator)
- For physical device: Change to your computer's IP (e.g., `http://192.168.1.100:8000/`)
- Timeout: 15s connect, 20s read/write

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Backend API Documentation](backend/docs/API_DOCUMENTATION.md)** - REST API endpoints and usage
- **[Backend Architecture](backend/docs/ARCHITECTURE.md)** - Backend design and structure
- **[Design Documentation Guide](docs/DESIGN_DOCUMENTATION_GUIDE.md)** - Project design guidelines
- **[Workflow Guide](docs/WORKFLOW_IMPLEMENTATION_GUIDE.md)** - Development workflow

## 🧪 Testing

### Backend Tests

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source .venv/bin/activate

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test books
python manage.py test barter

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report in htmlcov/
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Run instrumented tests (requires emulator or device)
./gradlew clean connectedDebugAndroidTest

# Run unit tests
./gradlew testDebugUnitTest       

# Jacoco Report (Generate HTML report)
./gradlew jacocoTestReport

# HTML report path:
# frontend/app/build/reports/jacoco/jacocoTestReport/html/index.html
```

## 🎯 API Endpoints

### Authentication
- `POST /auth/login/` - User login
- `POST /auth/signup/` - User registration
- `POST /auth/token/refresh/` - Refresh JWT token
- `POST /auth/login/google/` - Google Sign-In
- `POST /auth/signup/google/` - Google Sign-Up
- `POST /auth/login/kakao/` - Kakao login
- `POST /auth/signup/kakao/` - Kakao signup

### Password Reset
- `POST /auth/forgot/start/` - Request password reset
- `POST /auth/forgot/verify/` - Verify reset code
- `POST /auth/forgot/reset/` - Reset password

### User Profile
- `GET /auth/profile/` - Get user profile
- `PUT /auth/profile/update/` - Update user profile

See [API Documentation](backend/docs/API_DOCUMENTATION.md) for complete API reference.

## 🔧 Troubleshooting

### Backend Issues

**Database migrations fail:**
```bash
# Delete database and start fresh
rm backend/db.sqlite3
python manage.py migrate
```

**Port 8000 already in use:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python manage.py runserver 8080
```

**Module not found errors:**
```bash
# Ensure virtual environment is activated
source backend/.venv/bin/activate

# Reinstall dependencies
cd backend && uv sync --extra dev  # or: pip install -e ".[dev]"
```

### Frontend Issues

**Gradle sync fails:**
- Ensure Java 17+ is installed
- Check internet connection for dependency downloads
- Try: File → Invalidate Caches → Invalidate and Restart

**App cannot connect to backend:**
- Check backend is running: `curl http://localhost:8000/`
- For emulator: Use `http://10.0.2.2:8000/`
- For physical device: Use your computer's IP address
- Ensure firewall allows Python connections
- Verify device and computer are on same network

**Build errors:**
```bash
# Clean and rebuild
cd frontend
./gradlew clean
./gradlew assembleDebug
```

## 🤝 Contributing

We follow a structured development workflow:

1. **Create feature branch**: `git checkout -b feature/your-feature-name`
2. **Follow coding standards**:
   - Python: 79 characters line length
   - Kotlin: Follow Kotlin recommended standards
3. **Write tests**: Maintain test coverage
4. **Create pull request**: Target the `dev` branch
5. **Code review**: Get approval from team members
6. **Merge to dev**: Integration testing in dev branch
7. **Deploy to main**: Production deployment from main branch

### Branch Strategy

- `main`: Production-ready code
- `dev`: Integration branch for features
- `feature/*`: New features and enhancements
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

### Coding Standards

- **Python**: 79 characters line length (PEP 8)
- **Kotlin**: Follow Kotlin recommended line length
- **Frontend**: Follow respective language standards

### Code Formatting & Linting

This project uses automated code formatting and linting tools to maintain code quality and consistency.

#### Setup Pre-commit Hooks (One-time setup)

```bash
# Install pre-commit hooks that run automatically before each commit
bash tools/git-hooks/setup_pre_commit.sh
```

#### Manual Code Formatting

```bash
# Format Python code (recommended: uses ruff for speed)
python tools/formatters/format_python.py --use-ruff

# Format Kotlin code
bash tools/formatters/format_kotlin.sh

# Format all code (Python + Kotlin)
bash tools/formatters/format_all.sh
```

#### What Gets Checked

Pre-commit hooks automatically check and fix:
- **Python**: Linting and formatting with ruff, import sorting
- **Kotlin**: Code formatting with ktlint
- **General**: Trailing whitespace, end-of-file newlines, YAML/JSON validation
- **Safety**: Large file detection, merge conflict detection

For detailed information about formatting tools and workflows, see **[tools/README.md](tools/README.md)**.

## 📊 Project Status

- ✅ Project structure and setup
- ✅ Backend API (Django REST Framework)
- ✅ User authentication (Email, Google, Kakao)
- ✅ Frontend mobile application (Android/Kotlin)
- ✅ Book management system
- ✅ User profiles
- 🚧 Bartering system
- 🚧 Social features (follow, messaging)
- 🚧 Notifications
- ⏳ Production deployment

## 🎓 SWPP Course Requirements

This project fulfills the requirements for the SNU Software Practice (SWPP) course:

- **Design Documentation**: Available on GitHub Wiki
  - Document revision history
  - System architecture diagrams
  - Class diagrams (frontend/backend)
  - ER diagrams for database
  - Testing plan with coverage goals
  - 5 user acceptance test stories

- **Testing Requirements** (Starting Iteration 3):
  - Coverage goals reported by architectural component
  - Example: M/V/VM separately for MVVM architecture

## 📞 Support

- **Documentation**: Check the `docs/` directory and GitHub Wiki
- **Issues**: Create a GitHub issue with detailed information
- **Team**: Contact the development team for urgent matters

## 📄 License

This project is developed for educational purposes as part of the SNU SWPP course.

## 🙏 Acknowledgments

- **SNU SWPP Course** for the project framework and guidance
- **Django & Django REST Framework** for the robust backend framework
- **Android & Jetpack Compose** for modern mobile development
- **Open Source Libraries** used throughout the project
- **Team 10 Members** for their contributions and collaboration

---

**서로서로도서관 - 책으로 연결되는 우리들의 이야기** 📚

*Built with ❤️ for SWPP 2025*
