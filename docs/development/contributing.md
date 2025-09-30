# Contributing to UUID-Forge

Thank you for your interest in contributing to UUID-Forge! This guide will help you get started with development and contribution.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git for version control

### Setting Up Development Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/uuid-forge.git
   cd uuid-forge
   ```

2. **Install dependencies:**

   ```bash
   uv sync --dev
   ```

3. **Activate the virtual environment:**

   ```bash
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

4. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

### Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=uuid_forge --cov-report=html
```

Run specific test categories:

```bash
# Unit tests only
uv run pytest tests/ -k "not integration"

# Integration tests only
uv run pytest tests/ -k "integration"

# Performance tests
uv run pytest tests/ -k "performance"
```

### Code Quality

We use several tools to maintain code quality:

**Formatting:**

```bash
uv run black src tests
uv run isort src tests
```

**Linting:**

```bash
uv run ruff check src tests
uv run mypy src
```

**All quality checks:**

```bash
uv run pre-commit run --all-files
```

## Project Structure

```
uuid-forge/
├── src/uuid_forge/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── core.py              # Core UUID generation logic
│   ├── config.py            # Configuration management
│   └── cli.py               # Command-line interface
├── tests/                   # Test suite
│   ├── test_core.py         # Core functionality tests
│   ├── test_config.py       # Configuration tests
│   ├── test_cli.py          # CLI tests
│   └── conftest.py          # Test configuration
├── docs/                    # Documentation
├── pyproject.toml           # Project configuration
└── README.md               # Project overview
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Write descriptive docstrings (Google style)
- Keep functions and classes focused and small
- Use meaningful variable and function names

### Example Code Style

```python
def generate_uuid_from_data(
    data: dict[str, Any],
    namespace: str | None = None
) -> str:
    """Generate a deterministic UUID from structured data.

    Args:
        data: Dictionary containing the data to generate UUID from
        namespace: Optional namespace for UUID generation

    Returns:
        Generated UUID as a string

    Raises:
        ValueError: If data is empty or invalid

    Example:
        >>> generate_uuid_from_data({"user": "john@example.com"})
        '550e8400-e29b-41d4-a716-446655440000'
    """
    if not data:
        raise ValueError("Data cannot be empty")

    # Implementation here...
    return uuid_string
```

### Documentation

- Update documentation for new features
- Include examples in docstrings
- Add entries to CHANGELOG.md
- Update README.md if needed

### Testing

All contributions must include tests:

- **Unit tests** for individual functions/methods
- **Integration tests** for feature workflows
- **Property-based tests** for edge cases (using Hypothesis)
- **Performance tests** for optimization claims

Example test structure:

```python
def test_uuid_generation_deterministic():
    """Test that UUID generation is deterministic."""
    generator = UUIDGenerator(namespace="test")

    # Generate UUID multiple times
    uuid1 = generator.generate("test-data")
    uuid2 = generator.generate("test-data")

    # Should be identical
    assert uuid1 == uuid2
    assert isinstance(uuid1, str)
    assert len(uuid1) == 36  # Standard UUID length
```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Minimal example to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, package versions
- **Stack trace**: Full error output if applicable

### Feature Requests

For new features, please provide:

- **Use case**: Why is this feature needed?
- **Proposed API**: How should the feature work?
- **Alternatives**: Other ways to achieve the same goal
- **Breaking changes**: Will this break existing code?

### Pull Requests

Before submitting a pull request:

1. **Fork the repository** and create a feature branch
2. **Write tests** for your changes
3. **Update documentation** as needed
4. **Run all tests** and quality checks
5. **Write a clear commit message**

Pull request checklist:

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or clearly documented)

## Development Workflow

### Branching Strategy

- `main`: Stable release branch
- `develop`: Development integration branch
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical fixes for production

### Commit Messages

Use conventional commit format:

```
type(scope): description

Optional longer description

Closes #issue-number
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/maintenance tasks

Examples:

```
feat(core): add support for custom hash algorithms

fix(cli): handle empty input gracefully

docs(api): update configuration examples
```

## Release Process

### Version Numbers

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Build and publish to PyPI
5. Create GitHub release

## Getting Help

### Community Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Documentation**: Comprehensive guides and API reference

### Development Questions

If you have questions about development:

1. Check existing issues and discussions
2. Read the documentation thoroughly
3. Look at existing code for patterns
4. Ask specific questions with examples

## Recognition

Contributors are recognized in:

- CHANGELOG.md for significant contributions
- README.md contributors section
- GitHub contributors graph
- Release notes for major contributions

## Code of Conduct

Please note that this project follows a Code of Conduct. By participating, you agree to abide by its terms:

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment
- Report unacceptable behavior

Thank you for contributing to UUID-Forge! Your contributions help make deterministic UUID generation better for everyone.
