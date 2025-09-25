# Git Workflow and Branching Strategy

This document outlines the Git workflow, branching strategy, and version control practices for the SWPP AI Application project.

## 📋 Table of Contents

- [Branching Strategy](#branching-strategy)
- [Workflow Overview](#workflow-overview)
- [Branch Types](#branch-types)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Git Hooks](#git-hooks)

## 🌳 Branching Strategy

We use a **Git Flow** inspired branching strategy with two main branches:

```
main (production-ready code)
├── dev (integration branch)
    ├── feature/user-authentication
    ├── feature/ai-model-training
    ├── bugfix/login-validation
    └── hotfix/security-patch
```

### Main Branches

#### `main` Branch
- **Purpose**: Production-ready code only
- **Protection**: Protected branch with required reviews
- **Deployment**: Automatically deployed to production
- **Direct commits**: ❌ **NEVER** commit directly to main
- **Merges from**: `dev` branch only (via PR)

#### `dev` Branch  
- **Purpose**: Integration branch for feature development
- **Protection**: Protected branch with required reviews
- **Testing**: All features tested together before main merge
- **Direct commits**: ❌ **NEVER** commit directly to dev
- **Merges from**: Feature, bugfix, and hotfix branches

## 🔄 Workflow Overview

### 1. Feature Development
```bash
# Start from latest dev
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/your-feature-name

# Work on feature
git add .
git commit -m "feat: implement user authentication"

# Push and create PR to dev
git push origin feature/your-feature-name
```

### 2. Integration Testing
```bash
# After PR approval, feature is merged to dev
# Dev branch is tested with all integrated features
# If tests pass, create PR from dev to main
```

### 3. Production Release
```bash
# After dev testing, merge to main
# Main branch automatically deploys to production
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 🏷️ Branch Types

### Feature Branches
- **Naming**: `feature/description-of-feature`
- **Purpose**: New features or enhancements
- **Base**: `dev` branch
- **Merge to**: `dev` branch
- **Lifetime**: Until feature is complete and merged

```bash
# Examples
feature/user-authentication
feature/ai-model-integration
feature/mobile-ui-redesign
```

### Bugfix Branches
- **Naming**: `bugfix/description-of-bug`
- **Purpose**: Bug fixes for existing features
- **Base**: `dev` branch
- **Merge to**: `dev` branch
- **Lifetime**: Until bug is fixed and merged

```bash
# Examples
bugfix/login-validation-error
bugfix/model-prediction-accuracy
bugfix/mobile-crash-on-startup
```

### Hotfix Branches
- **Naming**: `hotfix/description-of-fix`
- **Purpose**: Critical fixes that need immediate production deployment
- **Base**: `main` branch
- **Merge to**: Both `main` and `dev` branches
- **Lifetime**: Until hotfix is deployed

```bash
# Examples
hotfix/security-vulnerability
hotfix/critical-data-loss
hotfix/production-server-crash
```

### Release Branches (Optional)
- **Naming**: `release/version-number`
- **Purpose**: Prepare releases, final testing, version bumps
- **Base**: `dev` branch
- **Merge to**: `main` and `dev` branches
- **Lifetime**: Until release is complete

## 📝 Commit Guidelines

### Commit Message Format
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples
```bash
# Good commit messages
git commit -m "feat(auth): add JWT token validation"
git commit -m "fix(ai-model): resolve memory leak in training loop"
git commit -m "docs(api): update authentication endpoint documentation"
git commit -m "test(backend): add unit tests for user service"
git commit -m "chore(deps): update FastAPI to version 0.104.0"

# Bad commit messages (avoid these)
git commit -m "fix stuff"
git commit -m "update"
git commit -m "changes"
git commit -m "wip"
```

### Commit Best Practices
- **Atomic commits**: One logical change per commit
- **Descriptive messages**: Explain what and why, not how
- **Present tense**: Use imperative mood ("add" not "added")
- **Line length**: Keep first line under 50 characters
- **Body**: Add body for complex changes (wrap at 72 characters)

## 🔍 Pull Request Process

### Creating Pull Requests

1. **Pre-PR Checklist**
   - [ ] Code follows project conventions
   - [ ] All tests pass locally
   - [ ] Code formatters have been run
   - [ ] Documentation is updated
   - [ ] No merge conflicts with target branch

2. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

### Review Process

1. **Automatic Checks**
   - Code formatting validation
   - Unit test execution
   - Security scanning
   - Build verification

2. **Manual Review**
   - At least 2 reviewers required for `main`
   - At least 1 reviewer required for `dev`
   - Focus on code quality, logic, and maintainability
   - Check for security vulnerabilities

3. **Approval and Merge**
   - All checks must pass
   - All requested changes addressed
   - Use "Squash and merge" for feature branches
   - Use "Merge commit" for release branches

## 🚀 Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Prepare Release**
   ```bash
   # Create release branch from dev
   git checkout dev
   git pull origin dev
   git checkout -b release/v1.2.0
   
   # Update version numbers
   # Update CHANGELOG.md
   # Final testing
   ```

2. **Create Release PR**
   ```bash
   # Create PR from release branch to main
   # Include release notes and changelog
   # Get required approvals
   ```

3. **Deploy and Tag**
   ```bash
   # After merge to main
   git checkout main
   git pull origin main
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   
   # Merge back to dev
   git checkout dev
   git merge main
   git push origin dev
   ```

### Hotfix Process

1. **Create Hotfix**
   ```bash
   # Create hotfix branch from main
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-security-fix
   
   # Make minimal changes
   # Test thoroughly
   ```

2. **Deploy Hotfix**
   ```bash
   # Create PR to main (expedited review)
   # After merge, tag immediately
   git tag -a v1.2.1 -m "Hotfix version 1.2.1"
   git push origin v1.2.1
   
   # Merge to dev as well
   git checkout dev
   git merge main
   git push origin dev
   ```

## 🪝 Git Hooks

### Pre-commit Hooks
Automatically installed and run before each commit:

```bash
# Install hooks (done during setup)
pre-commit install

# What runs on each commit:
# 1. Code formatters (Python, Kotlin)
# 2. Linting checks
# 3. Security scans
# 4. Test execution (fast tests only)
```

### Pre-push Hooks
Run before pushing to remote:

```bash
# What runs on each push:
# 1. Full test suite
# 2. Build verification
# 3. Documentation checks
```

### Bypassing Hooks (Emergency Only)
```bash
# Only in emergencies - requires justification
git commit --no-verify -m "emergency: critical production fix"
git push --no-verify
```

## 🛡️ Branch Protection Rules

### `main` Branch
- Require pull request reviews (2 reviewers)
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to administrators only
- Require signed commits

### `dev` Branch  
- Require pull request reviews (1 reviewer)
- Require status checks to pass
- Require branches to be up to date
- Allow force pushes by administrators

## 📊 Git Best Practices

### Daily Workflow
```bash
# Start of day - sync with remote
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/my-new-feature

# Regular commits during development
git add .
git commit -m "feat: implement basic functionality"

# End of day - push work
git push origin feature/my-new-feature
```

### Keeping Branches Updated
```bash
# Regularly sync feature branch with dev
git checkout dev
git pull origin dev
git checkout feature/my-feature
git rebase dev  # or git merge dev

# Resolve conflicts if any
git push origin feature/my-feature --force-with-lease
```

### Cleaning Up
```bash
# After feature is merged, clean up
git checkout dev
git pull origin dev
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

## 🚨 Emergency Procedures

### Reverting Bad Commits
```bash
# Revert specific commit
git revert <commit-hash>

# Revert merge commit
git revert -m 1 <merge-commit-hash>
```

### Rolling Back Release
```bash
# Create hotfix to revert changes
git checkout main
git checkout -b hotfix/rollback-v1.2.0
git revert <problematic-commit>
# Follow hotfix process
```

## 🔗 Quick Reference

### Common Commands
```bash
# Setup new feature
git checkout dev && git pull origin dev
git checkout -b feature/my-feature

# Daily sync
git checkout dev && git pull origin dev
git checkout feature/my-feature && git rebase dev

# Finish feature
git push origin feature/my-feature
# Create PR via GitHub UI

# Cleanup after merge
git checkout dev && git pull origin dev
git branch -d feature/my-feature
```

### Branch Naming Examples
```bash
# Features
feature/user-authentication
feature/ai-model-training
feature/mobile-push-notifications

# Bug fixes
bugfix/login-validation
bugfix/memory-leak-training
bugfix/ui-crash-android

# Hotfixes
hotfix/security-vulnerability
hotfix/data-corruption-fix
```

---

**Remember**: This workflow ensures code quality, enables collaboration, and maintains a stable production environment. When in doubt, ask the team lead or create an issue for discussion.
