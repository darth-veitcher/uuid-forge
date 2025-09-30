# UUID-Forge

**Deterministic UUID Generation for Cross-System Coordination**

[![PyPI version](https://badge.fury.io/py/uuid-forge.svg)](https://badge.fury.io/py/uuid-forge)
[![Python versions](https://img.shields.io/pypi/pyversions/uuid-forge.svg)](https://pypi.org/project/uuid-forge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code coverage](https://codecov.io/gh/yourusername/uuid-forge/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/uuid-forge)

UUID-Forge provides a simple, secure way to generate **deterministic UUIDs** that remain consistent across multiple storage systems without requiring inter-service communication or centralized ID generation.

## 🎯 The Problem

When building microservices or distributed systems, you often need the same entity to have the same ID across multiple storage systems:

- **Postgres** (primary database)
- **S3** (document storage)
- **Redis** (caching)
- **QDrant** (vector database)
- **MinIO** (object storage)

Traditional approaches require:
- ❌ Central ID generation service (single point of failure)
- ❌ Database lookups before accessing storage (performance impact)
- ❌ Storing mappings between systems (complexity)
- ❌ Service-to-service communication (latency)

## 💡 The Solution

UUID-Forge generates **deterministic UUIDs** from your business data:

```python
from uuid_forge import generate_uuid_only, IDConfig
import os

config = IDConfig(salt=os.getenv("UUID_FORGE_SALT"))

# Generate UUID from business data
invoice_uuid = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    number=12345
)

# Later, regenerate the EXACT SAME UUID from the same data
# No database lookup needed!
regenerated = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    number=12345
)

assert invoice_uuid == regenerated  # ✓ Always True!
```

**Core Principle**: `Same Input + Same Config = Same UUID, Every Time`

## ✨ Features

- **🔒 Secure**: Uses cryptographic salt to prevent UUID prediction
- **🎯 Deterministic**: Same inputs always produce the same UUID
- **🚀 Zero Coordination**: No service communication required
- **📦 Simple API**: Functional-first with optional OO convenience
- **🔧 Production Ready**: Type-safe, well-tested, documented
- **🎨 CLI Included**: First-class command-line interface
- **🐍 Modern Python**: Requires Python 3.11+

## 📦 Installation

```bash
# With uv (recommended)
uv add uuid-forge

# With pip
pip install uuid-forge

# With all extras
pip install uuid-forge[dev,docs]
```

## 🚀 Quick Start

### 1. Generate a Salt (One Time Setup)

```bash
# Generate a secure salt
uuid-forge new-salt

# Or initialize a config file
uuid-forge init
```

Add the generated salt to your environment:

```bash
export UUID_FORGE_SALT='your-generated-salt-here'
```

### 2. Generate UUIDs

```python
from uuid_forge import generate_uuid_only, load_config_from_env

# Load config from environment
config = load_config_from_env()

# Generate deterministic UUID
user_uuid = generate_uuid_only(
    "user",
    config=config,
    email="alice@example.com"
)
```

### 3. Use Across All Systems

```python
# Postgres - UUID as primary key
db.execute(
    "INSERT INTO users (id, email) VALUES (%s, %s)",
    (user_uuid, "alice@example.com")
)

# S3 - UUID in object key
s3.put_object(
    Bucket="users",
    Key=f"profiles/{user_uuid}.json",
    Body=profile_data
)

# Redis - UUID in cache key
redis.set(f"user:{user_uuid}", user_data, ex=3600)

# Later, regenerate UUID from business data - no lookup needed!
uuid_from_data = generate_uuid_only(
    "user",
    config=config,
    email="alice@example.com"
)

# All systems now accessible with the same UUID
```

## 📋 Use Cases

### ✅ Perfect For:

- **Microservices Architecture**: Multiple services need consistent IDs
- **Multi-Storage Systems**: Postgres + S3 + Redis + QDrant + MinIO
- **Zero-Coordination Design**: No central ID service required
- **Deterministic Testing**: Reproducible IDs for test scenarios
- **Data Migration**: Consistent IDs across old and new systems

### ❌ Not Ideal For:

- **Simple CRUD Apps**: Use database auto-increment
- **Sequential IDs Required**: Use database sequences
- **No Salt Available**: UUIDs become predictable (security risk)

## 🔒 Security

**CRITICAL**: Always use a salt in production!

```python
# ❌ INSECURE - UUIDs are predictable
config = IDConfig()

# ✅ SECURE - UUIDs are unpredictable
config = IDConfig(salt=os.getenv("UUID_FORGE_SALT"))
```

Generate a secure salt:

```bash
uuid-forge new-salt
```

Store it securely:
- Environment variables
- Secret management systems (AWS Secrets Manager, HashiCorp Vault, etc.)
- **Never commit to version control**

## 📖 Documentation

Full documentation is available at: [https://yourusername.github.io/uuid-forge](https://yourusername.github.io/uuid-forge)

- [Installation Guide](https://yourusername.github.io/uuid-forge/installation/)
- [Quick Start Tutorial](https://yourusername.github.io/uuid-forge/quickstart/)
- [API Reference](https://yourusername.github.io/uuid-forge/api/)
- [Best Practices](https://yourusername.github.io/uuid-forge/best-practices/)
- [Migration Guide](https://yourusername.github.io/uuid-forge/migration/)

## 🛠️ CLI Usage

UUID-Forge includes a comprehensive CLI:

```bash
# Generate UUID
uuid-forge generate invoice --attr region=EUR --attr number=12345

# With human-readable prefix
uuid-forge generate invoice --prefix INV-EUR --attr region=EUR --attr number=12345

# Extract UUID from prefixed ID
uuid-forge extract "INV-EUR-550e8400-e29b-41d4-a716-446655440000"

# Generate new salt
uuid-forge new-salt

# Initialize config file
uuid-forge init

# Validate configuration
uuid-forge validate

# Show current config
uuid-forge info
```

## 🏗️ Architecture

UUID-Forge uses **UUIDv5** (name-based, SHA-1) for deterministic generation:

1. **Entity Type** provides logical separation ("invoice", "user", "order")
2. **Business Data** uniquely identifies the entity (region, number, email, etc.)
3. **Salt** adds security (prevents UUID prediction)
4. **Namespace** provides additional isolation (optional)

The combination is hashed to produce a UUID that's:
- ✅ Deterministic (same inputs → same UUID)
- ✅ Unique (different inputs → different UUIDs)
- ✅ Secure (unpredictable with salt)
- ✅ Standard (RFC 4122 compliant)

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/yourusername/uuid-forge.git
cd uuid-forge

# Install with uv
uv sync --all-extras

# Run tests
pytest

# Run tests with coverage
pytest --cov=uuid_forge --cov-report=html

# Run linting
ruff check src tests
mypy src

# Run all checks with nox
nox

# Build documentation
cd docs
mkdocs serve
```

## 📊 Project Stats

- **Lines of Code**: ~300 (core), ~1000 (with tests)
- **Test Coverage**: >80%
- **Type Coverage**: 100%
- **Dependencies**: Minimal (typer, rich for CLI)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure tests pass and coverage remains >80%
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by the need for zero-coordination microservices
- Built with modern Python best practices
- Follows PEP-8, uses strict typing, and comprehensive testing

## 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/uuid-forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/uuid-forge/discussions)
- **Email**: your.email@example.com

---

**Made with ❤️ for developers who value simplicity and determinism**
