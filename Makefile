.PHONY: help install setup test lint format clean dev build deploy

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project variables
PROJECT_NAME := swpp-ai-app
PYTHON := python3
PIP := pip3
BACKEND_DIR := backend
FRONTEND_DIR := frontend
AI_MODEL_DIR := ai-model

##@ General

help: ## Display this help message
	@echo "$(BLUE)$(PROJECT_NAME) - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(MAKE) install-backend
	@$(MAKE) install-frontend
	@$(MAKE) install-ai
	@$(MAKE) install-tools
	@echo "$(GREEN)✅ All dependencies installed$(NC)"

install-backend: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	@cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt
	@cd $(BACKEND_DIR) && $(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✅ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@echo "$(YELLOW)Frontend dependencies will be managed by Gradle$(NC)"
	@echo "$(GREEN)✅ Frontend setup complete$(NC)"

install-ai: ## Install AI model dependencies
	@echo "$(BLUE)Installing AI model dependencies...$(NC)"
	@if [ -f $(AI_MODEL_DIR)/requirements.txt ]; then \
		cd $(AI_MODEL_DIR) && $(PIP) install -r requirements.txt; \
	fi
	@echo "$(GREEN)✅ AI model dependencies installed$(NC)"

install-tools: ## Install development tools
	@echo "$(BLUE)Installing development tools...$(NC)"
	@$(PIP) install pre-commit ruff black isort flake8 bandit pytest pytest-cov
	@pre-commit install
	@echo "$(GREEN)✅ Development tools installed$(NC)"

setup: install ## Complete development environment setup
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@$(MAKE) setup-backend
	@$(MAKE) setup-git-hooks
	@echo "$(GREEN)✅ Development environment ready$(NC)"

setup-backend: ## Setup backend (database, migrations)
	@echo "$(BLUE)Setting up backend...$(NC)"
	@cd $(BACKEND_DIR) && $(PYTHON) manage.py migrate
	@echo "$(GREEN)✅ Backend setup complete$(NC)"

setup-git-hooks: ## Setup git hooks
	@echo "$(BLUE)Setting up git hooks...$(NC)"
	@pre-commit install
	@echo "$(GREEN)✅ Git hooks installed$(NC)"

##@ Development

dev: ## Start development servers
	@echo "$(BLUE)Starting development servers...$(NC)"
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Start backend development server
	@echo "$(BLUE)Starting backend server...$(NC)"
	@cd $(BACKEND_DIR) && $(PYTHON) manage.py runserver

dev-frontend: ## Start frontend development
	@echo "$(BLUE)Frontend development...$(NC)"
	@echo "$(YELLOW)Open Android Studio and run the app$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@$(MAKE) test-ai
	@echo "$(GREEN)✅ All tests completed$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd $(BACKEND_DIR) && pytest -v

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@echo "$(YELLOW)Frontend tests will be added when build.gradle is configured$(NC)"

test-ai: ## Run AI model tests
	@echo "$(BLUE)Running AI model tests...$(NC)"
	@if [ -d $(AI_MODEL_DIR)/tests ]; then \
		cd $(AI_MODEL_DIR) && pytest -v; \
	else \
		echo "$(YELLOW)No AI model tests found$(NC)"; \
	fi

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@cd $(BACKEND_DIR) && pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Coverage report generated in $(BACKEND_DIR)/htmlcov/$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@cd $(BACKEND_DIR) && pytest tests/test_api_integration.py -v

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	@cd $(BACKEND_DIR) && pytest-watch

##@ Code Quality

lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	@$(MAKE) lint-python
	@$(MAKE) lint-kotlin
	@echo "$(GREEN)✅ Linting complete$(NC)"

lint-python: ## Run Python linters
	@echo "$(BLUE)Running Python linters...$(NC)"
	@python tools/formatters/format_python.py --use-ruff --check
	@echo "$(GREEN)✅ Python linting complete$(NC)"

lint-kotlin: ## Run Kotlin linters
	@echo "$(BLUE)Running Kotlin linters...$(NC)"
	@if [ -f tools/linting/ktlint ]; then \
		./tools/linting/ktlint "$(FRONTEND_DIR)/**/*.kt" || true; \
	fi
	@echo "$(GREEN)✅ Kotlin linting complete$(NC)"

format: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(MAKE) format-python
	@$(MAKE) format-kotlin
	@echo "$(GREEN)✅ Code formatting complete$(NC)"

format-python: ## Format Python code
	@echo "$(BLUE)Formatting Python code...$(NC)"
	@python tools/formatters/format_python.py --use-ruff
	@echo "$(GREEN)✅ Python code formatted$(NC)"

format-kotlin: ## Format Kotlin code
	@echo "$(BLUE)Formatting Kotlin code...$(NC)"
	@if [ -f scripts/formatters/format_kotlin.sh ]; then \
		./scripts/formatters/format_kotlin.sh; \
	fi
	@echo "$(GREEN)✅ Kotlin code formatted$(NC)"

format-check: ## Check code formatting without changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	@python tools/formatters/format_python.py --use-ruff --check
	@echo "$(GREEN)✅ Code formatting check complete$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@bandit -r $(BACKEND_DIR)/ -ll -f json -o security-report.json
	@echo "$(GREEN)✅ Security check complete$(NC)"

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@cd $(BACKEND_DIR) && $(PYTHON) manage.py migrate
	@echo "$(GREEN)✅ Migrations complete$(NC)"

db-makemigrations: ## Create new migrations
	@echo "$(BLUE)Creating migrations...$(NC)"
	@cd $(BACKEND_DIR) && $(PYTHON) manage.py makemigrations
	@echo "$(GREEN)✅ Migrations created$(NC)"

db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(RED)⚠️  WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(BACKEND_DIR) && rm -f db.sqlite3; \
		$(MAKE) db-migrate; \
		echo "$(GREEN)✅ Database reset complete$(NC)"; \
	fi

db-shell: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	@cd $(BACKEND_DIR) && $(PYTHON) manage.py dbshell

##@ Build

build: ## Build all components
	@echo "$(BLUE)Building all components...$(NC)"
	@$(MAKE) build-backend
	@$(MAKE) build-frontend
	@echo "$(GREEN)✅ Build complete$(NC)"

build-backend: ## Build backend Docker image
	@echo "$(BLUE)Building backend Docker image...$(NC)"
	@if [ -f $(BACKEND_DIR)/Dockerfile ]; then \
		docker build -t $(PROJECT_NAME)-backend:latest $(BACKEND_DIR)/; \
	else \
		echo "$(YELLOW)Dockerfile not found$(NC)"; \
	fi
	@echo "$(GREEN)✅ Backend build complete$(NC)"

build-frontend: ## Build frontend APK
	@echo "$(BLUE)Building frontend APK...$(NC)"
	@echo "$(YELLOW)Frontend build will be added when build.gradle is configured$(NC)"

##@ Docker

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Containers started$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Containers stopped$(NC)"

docker-logs: ## View Docker logs
	@docker-compose logs -f

docker-clean: ## Clean Docker resources
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	@docker-compose down -v
	@docker system prune -f
	@echo "$(GREEN)✅ Docker cleanup complete$(NC)"

##@ Git

git-status: ## Show git status
	@git status

git-branches: ## Show all branches
	@git branch -a

git-clean-branches: ## Clean merged branches
	@echo "$(BLUE)Cleaning merged branches...$(NC)"
	@git branch --merged | grep -v "\*\|main\|dev" | xargs -n 1 git branch -d || true
	@echo "$(GREEN)✅ Merged branches cleaned$(NC)"

##@ Documentation

docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	@if [ -d docs ]; then \
		echo "Documentation is in Markdown format"; \
	fi
	@echo "$(GREEN)✅ Documentation ready$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Open docs/README.md in your browser$(NC)"

##@ Cleanup

clean: ## Clean all generated files
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	@$(MAKE) clean-python
	@$(MAKE) clean-build
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-python: ## Clean Python cache files
	@echo "$(BLUE)Cleaning Python cache...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Python cache cleaned$(NC)"

clean-build: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf build/ dist/ *.egg-info
	@rm -rf $(BACKEND_DIR)/htmlcov/
	@rm -f $(BACKEND_DIR)/.coverage
	@echo "$(GREEN)✅ Build artifacts cleaned$(NC)"

##@ CI/CD

ci-local: ## Run CI checks locally
	@echo "$(BLUE)Running CI checks locally...$(NC)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) test
	@echo "$(GREEN)✅ CI checks passed$(NC)"

pre-commit: ## Run pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	@pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit checks passed$(NC)"

##@ Information

info: ## Display project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "===================="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Git: $(shell git --version)"
	@echo "Current branch: $(shell git branch --show-current)"
	@echo ""
	@echo "$(BLUE)Directory Structure$(NC)"
	@echo "===================="
	@echo "Backend: $(BACKEND_DIR)/"
	@echo "Frontend: $(FRONTEND_DIR)/"
	@echo "AI Model: $(AI_MODEL_DIR)/"
	@echo ""
	@echo "$(BLUE)Quick Commands$(NC)"
	@echo "===================="
	@echo "make dev          - Start development servers"
	@echo "make test         - Run all tests"
	@echo "make format       - Format all code"
	@echo "make lint         - Run all linters"
	@echo "make ci-local     - Run CI checks locally"

