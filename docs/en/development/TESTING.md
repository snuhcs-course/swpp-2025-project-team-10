# Testing Guidelines and Practices

This document outlines testing strategies, practices, and guidelines for the SWPP AI Application project.

## 📋 Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Testing Pyramid](#testing-pyramid)
- [Python Testing](#python-testing)
- [Kotlin Testing](#kotlin-testing)
- [AI Model Testing](#ai-model-testing)
- [Integration Testing](#integration-testing)
- [Test Organization](#test-organization)
- [Continuous Integration](#continuous-integration)

## 🎯 Testing Philosophy

### Core Principles
- **Test Early, Test Often**: Write tests as you develop features
- **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E tests
- **Fast Feedback**: Tests should run quickly to enable rapid development
- **Reliable Tests**: Tests should be deterministic and not flaky
- **Maintainable Tests**: Tests should be easy to understand and modify

### Testing Goals
- **Correctness**: Ensure code behaves as expected
- **Regression Prevention**: Catch bugs before they reach production
- **Documentation**: Tests serve as living documentation
- **Refactoring Safety**: Enable confident code changes
- **Quality Assurance**: Maintain high code quality standards

## 🔺 Testing Pyramid

```
    /\
   /  \     E2E Tests (Few)
  /____\    - Full system integration
 /      \   - User journey testing
/________\  - Slow, expensive, brittle

/          \  Integration Tests (Some)
/____________\ - Component interaction
               - API testing
               - Database integration

/              \  Unit Tests (Many)
/________________\ - Individual functions/methods
                   - Fast, reliable, isolated
                   - Mock external dependencies
```

### Test Distribution
- **70%** Unit Tests
- **20%** Integration Tests  
- **10%** End-to-End Tests

## 🐍 Python Testing

### Testing Framework
We use **pytest** for all Python testing with these plugins:
- `pytest-asyncio`: For async test support
- `pytest-cov`: For coverage reporting
- `pytest-mock`: For mocking utilities
- `pytest-xdist`: For parallel test execution

### Test Structure
```python
# test_user_service.py
import pytest
from unittest.mock import Mock, patch
from src.services.user_service import UserService
from src.models.user import User

class TestUserService:
    """Test suite for UserService."""
    
    @pytest.fixture
    def mock_database(self):
        """Mock database for testing."""
        return Mock()
    
    @pytest.fixture
    def user_service(self, mock_database):
        """UserService instance with mocked dependencies."""
        return UserService(database=mock_database)
    
    def test_create_user_success(self, user_service, mock_database):
        """Test successful user creation."""
        # Arrange
        user_data = {"email": "test@example.com", "name": "Test User"}
        expected_user = User(id=1, **user_data)
        mock_database.create_user.return_value = expected_user
        
        # Act
        result = user_service.create_user(user_data)
        
        # Assert
        assert result == expected_user
        mock_database.create_user.assert_called_once_with(user_data)
    
    def test_create_user_duplicate_email(self, user_service, mock_database):
        """Test user creation with duplicate email."""
        # Arrange
        user_data = {"email": "existing@example.com", "name": "Test User"}
        mock_database.create_user.side_effect = ValueError("Email already exists")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_async_user_operation(self, user_service):
        """Test async user operations."""
        # Arrange
        user_id = 1
        
        # Act
        result = await user_service.get_user_async(user_id)
        
        # Assert
        assert result is not None
```

### Testing Best Practices

#### Naming Conventions
```python
# Test files: test_*.py
# Test classes: TestClassName
# Test methods: test_method_name_scenario

def test_calculate_accuracy_with_valid_inputs():
    """Test accuracy calculation with valid prediction and target arrays."""
    pass

def test_calculate_accuracy_with_empty_arrays():
    """Test accuracy calculation raises error with empty arrays."""
    pass

def test_calculate_accuracy_with_mismatched_lengths():
    """Test accuracy calculation raises error with mismatched array lengths."""
    pass
```

#### Fixtures and Mocking
```python
# conftest.py - Shared fixtures
import pytest
from src.database import Database
from src.models.user import User

@pytest.fixture(scope="session")
def test_database():
    """Create test database for session."""
    db = Database("sqlite:///:memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow()
    )

# Using fixtures in tests
def test_user_creation(test_database, sample_user):
    """Test user creation in database."""
    created_user = test_database.create_user(sample_user)
    assert created_user.id == sample_user.id
```

#### Parametrized Tests
```python
@pytest.mark.parametrize("input_data,expected", [
    ([1, 2, 3], 6),
    ([0, 0, 0], 0),
    ([-1, 1, 0], 0),
    ([10], 10),
])
def test_sum_calculation(input_data, expected):
    """Test sum calculation with various inputs."""
    result = calculate_sum(input_data)
    assert result == expected
```

### Running Python Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend/src --cov=ai-model/src

# Run specific test file
pytest backend/tests/test_user_service.py

# Run specific test method
pytest backend/tests/test_user_service.py::TestUserService::test_create_user_success

# Run tests matching pattern
pytest -k "test_user"

# Run tests with specific markers
pytest -m "unit"  # or "integration", "slow"

# Parallel execution
pytest -n auto
```

## 📱 Kotlin Testing

### Testing Framework
We use **JUnit 5** with these additional libraries:
- **MockK**: For mocking in Kotlin
- **Kotest**: For assertion library
- **Robolectric**: For Android unit tests
- **Espresso**: For UI testing

### Test Structure
```kotlin
// UserRepositoryTest.kt
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*

class UserRepositoryTest {
    
    private lateinit var mockDatabase: Database
    private lateinit var userRepository: UserRepository
    
    @BeforeEach
    fun setup() {
        mockDatabase = mockk()
        userRepository = UserRepository(mockDatabase)
    }
    
    @AfterEach
    fun tearDown() {
        clearAllMocks()
    }
    
    @Test
    fun `createUser should return user when successful`() = runTest {
        // Arrange
        val userData = UserData("test@example.com", "Test User")
        val expectedUser = User(1, userData.email, userData.name)
        coEvery { mockDatabase.insertUser(userData) } returns expectedUser
        
        // Act
        val result = userRepository.createUser(userData)
        
        // Assert
        assertEquals(expectedUser, result)
        coVerify { mockDatabase.insertUser(userData) }
    }
    
    @Test
    fun `createUser should throw exception when email exists`() = runTest {
        // Arrange
        val userData = UserData("existing@example.com", "Test User")
        coEvery { mockDatabase.insertUser(userData) } throws 
            DatabaseException("Email already exists")
        
        // Act & Assert
        assertThrows<DatabaseException> {
            userRepository.createUser(userData)
        }
    }
    
    @ParameterizedTest
    @ValueSource(strings = ["", " ", "invalid-email"])
    fun `createUser should validate email format`(invalidEmail: String) = runTest {
        // Arrange
        val userData = UserData(invalidEmail, "Test User")
        
        // Act & Assert
        assertThrows<ValidationException> {
            userRepository.createUser(userData)
        }
    }
}
```

### Android UI Testing
```kotlin
// MainActivityTest.kt
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MainActivityTest {
    
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)
    
    @Test
    fun loginFlow_withValidCredentials_shouldNavigateToHome() {
        // Arrange
        val validEmail = "test@example.com"
        val validPassword = "password123"
        
        // Act
        onView(withId(R.id.emailEditText))
            .perform(typeText(validEmail), closeSoftKeyboard())
        
        onView(withId(R.id.passwordEditText))
            .perform(typeText(validPassword), closeSoftKeyboard())
        
        onView(withId(R.id.loginButton))
            .perform(click())
        
        // Assert
        onView(withId(R.id.homeScreen))
            .check(matches(isDisplayed()))
    }
}
```

### Running Kotlin Tests
```bash
# Run all tests
cd frontend
./gradlew test

# Run unit tests only
./gradlew testDebugUnitTest

# Run instrumented tests
./gradlew connectedDebugAndroidTest

# Run specific test class
./gradlew test --tests "UserRepositoryTest"

# Run with coverage
./gradlew testDebugUnitTestCoverage
```

## 🤖 AI Model Testing

### Testing Challenges
- **Non-deterministic outputs**: Models may produce different results
- **Large datasets**: Testing with full datasets is impractical
- **Training time**: Model training takes significant time
- **Hardware dependencies**: GPU availability affects tests

### Testing Strategies

#### Model Architecture Tests
```python
# test_model_architecture.py
import torch
import pytest
from src.models.transformer_model import TransformerModel

class TestTransformerModel:
    """Test transformer model architecture."""
    
    @pytest.fixture
    def model_config(self):
        """Model configuration for testing."""
        return {
            "vocab_size": 1000,
            "hidden_size": 256,
            "num_layers": 4,
            "num_heads": 8,
            "max_length": 512
        }
    
    @pytest.fixture
    def model(self, model_config):
        """Transformer model instance."""
        return TransformerModel(**model_config)
    
    def test_model_initialization(self, model, model_config):
        """Test model initializes with correct parameters."""
        assert model.vocab_size == model_config["vocab_size"]
        assert model.hidden_size == model_config["hidden_size"]
        assert len(model.layers) == model_config["num_layers"]
    
    def test_forward_pass_shape(self, model):
        """Test forward pass produces correct output shape."""
        batch_size, seq_length = 2, 10
        input_ids = torch.randint(0, 1000, (batch_size, seq_length))
        
        output = model(input_ids)
        
        expected_shape = (batch_size, seq_length, model.vocab_size)
        assert output.shape == expected_shape
    
    def test_model_parameters_count(self, model):
        """Test model has expected number of parameters."""
        total_params = sum(p.numel() for p in model.parameters())
        # Assert parameter count is within expected range
        assert 1_000_000 <= total_params <= 10_000_000
```

#### Data Processing Tests
```python
# test_data_preprocessing.py
import pytest
import numpy as np
from src.data.preprocessor import TextPreprocessor

class TestTextPreprocessor:
    """Test text preprocessing functionality."""
    
    @pytest.fixture
    def preprocessor(self):
        """Text preprocessor instance."""
        return TextPreprocessor(max_length=128, vocab_size=1000)
    
    def test_tokenization(self, preprocessor):
        """Test text tokenization."""
        text = "Hello world! This is a test."
        tokens = preprocessor.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(token, int) for token in tokens)
    
    def test_padding(self, preprocessor):
        """Test sequence padding."""
        sequences = [[1, 2, 3], [4, 5], [6, 7, 8, 9, 10]]
        padded = preprocessor.pad_sequences(sequences, max_length=5)
        
        assert padded.shape == (3, 5)
        assert np.all(padded[1, 2:] == 0)  # Check padding
    
    @pytest.mark.parametrize("text,expected_length", [
        ("Short text", 2),
        ("", 0),
        ("A very long text that should be truncated properly", 10),
    ])
    def test_text_length_handling(self, preprocessor, text, expected_length):
        """Test handling of different text lengths."""
        tokens = preprocessor.tokenize(text, max_length=10)
        assert len(tokens) <= expected_length
```

#### Model Performance Tests
```python
# test_model_performance.py
import pytest
import torch
from src.models.classifier import TextClassifier
from src.evaluation.metrics import calculate_accuracy, calculate_f1

class TestModelPerformance:
    """Test model performance and metrics."""
    
    @pytest.fixture
    def sample_predictions(self):
        """Sample model predictions for testing."""
        return torch.tensor([
            [0.9, 0.1],  # Confident positive
            [0.3, 0.7],  # Confident negative
            [0.6, 0.4],  # Weak positive
            [0.2, 0.8],  # Confident negative
        ])
    
    @pytest.fixture
    def sample_targets(self):
        """Sample target labels."""
        return torch.tensor([1, 0, 1, 0])
    
    def test_accuracy_calculation(self, sample_predictions, sample_targets):
        """Test accuracy metric calculation."""
        accuracy = calculate_accuracy(sample_predictions, sample_targets)
        
        assert 0.0 <= accuracy <= 1.0
        assert accuracy == 0.75  # 3 out of 4 correct
    
    def test_f1_score_calculation(self, sample_predictions, sample_targets):
        """Test F1 score calculation."""
        f1_score = calculate_f1(sample_predictions, sample_targets)
        
        assert 0.0 <= f1_score <= 1.0
        assert isinstance(f1_score, float)
    
    @pytest.mark.slow
    def test_model_training_convergence(self):
        """Test that model training converges (slow test)."""
        model = TextClassifier(vocab_size=1000, num_classes=2)
        # Use small synthetic dataset for testing
        # Assert that loss decreases over training steps
        pass
```

### Running AI Model Tests
```bash
# Run all AI model tests
pytest ai-model/tests/

# Run fast tests only (skip slow training tests)
pytest ai-model/tests/ -m "not slow"

# Run with GPU if available
CUDA_VISIBLE_DEVICES=0 pytest ai-model/tests/

# Run specific test categories
pytest ai-model/tests/ -m "unit"
pytest ai-model/tests/ -m "integration"
```

## 🔗 Integration Testing

### API Integration Tests
```python
# test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client for API testing."""
        return TestClient(app)
    
    def test_user_creation_flow(self, client):
        """Test complete user creation flow."""
        # Create user
        user_data = {"email": "test@example.com", "name": "Test User"}
        response = client.post("/users", json=user_data)
        
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["email"] == user_data["email"]
        
        # Retrieve user
        user_id = created_user["id"]
        response = client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["id"] == user_id
    
    def test_ai_prediction_endpoint(self, client):
        """Test AI model prediction endpoint."""
        prediction_data = {"text": "This is a test message"}
        response = client.post("/predict", json=prediction_data)
        
        assert response.status_code == 200
        result = response.json()
        assert "prediction" in result
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
```

## 📁 Test Organization

### Directory Structure
```
backend/tests/
├── unit/                   # Unit tests
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/            # Integration tests
│   ├── test_api/
│   └── test_database/
└── conftest.py            # Shared fixtures

ai-model/tests/
├── unit/
│   ├── test_models/
│   ├── test_data/
│   └── test_training/
├── integration/
│   └── test_pipelines/
└── conftest.py

frontend/src/test/
├── java/                  # Unit tests
│   └── com/example/app/
└── androidTest/           # Instrumented tests
    └── com/example/app/
```

### Test Markers
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests that take more than 1 second",
    "gpu: Tests that require GPU",
    "external: Tests that require external services",
]
```

## 🚀 Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest --cov=backend/src --cov=ai-model/src
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  test-kotlin:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up JDK
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: Run tests
      run: |
        cd frontend
        ./gradlew test
```

### Test Coverage Goals
- **Overall**: Minimum 80% code coverage
- **Critical paths**: 95%+ coverage for core business logic
- **New code**: 90%+ coverage for all new features
- **AI models**: Focus on architecture and data processing tests

---

**Remember**: Good tests are an investment in code quality and team productivity. Write tests that provide value and confidence in your code.
