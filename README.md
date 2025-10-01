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

### 2. Choose Your API Style

UUID-Forge offers both **functional** and **object-oriented** approaches:

#### Functional API (Recommended for Simple Cases)

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

#### Object-Oriented API (Great for Services)

```python
from uuid_forge import UUIDGenerator, IDConfig
import os

# Create a generator with your configuration
generator = UUIDGenerator(
    config=IDConfig(salt=os.getenv("UUID_FORGE_SALT"))
)

# Generate multiple UUIDs with same config (no repetitive config passing)
user_uuid = generator.generate("user", email="alice@example.com")
invoice_uuid = generator.generate("invoice", number=12345, region="EUR")
order_uuid = generator.generate("order", user_id=str(user_uuid), total=99.99)

# Generate with human-readable prefixes
prefixed_id = generator.generate_with_prefix(
    "user",
    prefix="USER",
    email="alice@example.com"
)
# Result: "USER-550e8400-e29b-41d4-a716-446655440000"

# Perfect for service classes - encapsulates configuration
class InvoiceService:
    def __init__(self, salt: str):
        self.uuid_gen = UUIDGenerator(config=IDConfig(salt=salt))

    def create_invoice_id(self, region: str, number: int) -> str:
        return self.uuid_gen.generate_with_prefix(
            "invoice",
            prefix=f"INV-{region}",
            region=region,
            number=number
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

## 🏛️ Advanced Usage Patterns

### Repository Pattern with UUID Generation

```python
from uuid_forge import UUIDGenerator, IDConfig, UUID, Namespace
from typing import Protocol
import os

class EntityRepository(Protocol):
    def generate_id(self, **kwargs) -> UUID: ...

class InvoiceRepository:
    def __init__(self):
        self.uuid_generator = UUIDGenerator(
            config=IDConfig(
                namespace=Namespace("invoices.mycompany.com"),
                salt=os.getenv("UUID_FORGE_SALT")
            )
        )

    def generate_id(self, region: str, number: int) -> UUID:
        return self.uuid_generator.generate("invoice", region=region, number=number)

    def generate_prefixed_id(self, region: str, number: int) -> str:
        return self.uuid_generator.generate_with_prefix(
            "invoice",
            prefix=f"INV-{region}",
            region=region,
            number=number
        )
```

### Factory Pattern for Multi-Entity Systems

```python
from uuid_forge import UUIDGenerator, IDConfig, UUID
from enum import Enum

class EntityType(Enum):
    USER = "user"
    ORDER = "order"
    PRODUCT = "product"
    INVOICE = "invoice"

class UUIDFactory:
    def __init__(self, config: IDConfig):
        self.generators = {
            EntityType.USER: UUIDGenerator(config),
            EntityType.ORDER: UUIDGenerator(config),
            EntityType.PRODUCT: UUIDGenerator(config),
            EntityType.INVOICE: UUIDGenerator(config),
        }

    def create_uuid(self, entity_type: EntityType, **attributes) -> UUID:
        return self.generators[entity_type].generate(entity_type.value, **attributes)

    def create_prefixed_uuid(self, entity_type: EntityType, **attributes) -> str:
        prefix_map = {
            EntityType.USER: "USR",
            EntityType.ORDER: "ORD",
            EntityType.PRODUCT: "PRD",
            EntityType.INVOICE: "INV",
        }
        return self.generators[entity_type].generate_with_prefix(
            entity_type.value,
            prefix=prefix_map[entity_type],
            **attributes
        )

# Usage
factory = UUIDFactory(config=load_config_from_env())
user_uuid = factory.create_uuid(EntityType.USER, email="alice@example.com")
order_id = factory.create_prefixed_uuid(EntityType.ORDER, user_id=user_uuid, items=["A", "B"])
```

### Dependency Injection with UUID Services

```python
from abc import ABC, abstractmethod
from uuid_forge import UUIDGenerator, IDConfig, UUID

class UUIDService(ABC):
    @abstractmethod
    def generate_user_uuid(self, email: str) -> UUID: ...

    @abstractmethod
    def generate_order_uuid(self, user_id: UUID, timestamp: int) -> UUID: ...

class ProductionUUIDService(UUIDService):
    def __init__(self, config: IDConfig):
        self.generator = UUIDGenerator(config)

    def generate_user_uuid(self, email: str) -> UUID:
        return self.generator.generate("user", email=email)

    def generate_order_uuid(self, user_id: UUID, timestamp: int) -> UUID:
        return self.generator.generate("order", user_id=str(user_id), timestamp=timestamp)

class TestUUIDService(UUIDService):
    def __init__(self):
        # Use deterministic config for testing
        self.generator = UUIDGenerator(
            config=IDConfig(salt="test-salt-for-reproducible-tests")
        )

    def generate_user_uuid(self, email: str) -> UUID:
        return self.generator.generate("user", email=email)

    def generate_order_uuid(self, user_id: UUID, timestamp: int) -> UUID:
        return self.generator.generate("order", user_id=str(user_id), timestamp=timestamp)
```

## 📋 Use Cases

### ✅ Perfect For:

- **Microservices Architecture**: Multiple services need consistent IDs
- **Multi-Storage Systems**: Postgres + S3 + Redis + QDrant + MinIO
- **Zero-Coordination Design**: No central ID service required
- **Deterministic Testing**: Reproducible IDs for test scenarios
- **Data Migration**: Consistent IDs across old and new systems
- **Service-Oriented Architecture**: Clean dependency injection patterns
- **Multi-Tenant Applications**: Isolated UUID namespaces per tenant

### ❌ Not Ideal For:

- **Simple CRUD Apps**: Use database auto-increment
- **Sequential IDs Required**: Use database sequences
- **No Salt Available**: UUIDs become predictable (security risk)
- **High-Performance Scenarios**: UUID generation has computational overhead

## ⚙️ Configuration Options

UUID-Forge provides flexible configuration through the `IDConfig` class:

### Basic Configuration

```python
from uuid_forge import IDConfig, Namespace
import os

# Default configuration (no salt - not recommended for production)
config = IDConfig()

# Production configuration with salt
config = IDConfig(salt=os.getenv("UUID_FORGE_SALT"))

# Custom namespace for your organization
config = IDConfig(
    namespace=Namespace("mycompany.com"),
    salt=os.getenv("UUID_FORGE_SALT")
)
```

### Environment-Based Configuration

```python
from uuid_forge import load_config_from_env

# Load from default environment variables
config = load_config_from_env()
# Reads: UUID_FORGE_NAMESPACE and UUID_FORGE_SALT

# Load from custom environment variables
config = load_config_from_env(
    namespace_env="MY_UUID_NAMESPACE",
    salt_env="MY_UUID_SALT"
)
```

### Configuration Hierarchy

1. **Namespace**: Provides logical separation between applications

   - Default: `uuid.NAMESPACE_DNS`
   - Custom: `Namespace("your-domain.com")`
   - From env: Set `UUID_FORGE_NAMESPACE=your-domain.com`

2. **Salt**: Adds cryptographic security to prevent UUID prediction
   - Default: `""` (empty - **not secure for production**)
   - Generated: Use `uuid-forge new-salt` command
   - From env: Set `UUID_FORGE_SALT=your-generated-salt`

### Configuration Patterns

#### Service-Based Configuration

```python
from uuid_forge import UUIDGenerator, IDConfig, UUID, Namespace
import os

class UserService:
    def __init__(self):
        self.uuid_generator = UUIDGenerator(
            config=IDConfig(
                namespace=Namespace("users.mycompany.com"),
                salt=os.getenv("UUID_FORGE_SALT")
            )
        )

    def create_user_uuid(self, email: str) -> UUID:
        return self.uuid_generator.generate("user", email=email)
```

#### Multi-Tenant Configuration

```python
from uuid_forge import UUIDGenerator, IDConfig, UUID, Namespace
import os

class TenantUUIDService:
    def __init__(self, tenant_id: str):
        self.generator = UUIDGenerator(
            config=IDConfig(
                namespace=Namespace(f"tenant-{tenant_id}.mycompany.com"),
                salt=os.getenv("UUID_FORGE_SALT")
            )
        )

    def generate_entity_uuid(self, entity_type: str, **kwargs) -> UUID:
        return self.generator.generate(entity_type, **kwargs)
```

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

Full documentation is available at: [https://darth-veitcher.github.io/uuid-forge](https://darth-veitcher.github.io/uuid-forge)

- [API Reference](https://darth-veitcher.github.io/uuid-forge/api/core/)
- [Getting Started Guide](https://darth-veitcher.github.io/uuid-forge/gettting-started/quickstart/)
- [Configuration Options](https://darth-veitcher.github.io/uuid-forge/api/core/#configuration)
- [Best Practices](https://darth-veitcher.github.io/uuid-forge/api/core/#security)
- [CLI Reference](https://darth-veitcher.github.io/uuid-forge/api/core/#cli-usage)

## � API Reference

### Functional API

```python
from uuid_forge import generate_uuid_only, generate_uuid_with_prefix, extract_uuid_from_prefixed

# Generate UUID
uuid_obj = generate_uuid_only("user", config=config, email="alice@example.com")

# Generate with prefix
prefixed_id = generate_uuid_with_prefix("user", config=config, prefix="USR", email="alice@example.com")

# Extract UUID from prefixed ID
uuid_obj = extract_uuid_from_prefixed("USR-550e8400-e29b-41d4-a716-446655440000")
```

### Object-Oriented API

```python
from uuid_forge import UUIDGenerator, IDConfig

# Create generator
generator = UUIDGenerator(config=IDConfig(salt="your-salt"))

# Generate UUIDs
uuid_obj = generator.generate("user", email="alice@example.com")
prefixed_id = generator.generate_with_prefix("user", prefix="USR", email="alice@example.com")
```

### Configuration API

```python
from uuid_forge import IDConfig, load_config_from_env, generate_salt

# Create configurations
config = IDConfig(salt="your-salt")
config = load_config_from_env()

# Generate secure salt
salt = generate_salt()  # 32 bytes by default
salt = generate_salt(64)  # Custom length
```

## �🛠️ CLI Usage

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
git clone https://github.com/darth-veitcher/uuid-forge.git
cd uuid-forge

# Install with uv (includes all dev dependencies)
uv sync --all-groups

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=uuid_forge --cov-report=html

# Run linting and formatting
uv run ruff check src tests
uv run ruff format src tests
uv run mypy src

# Run all checks with nox
uv run nox

# Build the package
uv build

# Build and serve documentation
uv run mkdocs serve
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
- Built with modern Python best practices using `uv` and `hatch-vcs`
- Follows PEP-8, uses strict typing, and comprehensive testing

## 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/darth-veitcher/uuid-forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/darth-veitcher/uuid-forge/discussions)
- **Repository**: [https://github.com/darth-veitcher/uuid-forge](https://github.com/darth-veitcher/uuid-forge)

---

**Made with ❤️ for developers who value simplicity and determinism**
