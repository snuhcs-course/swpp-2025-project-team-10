# SWPP AI Application - English Documentation

Welcome to the English documentation for the SWPP AI Application project. This comprehensive guide will help you understand, develop, and contribute to our AI-powered mobile application.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Development Guidelines](#development-guidelines)
- [Version Control](#version-control)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Support](#support)

## 🚀 Quick Start

### For New Developers
1. **Environment Setup**: Start with [development/SETUP.md](development/SETUP.md)
2. **Coding Standards**: Review [development/CONVENTIONS.md](development/CONVENTIONS.md)
3. **Git Workflow**: Understand our workflow in [development/GIT_WORKFLOW.md](development/GIT_WORKFLOW.md)
4. **Testing**: Learn testing practices in [development/TESTING.md](development/TESTING.md)

### For Version Control
1. **Commit Rules**: Learn commit standards in [version-control/COMMIT_RULES.md](version-control/COMMIT_RULES.md)
2. **PR Guidelines**: Follow PR process in [version-control/PR_RULES.md](version-control/PR_RULES.md)
3. **Branch Strategy**: Understand branching in [version-control/BRANCH_STRATEGY.md](version-control/BRANCH_STRATEGY.md)

### Essential Commands
```bash
# Setup development environment
./scripts/setup/setup_dev_environment.sh

# Format code before committing
make format

# Run tests
make test

# Start development
make dev
```

## 📋 Project Overview

### 🏗️ Architecture

This is an AI-powered mobile application with three main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Model     │
│   (Kotlin)      │◄──►│   (FastAPI)     │◄──►│   (PyTorch)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🛠️ Technology Stack

#### Backend
- **Python 3.8+** with FastAPI framework
- **PostgreSQL** for data persistence
- **Redis** for caching and message queuing
- **Celery** for background task processing
- **SQLAlchemy** for ORM

#### Frontend
- **Kotlin** for Android development
- **Android SDK** (API level 21+)
- **Jetpack Compose** for modern UI
- **Retrofit** for API communication

#### AI/ML
- **PyTorch** for deep learning models
- **Transformers** for NLP capabilities
- **NumPy & Pandas** for data processing
- **Jupyter** for model development

#### DevOps
- **uv** for Python package management
- **Docker** for containerization
- **GitHub Actions** for CI/CD
- **Pre-commit hooks** for code quality

## 📚 Development Guidelines

### Core Documents
- **[CONVENTIONS.md](development/CONVENTIONS.md)** - Coding standards and best practices (**MUST READ**)
- **[GIT_WORKFLOW.md](development/GIT_WORKFLOW.md)** - Git workflow and branching strategy (**MUST READ**)
- **[SETUP.md](development/SETUP.md)** - Complete development environment setup
- **[TESTING.md](development/TESTING.md)** - Testing guidelines and practices

### Code Quality Standards
- **Python**: Black, isort, flake8, mypy, bandit
- **Kotlin**: ktlint, detekt
- **Pre-commit hooks**: Automatic code quality checks
- **Test Coverage**: Minimum 80% coverage required

## 🔄 Version Control

### Essential Documents
- **[COMMIT_RULES.md](version-control/COMMIT_RULES.md)** - Commit message standards and conventions
- **[PR_RULES.md](version-control/PR_RULES.md)** - Pull request guidelines and templates
- **[BRANCH_STRATEGY.md](version-control/BRANCH_STRATEGY.md)** - Detailed branching strategy

### Branch Strategy Overview
- **`main`**: Production-ready code (protected)
- **`dev`**: Integration branch for features (protected)
- **`feature/*`**: New features and enhancements
- **`bugfix/*`**: Bug fixes
- **`hotfix/*`**: Critical production fixes

### Workflow Summary
1. Create feature branch from `dev`
2. Follow commit message conventions
3. Run code formatters and tests
4. Create PR to `dev` branch
5. Get code review approval
6. Merge to `dev` for integration testing
7. Deploy to `main` for production

## 📖 API Documentation

### Backend API
- **[backend-api.md](api/backend-api.md)** - REST API endpoints and schemas
- **OpenAPI/Swagger**: Available at `/docs` when running backend
- **Authentication**: JWT-based authentication system

### AI Model API
- **[ai-model-api.md](api/ai-model-api.md)** - ML model inference endpoints
- **Model Serving**: FastAPI-based model serving
- **Batch Processing**: Celery-based background processing

## 🚀 Deployment

### Development
- **Local Development**: Virtual environments with uv
- **Docker Compose**: Multi-service local environment
- **Hot Reload**: Automatic code reloading

### Production
- **[DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - Production deployment procedures
- **[INFRASTRUCTURE.md](deployment/INFRASTRUCTURE.md)** - Infrastructure setup and requirements
- **Containerization**: Docker images for all services
- **Monitoring**: Prometheus and Grafana integration

## 🔧 Development Tools

### Code Formatters
```bash
# Format Python code
./scripts/formatters/format_python.py

# Format Kotlin code
./scripts/formatters/format_kotlin.sh

# Format all code
./scripts/formatters/format_all.sh
```

### Testing
```bash
# Run all tests
make test

# Run Python tests only
make test-python

# Run Kotlin tests only
make test-kotlin

# Run with coverage
make test-coverage
```

### Package Management
```bash
# Install dependencies with uv
uv pip install -r requirements.txt

# Add new dependency
uv add package-name

# Update dependencies
uv pip compile requirements.in
```

## 📊 Project Status

- ✅ Project structure and tooling setup
- ✅ Development environment configuration
- ✅ Code quality tools and pre-commit hooks
- ✅ Comprehensive documentation (EN/KR)
- ✅ Version control guidelines and templates
- 🚧 Backend API development
- 🚧 AI model implementation
- 🚧 Frontend mobile application
- ⏳ Integration testing
- ⏳ Production deployment

## 📞 Support

### Getting Help
1. **Documentation**: Check this documentation first
2. **Search Issues**: Look through existing GitHub issues
3. **Create Issue**: Use issue templates for bug reports or feature requests
4. **Team Discussion**: Use GitHub Discussions for questions
5. **Direct Contact**: Reach out to team members for urgent matters

### Issue Templates
- **Bug Report**: For reporting bugs and issues
- **Feature Request**: For suggesting new features
- **Documentation**: For documentation improvements
- **Question**: For general questions and discussions

## 🤝 Contributing

### Before You Start
1. Read [CONVENTIONS.md](development/CONVENTIONS.md) for coding standards
2. Understand [GIT_WORKFLOW.md](development/GIT_WORKFLOW.md) for our workflow
3. Review [COMMIT_RULES.md](version-control/COMMIT_RULES.md) for commit standards
4. Check [PR_RULES.md](version-control/PR_RULES.md) for pull request guidelines

### Contribution Process
1. Fork the repository (if external contributor)
2. Create feature branch: `git checkout -b feature/your-feature-name`
3. Follow coding conventions and write tests
4. Commit with conventional commit messages
5. Push branch and create pull request
6. Address code review feedback
7. Merge after approval

### Code Review Checklist
- [ ] Code follows project conventions
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Commit messages follow conventions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**Ready to contribute? Start with the [development setup guide](development/SETUP.md)!** 🚀
