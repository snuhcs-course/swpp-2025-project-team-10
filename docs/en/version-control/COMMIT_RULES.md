# Commit Message Rules and Standards

This document defines the commit message standards for the SWPP AI Application project. Following these rules ensures consistent, readable, and trackable project history.

## 📋 Table of Contents

- [Commit Message Format](#commit-message-format)
- [Commit Types](#commit-types)
- [Scope Guidelines](#scope-guidelines)
- [Writing Guidelines](#writing-guidelines)
- [Examples](#examples)
- [Tools and Automation](#tools-and-automation)
- [Common Mistakes](#common-mistakes)

## 📝 Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Structure Rules
- **Header**: `<type>[optional scope]: <description>`
  - Maximum 50 characters
  - Lowercase type and scope
  - Imperative mood for description
  - No period at the end

- **Body** (optional):
  - Wrap at 72 characters
  - Explain what and why, not how
  - Separate from header with blank line

- **Footer** (optional):
  - Reference issues, breaking changes
  - Separate from body with blank line

## 🏷️ Commit Types

### Primary Types (Required)

#### `feat` - New Features
- New functionality for users
- New API endpoints
- New UI components
- New AI model capabilities

```bash
feat(auth): add JWT token refresh mechanism
feat(ui): implement dark mode toggle
feat(ai): add sentiment analysis model
```

#### `fix` - Bug Fixes
- Fixes for existing functionality
- Security patches
- Performance fixes
- UI/UX improvements

```bash
fix(api): resolve memory leak in user service
fix(ui): correct button alignment on mobile
fix(ai): handle edge case in model prediction
```

#### `docs` - Documentation
- Documentation updates
- README changes
- API documentation
- Code comments

```bash
docs(api): update authentication endpoint examples
docs(setup): add uv installation instructions
docs: fix typos in contributing guide
```

### Secondary Types

#### `style` - Code Style
- Formatting changes
- Missing semicolons
- Whitespace changes
- Code style improvements

```bash
style(backend): format code with black
style(frontend): fix ktlint warnings
style: remove trailing whitespace
```

#### `refactor` - Code Refactoring
- Code restructuring without changing functionality
- Performance improvements
- Code organization

```bash
refactor(auth): extract validation logic to separate module
refactor(ai): optimize model loading performance
refactor: reorganize utility functions
```

#### `test` - Testing
- Adding tests
- Updating existing tests
- Test configuration changes

```bash
test(auth): add unit tests for JWT validation
test(ai): add integration tests for model pipeline
test: increase coverage for user service
```

#### `chore` - Maintenance
- Dependency updates
- Build configuration
- CI/CD changes
- Tool configuration

```bash
chore(deps): update fastapi to 0.104.0
chore(ci): add security scanning workflow
chore: update pre-commit hooks configuration
```

#### `perf` - Performance
- Performance improvements
- Optimization changes
- Resource usage improvements

```bash
perf(api): optimize database query performance
perf(ai): reduce model inference time
perf: implement caching for frequent requests
```

#### `ci` - Continuous Integration
- CI/CD pipeline changes
- GitHub Actions updates
- Build script modifications

```bash
ci: add automated testing workflow
ci(deploy): update production deployment script
ci: fix docker build caching issues
```

#### `build` - Build System
- Build tool changes
- Dependency management
- Package configuration

```bash
build: update pyproject.toml configuration
build(docker): optimize container image size
build: add uv lock file generation
```

#### `revert` - Reverts
- Reverting previous commits
- Rolling back changes

```bash
revert: revert "feat(auth): add OAuth integration"
revert: rollback database migration changes
```

## 🎯 Scope Guidelines

Scopes provide additional context about the change location:

### Backend Scopes
- `api` - API endpoints and routes
- `auth` - Authentication and authorization
- `db` - Database models and migrations
- `service` - Business logic services
- `config` - Configuration files
- `middleware` - Middleware components

### Frontend Scopes
- `ui` - User interface components
- `navigation` - App navigation
- `auth` - Authentication flows
- `api` - API integration
- `utils` - Utility functions
- `theme` - Styling and theming

### AI Model Scopes
- `model` - Model architecture and training
- `data` - Data processing and preparation
- `inference` - Model inference and serving
- `training` - Training scripts and pipelines
- `evaluation` - Model evaluation and metrics

### General Scopes
- `docs` - Documentation
- `tests` - Testing
- `ci` - Continuous integration
- `deps` - Dependencies
- `config` - Configuration

## ✍️ Writing Guidelines

### Description Rules
1. **Use imperative mood**: "add" not "added" or "adds"
2. **Start with lowercase**: "fix user login" not "Fix user login"
3. **No period at end**: "add new feature" not "add new feature."
4. **Be specific**: "fix login bug" → "fix password validation error"
5. **Keep it short**: Maximum 50 characters for the header

### Body Guidelines
1. **Explain the why**: Why was this change necessary?
2. **Provide context**: What problem does this solve?
3. **Mention side effects**: Any breaking changes or impacts
4. **Reference issues**: Link to related issues or tickets

### Footer Guidelines
1. **Breaking changes**: Start with "BREAKING CHANGE:"
2. **Issue references**: "Closes #123", "Fixes #456", "Refs #789"
3. **Co-authors**: "Co-authored-by: Name <email@example.com>"

## 📚 Examples

### Simple Commit
```bash
feat(auth): add password reset functionality
```

### Commit with Body
```bash
fix(api): resolve race condition in user creation

The user creation endpoint was experiencing race conditions when
multiple requests were made simultaneously. This fix adds proper
locking mechanism to prevent duplicate user creation.

Fixes #234
```

### Breaking Change
```bash
feat(api): redesign authentication endpoints

BREAKING CHANGE: The authentication API has been redesigned.
The /login endpoint now returns a different response format.
Update your client code accordingly.

- Changed response format from {token} to {access_token, refresh_token}
- Added token expiration information
- Removed deprecated /auth/validate endpoint

Closes #123
```

### Multiple Changes
```bash
feat(ai): implement text classification model

- Add BERT-based text classifier
- Implement training pipeline with early stopping
- Add model evaluation metrics
- Create inference API endpoint

The model achieves 94% accuracy on the test dataset and supports
real-time classification with sub-100ms response times.

Closes #456, #789
```

### Revert Commit
```bash
revert: revert "feat(auth): add OAuth integration"

This reverts commit 1234567890abcdef due to security concerns
identified in the OAuth implementation. Will be re-implemented
with proper security measures.

Refs #999
```

## 🔧 Tools and Automation

### Git Commit Template
A commit message template is automatically configured:

```bash
# .gitmessage template is set up automatically
git config commit.template .gitmessage
```

### Pre-commit Hooks
Pre-commit hooks validate commit messages:

```yaml
# .pre-commit-config.yaml includes commit message validation
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v2.4.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
```

### Commit Message Validation
```bash
# Validate commit message format
npx commitlint --from HEAD~1 --to HEAD --verbose

# Interactive commit with validation
npx git-cz
```

### IDE Integration
- **VS Code**: Install "Conventional Commits" extension
- **IntelliJ/Android Studio**: Install "Git Commit Template" plugin
- **Vim**: Use commit message templates

## ❌ Common Mistakes

### ❌ Bad Examples
```bash
# Too vague
fix: bug fix

# Wrong tense
feat: added new feature

# Too long
feat(auth): implement comprehensive user authentication system with JWT tokens and refresh mechanism

# Missing type
update user service

# Wrong capitalization
Fix: User Login Issue

# Period at end
feat(ui): add dark mode.

# Not imperative
feat(api): adding new endpoint
```

### ✅ Good Examples
```bash
# Clear and specific
fix(auth): resolve password validation error

# Proper imperative mood
feat(ui): add dark mode toggle

# Appropriate length
feat(auth): implement JWT refresh mechanism

# Proper format
refactor(api): extract user validation logic

# Correct capitalization
fix(db): resolve connection timeout issue

# No period
feat(ai): add sentiment analysis model

# Imperative mood
feat(api): add user profile endpoint
```

## 🔍 Commit Message Checklist

Before committing, ensure your message:

- [ ] Follows the conventional commit format
- [ ] Uses appropriate type and scope
- [ ] Has a clear, descriptive subject line
- [ ] Uses imperative mood ("add" not "added")
- [ ] Starts with lowercase (except proper nouns)
- [ ] Has no period at the end of subject
- [ ] Is under 50 characters for subject line
- [ ] Includes body if change is complex
- [ ] References related issues if applicable
- [ ] Mentions breaking changes if applicable

## 🚀 Advanced Usage

### Semantic Versioning Integration
Commit types automatically determine version bumps:
- `feat`: Minor version bump (1.1.0 → 1.2.0)
- `fix`: Patch version bump (1.1.0 → 1.1.1)
- `BREAKING CHANGE`: Major version bump (1.1.0 → 2.0.0)

### Automated Changelog
Conventional commits enable automatic changelog generation:
```bash
# Generate changelog from commits
npx conventional-changelog -p angular -i CHANGELOG.md -s
```

### Release Automation
Commits trigger automated releases:
```bash
# Semantic release based on commit messages
npx semantic-release
```

---

**Remember**: Good commit messages are a gift to your future self and your teammates. Take the time to write them well! 🎁
