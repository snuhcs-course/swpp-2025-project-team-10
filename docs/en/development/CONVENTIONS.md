# Development Conventions

This document outlines the coding standards, conventions, and best practices for the SWPP AI Application project.

## 📋 Table of Contents

- [General Principles](#general-principles)
- [Python Conventions](#python-conventions)
- [Kotlin Conventions](#kotlin-conventions)
- [File Organization](#file-organization)
- [Naming Conventions](#naming-conventions)
- [Documentation Standards](#documentation-standards)
- [Code Quality Tools](#code-quality-tools)

## 🎯 General Principles

### Code Quality Standards
- **Readability First**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns throughout the codebase
- **Maintainability**: Write code that is easy to modify and extend
- **Performance**: Consider performance implications, especially for AI model code
- **Security**: Follow security best practices, especially for backend code

### Development Workflow
1. **Always** run code formatters before committing
2. **Always** write tests for new functionality
3. **Always** update documentation when making changes
4. **Never** commit directly to `main` branch
5. **Never** bypass pre-commit hooks

## 🐍 Python Conventions

### Code Style
- **Line Length**: Maximum 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes for strings, single quotes for string literals in code
- **Imports**: Follow isort configuration, group imports logically

### Formatting Tools
```bash
# Format Python code
./scripts/formatters/format_python.py

# Check formatting without changes
./scripts/formatters/format_python.py --check

# Show diffs
./scripts/formatters/format_python.py --diff
```

### Type Hints
- **Required** for all public functions and methods
- **Required** for all function parameters and return types
- Use `typing` module for complex types
- Use `Optional` for nullable parameters

```python
from typing import List, Optional, Dict, Any

def process_data(
    data: List[Dict[str, Any]], 
    filter_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Process data with optional filtering."""
    # Implementation here
    pass
```

### Documentation
- **Required** docstrings for all public classes, functions, and methods
- Use Google-style docstrings
- Include parameter types, return types, and examples

```python
def calculate_accuracy(predictions: List[float], targets: List[float]) -> float:
    """Calculate accuracy between predictions and targets.
    
    Args:
        predictions: List of predicted values
        targets: List of target values
        
    Returns:
        Accuracy score as a float between 0 and 1
        
    Raises:
        ValueError: If predictions and targets have different lengths
        
    Example:
        >>> calculate_accuracy([0.9, 0.8, 0.7], [1.0, 0.8, 0.6])
        0.93
    """
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")
    # Implementation here
```

### Error Handling
- Use specific exception types
- Always include meaningful error messages
- Log errors appropriately

```python
import logging

logger = logging.getLogger(__name__)

def load_model(model_path: str) -> Model:
    """Load model from file."""
    try:
        return torch.load(model_path)
    except FileNotFoundError:
        logger.error(f"Model file not found: {model_path}")
        raise ModelLoadError(f"Could not load model from {model_path}")
    except Exception as e:
        logger.error(f"Unexpected error loading model: {e}")
        raise
```

## 📱 Kotlin Conventions

### Code Style
- **Line Length**: Maximum 120 characters
- **Indentation**: 4 spaces (no tabs)
- **Braces**: Opening brace on same line
- **Naming**: camelCase for functions/variables, PascalCase for classes

### Formatting Tools
```bash
# Format Kotlin code
./scripts/formatters/format_kotlin.sh

# Check formatting without changes
./scripts/formatters/format_kotlin.sh --check
```

### Class Structure
```kotlin
class UserRepository(
    private val database: Database,
    private val logger: Logger
) {
    companion object {
        private const val TAG = "UserRepository"
        private const val MAX_RETRY_ATTEMPTS = 3
    }
    
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val user = database.getUserById(userId)
            Result.success(user)
        } catch (e: Exception) {
            logger.error(TAG, "Failed to get user: $userId", e)
            Result.failure(e)
        }
    }
}
```

### Documentation
- Use KDoc for public APIs
- Include parameter descriptions and return types
- Provide usage examples

```kotlin
/**
 * Calculates the similarity between two text strings.
 *
 * @param text1 The first text string to compare
 * @param text2 The second text string to compare
 * @param algorithm The similarity algorithm to use (default: COSINE)
 * @return A similarity score between 0.0 and 1.0
 *
 * @throws IllegalArgumentException if either text is empty
 *
 * @sample
 * ```kotlin
 * val similarity = calculateSimilarity("hello world", "hello kotlin")
 * println("Similarity: $similarity") // Output: Similarity: 0.67
 * ```
 */
fun calculateSimilarity(
    text1: String,
    text2: String,
    algorithm: SimilarityAlgorithm = SimilarityAlgorithm.COSINE
): Double {
    require(text1.isNotEmpty()) { "text1 cannot be empty" }
    require(text2.isNotEmpty()) { "text2 cannot be empty" }
    // Implementation here
}
```

## 📁 File Organization

### Directory Structure
```
backend/
├── src/
│   ├── api/           # API endpoints
│   ├── core/          # Core business logic
│   ├── models/        # Data models
│   ├── services/      # Business services
│   └── utils/         # Utility functions
├── tests/             # Test files
└── config/            # Configuration files

ai-model/
├── src/
│   ├── models/        # Model definitions
│   ├── training/      # Training scripts
│   ├── inference/     # Inference code
│   └── utils/         # Utility functions
├── notebooks/         # Jupyter notebooks
├── data/              # Data files
└── tests/             # Test files

frontend/
├── src/
│   ├── main/
│   │   ├── java/      # Kotlin source files
│   │   └── res/       # Resources
│   └── test/          # Test files
```

### File Naming
- **Python**: `snake_case.py`
- **Kotlin**: `PascalCase.kt`
- **Tests**: `test_*.py` or `*Test.kt`
- **Configuration**: `lowercase.toml`, `lowercase.yaml`

## 🏷️ Naming Conventions

### Variables and Functions
- **Python**: `snake_case`
- **Kotlin**: `camelCase`
- Use descriptive names that explain purpose
- Avoid abbreviations unless widely understood

### Classes and Interfaces
- **Python**: `PascalCase`
- **Kotlin**: `PascalCase`
- Use nouns for classes, adjectives for interfaces
- Suffix interfaces with "Interface" if needed

### Constants
- **Python**: `UPPER_SNAKE_CASE`
- **Kotlin**: `UPPER_SNAKE_CASE`
- Group related constants in classes or objects

### Database Tables and Columns
- **Tables**: `snake_case` (plural nouns)
- **Columns**: `snake_case`
- Use descriptive names, avoid abbreviations

## 📚 Documentation Standards

### Code Comments
- Explain **why**, not **what**
- Update comments when code changes
- Remove outdated comments
- Use TODO comments for future improvements

```python
# TODO: Implement caching for better performance
# FIXME: Handle edge case when input is empty
# NOTE: This algorithm assumes normalized input data
```

### README Files
- Each major component should have a README
- Include setup instructions, usage examples, and API documentation
- Keep README files up to date

### API Documentation
- Document all public APIs
- Include request/response examples
- Specify error codes and messages
- Use OpenAPI/Swagger for REST APIs

## 🔧 Code Quality Tools

### Automated Formatting
All code must pass through automated formatters before commit:

```bash
# Format all code
./scripts/formatters/format_all.sh

# Check all code formatting
./scripts/formatters/format_all.sh --check
```

### Python Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security analysis

### Kotlin Tools
- **ktlint**: Code formatting and linting
- **detekt**: Static analysis

### Pre-commit Hooks
Pre-commit hooks automatically run these tools. Never bypass them:

```bash
# Install pre-commit hooks (done automatically in setup)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## ✅ Checklist for Code Reviews

### General
- [ ] Code follows project conventions
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed

### Python Specific
- [ ] Type hints are present and correct
- [ ] Docstrings follow Google style
- [ ] Error handling is appropriate
- [ ] Imports are properly organized

### Kotlin Specific
- [ ] KDoc is present for public APIs
- [ ] Null safety is properly handled
- [ ] Resource management is correct
- [ ] Android best practices followed

## 🚫 Common Anti-patterns to Avoid

### General
- Magic numbers without explanation
- Deep nesting (> 3 levels)
- Functions longer than 50 lines
- Classes with too many responsibilities

### Python
- Using `except:` without specific exception types
- Mutable default arguments
- Not using context managers for resources
- Importing with `*`

### Kotlin
- Using `!!` operator unnecessarily
- Not handling nullable types properly
- Memory leaks in Android components
- Blocking main thread with long operations

---

**Remember**: These conventions exist to maintain code quality and team productivity. When in doubt, ask for clarification or propose improvements to these guidelines.
