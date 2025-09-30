# Development Setup

Set up your development environment for contributing to UUID-Forge.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**: UUID-Forge requires modern Python features
- **uv**: Fast Python package installer and resolver
- **Git**: Version control system
- **Code Editor**: VS Code, PyCharm, or your preferred editor

## Installation

### 1. Install uv

If you don't have uv installed:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/uuid-forge.git
cd uuid-forge
```

### 3. Set Up Development Environment

```bash
# Create virtual environment and install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 4. Install Pre-commit Hooks

```bash
uv run pre-commit install
```

## Development Dependencies

The development environment includes:

### Core Dependencies

- **typer**: CLI framework
- **rich**: Rich text and beautiful formatting
- **pydantic**: Data validation (if used)

### Development Tools

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance testing
- **hypothesis**: Property-based testing

### Code Quality

- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Fast Python linter
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality

### Documentation

- **mkdocs**: Documentation generator
- **mkdocs-material**: Material theme for MkDocs
- **mkdocstrings**: API documentation from docstrings

## Project Structure

```
uuid-forge/
├── .github/                 # GitHub workflows and templates
│   └── workflows/
│       ├── ci.yml          # Continuous integration
│       └── release.yml     # Release automation
├── .vscode/                # VS Code configuration
│   ├── settings.json       # Editor settings
│   └── launch.json         # Debug configuration
├── docs/                   # Documentation source
│   ├── index.md           # Homepage
│   ├── getting-started/   # Getting started guides
│   ├── guide/             # User guides
│   ├── api/               # API reference
│   ├── use-cases/         # Use case examples
│   └── development/       # Development docs
├── src/uuid_forge/         # Main package
│   ├── __init__.py        # Package initialization
│   ├── core.py            # Core UUID generation
│   ├── config.py          # Configuration management
│   └── cli.py             # Command-line interface
├── tests/                  # Test suite
│   ├── conftest.py        # Test configuration
│   ├── test_core.py       # Core functionality tests
│   ├── test_config.py     # Configuration tests
│   ├── test_cli.py        # CLI tests
│   └── integration/       # Integration tests
├── .gitignore             # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit configuration
├── mkdocs.yml             # Documentation configuration
├── pyproject.toml         # Project configuration
└── README.md              # Project overview
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code following the project conventions:

- **Type hints**: Use type hints for all functions
- **Docstrings**: Google-style docstrings
- **Testing**: Write tests for new functionality
- **Documentation**: Update docs for user-facing changes

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=uuid_forge --cov-report=html

# Run specific test file
uv run pytest tests/test_core.py

# Run tests matching pattern
uv run pytest -k "test_uuid_generation"
```

### 4. Check Code Quality

```bash
# Format code
uv run black src tests

# Sort imports
uv run isort src tests

# Check linting
uv run ruff check src tests

# Type checking
uv run mypy src

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### 5. Build Documentation

```bash
# Build documentation
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add new UUID generation feature"
```

The pre-commit hooks will automatically run and ensure code quality.

## IDE Configuration

### VS Code Setup

Recommended VS Code extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "ms-python.pytest",
    "yzhang.markdown-all-in-one"
  ]
}
```

VS Code settings (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "./.venv/bin/pytest",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm Setup

1. **Open Project**: Open the `uuid-forge` directory
2. **Configure Interpreter**: Set Python interpreter to `.venv/bin/python`
3. **Enable Tools**:
   - Code → Reformat Code (Black)
   - Code → Optimize Imports (isort)
   - Enable type checking in settings

## Testing

### Test Categories

**Unit Tests**: Test individual functions and classes

```bash
uv run pytest tests/test_core.py::test_uuid_generation
```

**Integration Tests**: Test component interactions

```bash
uv run pytest tests/integration/
```

**Property Tests**: Test with generated data using Hypothesis

```bash
uv run pytest tests/test_properties.py
```

**Performance Tests**: Benchmark performance

```bash
uv run pytest tests/test_performance.py --benchmark-only
```

### Writing Tests

Example test structure:

```python
import pytest
from uuid_forge import UUIDGenerator

class TestUUIDGeneration:
    def setUp(self):
        self.generator = UUIDGenerator(namespace="test")

    def test_deterministic_generation(self):
        """Test that UUID generation is deterministic."""
        uuid1 = self.generator.generate("test-input")
        uuid2 = self.generator.generate("test-input")

        assert uuid1 == uuid2
        assert len(uuid1) == 36

    @pytest.mark.parametrize("input_data", [
        "string",
        {"key": "value"},
        ["list", "data"],
        42
    ])
    def test_various_input_types(self, input_data):
        """Test UUID generation with various input types."""
        uuid_result = self.generator.generate(input_data)

        assert isinstance(uuid_result, str)
        assert len(uuid_result) == 36
```

### Test Configuration

The `conftest.py` file contains shared test fixtures:

```python
import pytest
from uuid_forge import UUIDGenerator

@pytest.fixture
def test_generator():
    """Provide a test UUID generator."""
    return UUIDGenerator(namespace="test-namespace")

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "users": [
            {"email": "user1@test.com", "name": "User 1"},
            {"email": "user2@test.com", "name": "User 2"}
        ],
        "orders": [
            {"id": "order1", "total": 100.0},
            {"id": "order2", "total": 200.0}
        ]
    }
```

## Debugging

### VS Code Debugging

Launch configuration (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    },
    {
      "name": "Python: Test Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "UUID-Forge CLI",
      "type": "python",
      "request": "launch",
      "module": "uuid_forge.cli",
      "args": ["generate", "test-input"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### Debug Configuration

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug information")
```

## Performance Profiling

### Profile Code Performance

```bash
# Profile with cProfile
python -m cProfile -o profile.stats -m uuid_forge.cli generate "test-data"

# Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

### Memory Profiling

```bash
# Install memory profiler
uv add --dev memory-profiler

# Profile memory usage
python -m memory_profiler uuid_forge/core.py
```

### Benchmark Tests

```python
import pytest
from uuid_forge import UUIDGenerator

@pytest.mark.benchmark
def test_uuid_generation_performance(benchmark):
    """Benchmark UUID generation performance."""
    generator = UUIDGenerator(namespace="benchmark")

    result = benchmark(generator.generate, "benchmark-data")

    assert len(result) == 36
```

## Documentation Development

### Local Documentation Server

```bash
# Start local server with auto-reload
uv run mkdocs serve

# Build documentation
uv run mkdocs build

# Deploy to GitHub Pages (maintainers only)
uv run mkdocs gh-deploy
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add links between related sections
- Follow the existing style and structure

## Common Tasks

### Add New Dependency

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update lockfile
uv lock
```

### Update Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest
```

### Release Preparation

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Run full test suite
uv run pytest

# Build package
uv build

# Check package
uv run twine check dist/*
```

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search GitHub issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Submit PRs for feedback

For development questions, include:

- Python version
- Operating system
- Full error messages
- Minimal reproduction example
