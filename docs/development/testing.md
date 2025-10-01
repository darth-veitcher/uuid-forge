# Development Testing

Comprehensive guide to testing practices and infrastructure for UUID-Forge development.

## Testing Philosophy

UUID-Forge follows a comprehensive testing strategy that ensures:

- **Correctness**: All functionality works as specified
- **Determinism**: UUIDs are consistently generated
- **Performance**: Generation is fast and efficient
- **Reliability**: Code works across different environments
- **Maintainability**: Tests are clear and maintainable

## Test Structure

### Test Organization

```
tests/
├── conftest.py              # Shared test configuration
├── test_core.py             # Core functionality tests
├── test_config.py           # Configuration tests
├── test_cli.py              # CLI tests
├── test_init.py             # Package initialization tests
├── test_version.py          # Version tests
├── integration/             # Integration tests
│   ├── test_database.py     # Database integration
│   ├── test_api.py          # API integration
│   └── test_cli_integration.py # CLI integration
├── performance/             # Performance tests
│   ├── test_benchmarks.py   # Benchmark tests
│   └── test_memory.py       # Memory usage tests
└── property/                # Property-based tests
    ├── test_determinism.py  # Determinism properties
    └── test_uniqueness.py   # Uniqueness properties
```

### Test Categories

**Unit Tests**: Test individual functions and classes in isolation
**Integration Tests**: Test component interactions and workflows
**Property Tests**: Test mathematical properties using generated data
**Performance Tests**: Benchmark and validate performance requirements
**Regression Tests**: Prevent previously fixed bugs from reoccurring

## Unit Testing

### Core Functionality Tests

```python
import pytest
import uuid
from uuid_forge.core import UUIDGenerator, IDConfig

class TestUUIDGenerator:
    """Test core UUID generation functionality."""

    def setUp(self):
        self.config = IDConfig(namespace="test-namespace")
        self.generator = UUIDGenerator(self.config)

    def test_deterministic_generation(self):
        """Test that same input produces same UUID."""
        input_data = "test-input"

        uuid1 = self.generator.generate(input_data)
        uuid2 = self.generator.generate(input_data)

        assert uuid1 == uuid2
        assert isinstance(uuid1, str)
        assert len(uuid1) == 36

    def test_different_inputs_different_uuids(self):
        """Test that different inputs produce different UUIDs."""
        uuid1 = self.generator.generate("input1")
        uuid2 = self.generator.generate("input2")

        assert uuid1 != uuid2

    def test_valid_uuid_format(self):
        """Test that generated UUIDs have valid format."""
        uuid_result = self.generator.generate("test")

        # Should be parseable as UUID
        parsed_uuid = uuid.UUID(uuid_result)
        assert str(parsed_uuid) == uuid_result

        # Should have correct format
        assert len(uuid_result) == 36
        assert uuid_result.count('-') == 4

    @pytest.mark.parametrize("input_data", [
        "string",
        {"key": "value"},
        ["list", "item"],
        42,
        3.14,
        True,
        None
    ])
    def test_various_input_types(self, input_data):
        """Test UUID generation with various input types."""
        uuid_result = self.generator.generate(input_data)

        assert isinstance(uuid_result, str)
        assert len(uuid_result) == 36

        # Same input should produce same UUID
        uuid_again = self.generator.generate(input_data)
        assert uuid_result == uuid_again

    def test_namespace_isolation(self):
        """Test that different namespaces produce different UUIDs."""
        config1 = IDConfig(namespace="namespace1")
        config2 = IDConfig(namespace="namespace2")

        gen1 = UUIDGenerator(config1)
        gen2 = UUIDGenerator(config2)

        input_data = "same-input"
        uuid1 = gen1.generate(input_data)
        uuid2 = gen2.generate(input_data)

        assert uuid1 != uuid2

    def test_empty_input_handling(self):
        """Test handling of empty inputs."""
        empty_inputs = ["", {}, [], None]

        for empty_input in empty_inputs:
            uuid_result = self.generator.generate(empty_input)
            assert isinstance(uuid_result, str)
            assert len(uuid_result) == 36
```

### Configuration Tests

```python
from uuid_forge.config import load_config_from_env, init_config_file
from uuid_forge.core import IDConfig
import os
import tempfile

class TestConfiguration:
    """Test configuration loading and validation."""

    def test_default_config(self):
        """Test default configuration values."""
        config = IDConfig()

        assert config.namespace is not None
        assert isinstance(config.salt, str)
        assert len(config.salt) > 0

    def test_custom_namespace(self):
        """Test custom namespace configuration."""
        custom_namespace = "custom-test-namespace"
        config = IDConfig(namespace=custom_namespace)

        assert config.namespace == custom_namespace

    def test_environment_config_loading(self):
        """Test loading configuration from environment variables."""
        test_namespace = "env-test-namespace"
        test_salt = "env-test-salt"

        # Set environment variables
        os.environ["UUID_FORGE_NAMESPACE"] = test_namespace
        os.environ["UUID_FORGE_SALT"] = test_salt

        try:
            config = load_config_from_env()
            assert config.namespace == test_namespace
            assert config.salt == test_salt
        finally:
            # Cleanup
            del os.environ["UUID_FORGE_NAMESPACE"]
            del os.environ["UUID_FORGE_SALT"]

    def test_config_file_creation(self):
        """Test configuration file creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.yaml")

            init_config_file(config_path)

            assert os.path.exists(config_path)

            # File should contain expected content
            with open(config_path, 'r') as f:
                content = f.read()
                assert "namespace:" in content
                assert "salt:" in content
```

### CLI Tests

```python
from typer.testing import CliRunner
from uuid_forge.cli import app
import json

class TestCLI:
    """Test command-line interface."""

    def setUp(self):
        self.runner = CliRunner()

    def test_generate_command(self):
        """Test basic UUID generation command."""
        result = self.runner.invoke(app, ["generate", "test-input"])

        assert result.exit_code == 0
        output = result.stdout.strip()
        assert len(output) == 36
        assert output.count('-') == 4

    def test_generate_multiple_inputs(self):
        """Test generating UUIDs for multiple inputs."""
        result = self.runner.invoke(app, [
            "generate", "input1", "input2", "input3"
        ])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 3

        # All should be valid UUIDs
        for line in lines:
            assert len(line) == 36
            assert line.count('-') == 4

        # All should be different
        assert len(set(lines)) == 3

    def test_namespace_option(self):
        """Test namespace option."""
        result1 = self.runner.invoke(app, [
            "generate", "--namespace", "ns1", "test"
        ])
        result2 = self.runner.invoke(app, [
            "generate", "--namespace", "ns2", "test"
        ])

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        uuid1 = result1.stdout.strip()
        uuid2 = result2.stdout.strip()

        # Different namespaces should produce different UUIDs
        assert uuid1 != uuid2

    def test_config_commands(self):
        """Test configuration management commands."""
        # Test config show
        result = self.runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

        # Output should contain configuration information
        assert "namespace" in result.stdout.lower()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "uuid-forge" in result.stdout.lower()

    def test_help_commands(self):
        """Test help commands."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "generate" in result.stdout

        result = self.runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "namespace" in result.stdout
```

## Integration Testing

### Database Integration

```python
import pytest
import sqlite3
from uuid_forge import UUIDGenerator

class TestDatabaseIntegration:
    """Test integration with database systems."""

    @pytest.fixture
    def test_db(self):
        """Create test database."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE orders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        conn.commit()
        yield conn
        conn.close()

    def test_user_order_relationship(self, test_db):
        """Test maintaining relationships with deterministic UUIDs."""
        user_gen = UUIDGenerator(IDConfig(namespace=Namespace("db-users"), salt="v1"))
        order_gen = UUIDGenerator(IDConfig(namespace=Namespace("db-orders"), salt="v1"))

        cursor = test_db.cursor()

        # Create user with deterministic UUID
        user_email = "dbtest@example.com"
        user_id = user_gen.generate("user", email=user_email)

        cursor.execute(
            "INSERT INTO users (id, email, name) VALUES (?, ?, ?)",
            (user_id, user_email, "Test User")
        )

        # Create order with deterministic UUID
        order_data = {
            "user_id": user_id,
            "total": 100.50,
            "items": ["item1", "item2"]
        }
        order_id = order_gen.generate(order_data)

        cursor.execute(
            "INSERT INTO orders (id, user_id, total) VALUES (?, ?, ?)",
            (order_id, user_id, 100.50)
        )

        test_db.commit()

        # Verify relationship
        cursor.execute("""
            SELECT u.email, o.total
            FROM users u
            JOIN orders o ON u.id = o.user_id
            WHERE u.id = ?
        """, (user_id,))

        result = cursor.fetchone()
        assert result is not None
        assert result[0] == user_email
        assert result[1] == 100.50

        # Verify UUIDs are deterministic
        user_id_2 = user_gen.generate("user", email=user_email)
        order_id_2 = order_gen.generate(order_data)

        assert user_id == user_id_2
        assert order_id == order_id_2
```

### API Integration

```python
import pytest
import requests_mock
from uuid_forge import UUIDGenerator

class TestAPIIntegration:
    """Test integration with API services."""

    def test_rest_api_integration(self):
        """Test integration with REST API."""
        user_gen = UUIDGenerator(IDConfig(namespace=Namespace("api-users"), salt="v1"))

        with requests_mock.Mocker() as m:
            user_email = "apitest@example.com"
            user_id = user_gen.generate("user", email=user_email)

            # Mock API response
            m.post(
                "http://api.example.com/users",
                json={"id": user_id, "email": user_email},
                status_code=201
            )

            # Test API call
            response = requests.post(
                "http://api.example.com/users",
                json={"email": user_email}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == user_id
            assert data["email"] == user_email
```

## Property-Based Testing

### Determinism Properties

```python
from hypothesis import given, strategies as st
from uuid_forge import UUIDGenerator
import uuid

class TestDeterminismProperties:
    """Test determinism properties using Hypothesis."""

    def setUp(self):
        self.generator = UUIDGenerator(IDConfig(namespace=Namespace("property-test"), salt="v1"))

    @given(st.text(min_size=1))
    def test_determinism_property(self, input_text):
        """Property: Same input always produces same output."""
        uuid1 = self.generator.generate(input_text)
        uuid2 = self.generator.generate(input_text)

        assert uuid1 == uuid2

    @given(st.text(min_size=1))
    def test_valid_uuid_property(self, input_text):
        """Property: All outputs are valid UUIDs."""
        uuid_result = self.generator.generate(input_text)

        # Should be parseable as UUID
        parsed = uuid.UUID(uuid_result)
        assert str(parsed) == uuid_result

        # Should have correct length and format
        assert len(uuid_result) == 36
        assert uuid_result.count('-') == 4

    @given(st.lists(st.text(min_size=1), min_size=2, unique=True))
    def test_uniqueness_property(self, input_list):
        """Property: Different inputs produce different UUIDs."""
        uuids = [self.generator.generate(inp) for inp in input_list]

        # All UUIDs should be unique
        assert len(set(uuids)) == len(uuids)

    @given(st.dictionaries(st.text(), st.text(), min_size=1))
    def test_dict_determinism_property(self, input_dict):
        """Property: Dictionary inputs produce deterministic UUIDs."""
        uuid1 = self.generator.generate(input_dict)
        uuid2 = self.generator.generate(input_dict)

        assert uuid1 == uuid2
```

## Performance Testing

### Benchmark Tests

```python
import pytest
from uuid_forge import UUIDGenerator
import time

class TestPerformance:
    """Test performance requirements."""

    def setUp(self):
        self.generator = UUIDGenerator(IDConfig(namespace=Namespace("perf-test"), salt="v1"))

    @pytest.mark.benchmark
    def test_single_generation_speed(self, benchmark):
        """Benchmark single UUID generation."""
        result = benchmark(self.generator.generate, "benchmark-input")

        assert len(result) == 36

    def test_batch_generation_performance(self):
        """Test batch generation performance."""
        test_inputs = [f"input-{i}" for i in range(1000)]

        start_time = time.time()
        uuids = [self.generator.generate(inp) for inp in test_inputs]
        end_time = time.time()

        generation_time = end_time - start_time

        # Should generate 1000 UUIDs in under 100ms
        assert generation_time < 0.1
        assert len(uuids) == 1000
        assert len(set(uuids)) == 1000  # All unique

    def test_memory_efficiency(self):
        """Test memory usage during generation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Generate many UUIDs
        large_inputs = [f"input-{i}" for i in range(10000)]
        uuids = [self.generator.generate(inp) for inp in large_inputs]

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Memory increase should be reasonable
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB
        assert len(uuids) == 10000

    @pytest.mark.slow
    def test_large_scale_performance(self):
        """Test performance with large-scale generation."""
        # Generate 100,000 UUIDs
        start_time = time.time()

        uuids = []
        for i in range(100000):
            uuid_result = self.generator.generate(f"large-scale-{i}")
            uuids.append(uuid_result)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in reasonable time
        assert total_time < 10.0  # Less than 10 seconds
        assert len(uuids) == 100000
        assert len(set(uuids)) == 100000  # All unique
```

### Memory Profiling

```python
import pytest
from memory_profiler import profile
from uuid_forge import UUIDGenerator

class TestMemoryUsage:
    """Test memory usage patterns."""

    @profile
    def test_memory_profile_batch_generation(self):
        """Profile memory usage during batch generation."""
        generator = UUIDGenerator(IDConfig(namespace=Namespace("memory-test"), salt="v1"))

        # Generate many UUIDs to observe memory pattern
        uuids = []
        for i in range(10000):
            uuid_result = generator.generate(f"memory-test-{i}")
            uuids.append(uuid_result)

        return len(uuids)
```

## Test Configuration and Fixtures

### Shared Test Configuration

```python
# conftest.py
import pytest
from uuid_forge import UUIDGenerator
from uuid_forge.core import IDConfig
import tempfile
import os

@pytest.fixture
def test_generator():
    """Provide a test UUID generator with consistent namespace."""
    config = IDConfig(namespace="test-namespace")
    return UUIDGenerator(config)

@pytest.fixture
def temp_config_file():
    """Provide a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
namespace: test-config-namespace
salt: test-config-salt
""")
        config_path = f.name

    yield config_path

    # Cleanup
    os.unlink(config_path)

@pytest.fixture
def sample_test_data():
    """Provide sample test data."""
    return {
        "users": [
            {"email": "user1@test.com", "name": "User One"},
            {"email": "user2@test.com", "name": "User Two"},
            {"email": "user3@test.com", "name": "User Three"}
        ],
        "orders": [
            {"id": "order1", "user_email": "user1@test.com", "total": 100.0},
            {"id": "order2", "user_email": "user2@test.com", "total": 200.0}
        ]
    }

@pytest.fixture(scope="session")
def performance_generator():
    """Provide a generator for performance tests."""
    config = IDConfig(namespace="performance-test")
    return UUIDGenerator(config)

# Test markers
pytest.mark.slow = pytest.mark.mark_slow("Slow running tests")
pytest.mark.benchmark = pytest.mark.benchmark("Benchmark tests")
pytest.mark.integration = pytest.mark.integration("Integration tests")
```

## Test Execution

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest -m "not slow"  # Skip slow tests
uv run pytest -m benchmark   # Only benchmark tests
uv run pytest -m integration # Only integration tests

# Run with coverage
uv run pytest --cov=uuid_forge --cov-report=html

# Run specific test file
uv run pytest tests/test_core.py

# Run specific test
uv run pytest tests/test_core.py::TestUUIDGenerator::test_deterministic_generation

# Run tests matching pattern
uv run pytest -k "test_uuid"

# Run tests with verbose output
uv run pytest -v

# Run tests with detailed output
uv run pytest -vv

# Stop on first failure
uv run pytest -x

# Run failed tests from last run
uv run pytest --lf
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: |
          pip install uv

      - name: Install dependencies
        run: |
          uv sync --dev

      - name: Run tests
        run: |
          uv run pytest --cov=uuid_forge --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Test Best Practices

### Writing Good Tests

1. **Clear Names**: Test names should describe what is being tested
2. **Single Responsibility**: Each test should test one thing
3. **Deterministic**: Tests should not depend on external factors
4. **Fast**: Unit tests should run quickly
5. **Independent**: Tests should not depend on each other

### Test Organization

1. **Group Related Tests**: Use classes to group related test methods
2. **Use Fixtures**: Share setup code using pytest fixtures
3. **Parametrize Tests**: Use `@pytest.mark.parametrize` for similar tests
4. **Mark Tests**: Use pytest marks to categorize tests

### Coverage Goals

- **Unit Tests**: Aim for >95% code coverage
- **Integration Tests**: Cover critical workflows
- **Property Tests**: Validate mathematical properties
- **Performance Tests**: Ensure performance requirements

## Debugging Tests

### Debug Failing Tests

```bash
# Run with pdb debugger
uv run pytest --pdb

# Run specific failing test with verbose output
uv run pytest tests/test_core.py::test_failing -vv

# Show local variables in traceback
uv run pytest --tb=long
```

### Test Output Analysis

```bash
# Show print statements
uv run pytest -s

# Show test duration
uv run pytest --durations=10

# Generate HTML coverage report
uv run pytest --cov=uuid_forge --cov-report=html
open htmlcov/index.html
```

## Next Steps

- [Release Process](release.md) - Preparing releases
- [Contributing](contributing.md) - Contributing guidelines
- [Best Practices](../guide/best-practices.md) - Code best practices
