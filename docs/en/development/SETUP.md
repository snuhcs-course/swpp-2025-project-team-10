# Development Environment Setup

This guide will help you set up your development environment for the SWPP AI Application project.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [AI Model Setup](#ai-model-setup)
- [Development Tools](#development-tools)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **OS**: macOS 10.15+, Ubuntu 20.04+, or Windows 10+ with WSL2
- **RAM**: Minimum 8GB, recommended 16GB+ (for AI model training)
- **Storage**: At least 10GB free space
- **Internet**: Stable connection for downloading dependencies

### Required Software

#### Git
```bash
# macOS
brew install git

# Ubuntu
sudo apt update && sudo apt install git

# Windows (use Git for Windows or WSL2)
```

#### Python 3.8+ and uv
```bash
# macOS
brew install python@3.11

# Ubuntu
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install uv (fast Python package manager)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Verify installation
python3 --version  # Should be 3.8 or higher
uv --version       # Should show uv version
```

#### Node.js 18+ (for frontend tooling)
```bash
# macOS
brew install node

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be 18.0 or higher
npm --version
```

#### Java 11+ (for Android development)
```bash
# macOS
brew install openjdk@11

# Ubuntu
sudo apt install openjdk-11-jdk

# Verify installation
java -version
```

#### Android Studio
1. Download from [developer.android.com](https://developer.android.com/studio)
2. Install Android SDK (API level 21+)
3. Set up Android Virtual Device (AVD)

## 🚀 Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/snuhcs-course/swpp-2025-project-team-10.git
cd swpp-2025-project-team-10
```

### 2. Run Setup Script
```bash
# Make setup script executable
chmod +x scripts/setup/setup_dev_environment.sh

# Run setup (this will install all dependencies)
./scripts/setup/setup_dev_environment.sh
```

### 3. Configure Git
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Set up Git hooks
pre-commit install
```

## 🐍 Backend Setup

### 1. Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux
source venv/bin/activate

# Windows (if not using WSL2)
venv\Scripts\activate

# Verify activation (should show venv in prompt)
which python  # Should point to venv/bin/python
```

### 2. Install Dependencies with uv
```bash
# Install development dependencies using uv (faster)
uv pip install -e ".[dev]"

# Or install from requirements file
uv pip install -r backend/requirements.txt
uv pip install -r backend/requirements-dev.txt

# Alternative: Create and sync with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip sync requirements.txt
```

### 3. Database Setup
```bash
# Install PostgreSQL
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb swpp_ai_app_dev
createdb swpp_ai_app_test

# Set environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials
```

### 4. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 5. Start Backend Server
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📱 Frontend Setup

### 1. Android SDK Configuration
```bash
# Set environment variables (add to ~/.bashrc or ~/.zshrc)
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc
```

### 2. Install Android Dependencies
```bash
# Install required SDK packages
sdkmanager "platform-tools" "platforms;android-30" "build-tools;30.0.3"

# Create AVD (Android Virtual Device)
avdmanager create avd -n "Pixel_4_API_30" -k "system-images;android-30;google_apis;x86_64"
```

### 3. Build Frontend
```bash
cd frontend

# Build debug version
./gradlew assembleDebug

# Install on connected device/emulator
./gradlew installDebug
```

## 🤖 AI Model Setup

### 1. Install AI/ML Dependencies with uv
```bash
# Activate virtual environment first
source venv/bin/activate

# Install AI dependencies using uv (faster)
uv pip install -e ".[ai]"

# For GPU support (optional, requires CUDA)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Alternative: Use uv to manage AI environment
uv venv ai-env
source ai-env/bin/activate
uv pip install -r ai-model/requirements.txt
```

### 2. Download Pre-trained Models
```bash
cd ai-model

# Download required models (this may take a while)
python scripts/download_models.py

# Verify models are downloaded
ls models/  # Should contain model files
```

### 3. Set up Jupyter Environment
```bash
# Install Jupyter kernel
python -m ipykernel install --user --name swpp-ai-app --display-name "SWPP AI App"

# Start Jupyter Lab
jupyter lab
```

## 🛠️ Development Tools

### 1. Code Formatters
```bash
# Install pre-commit hooks (already done in setup script)
pre-commit install

# Test formatters
./scripts/formatters/format_all.sh --check

# Format code manually
./scripts/formatters/format_python.py
./scripts/formatters/format_kotlin.sh
```

### 2. IDE Configuration

#### VS Code (Recommended)
Install recommended extensions:
- Python
- Pylance
- Black Formatter
- isort
- Kotlin
- Android iOS Emulator

#### PyCharm/IntelliJ IDEA
1. Open project root directory
2. Configure Python interpreter to use virtual environment
3. Install Kotlin plugin
4. Configure code style settings

### 3. Testing Tools
```bash
# Run Python tests
pytest backend/tests/
pytest ai-model/tests/

# Run with coverage
pytest --cov=backend/src --cov=ai-model/src

# Run Kotlin tests
cd frontend
./gradlew test
```

## ✅ Verification

### 1. Backend Verification
```bash
# Check if backend is running
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

### 2. Frontend Verification
```bash
# Check if Android emulator is working
emulator -list-avds  # Should show your AVD

# Start emulator
emulator -avd Pixel_4_API_30

# Install and run app
cd frontend
./gradlew installDebug
```

### 3. AI Model Verification
```bash
# Test model loading
cd ai-model
python -c "
import torch
from src.models.base_model import BaseModel
print('AI model setup successful!')
"
```

### 4. Code Quality Verification
```bash
# Run all formatters and checks
./scripts/formatters/format_all.sh --check

# Run tests
pytest
cd frontend && ./gradlew test
```

## 🔧 Troubleshooting

### Common Issues

#### Python Virtual Environment Issues
```bash
# If venv activation fails
python3 -m venv --clear venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
# macOS
brew services list | grep postgresql

# Ubuntu
sudo systemctl status postgresql

# Reset database
dropdb swpp_ai_app_dev
createdb swpp_ai_app_dev
cd backend && alembic upgrade head
```

#### Android SDK Issues
```bash
# Update SDK
sdkmanager --update

# List installed packages
sdkmanager --list

# Accept licenses
sdkmanager --licenses
```

#### Memory Issues (AI Model Training)
```bash
# Monitor memory usage
htop  # or top

# Reduce batch size in training configs
# Edit ai-model/config/training.yaml
```

### Getting Help

1. **Check logs**: Look in `logs/` directory for error details
2. **Search issues**: Check GitHub issues for similar problems
3. **Ask team**: Create issue or ask in team chat
4. **Documentation**: Review relevant docs in `docs/` directory

### Environment Variables

Create these files with appropriate values:

#### `backend/.env`
```bash
DATABASE_URL=postgresql://username:password@localhost/swpp_ai_app_dev
SECRET_KEY=your-secret-key-here
DEBUG=true
LOG_LEVEL=debug
```

#### `ai-model/.env`
```bash
MODEL_PATH=./models
DATA_PATH=./data
CUDA_VISIBLE_DEVICES=0  # If using GPU
WANDB_API_KEY=your-wandb-key  # If using Weights & Biases
```

---

**Next Steps**: After completing setup, read the [development conventions](CONVENTIONS.md) and [git workflow](GIT_WORKFLOW.md) documentation.
