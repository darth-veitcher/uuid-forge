# UUID-Forge Documentation

**Deterministic UUID Generation for Cross-System Coordination**

Welcome to the UUID-Forge documentation! This library provides a simple, secure way to generate deterministic UUIDs that remain consistent across multiple storage systems without requiring inter-service communication or centralized ID generation.

## What is UUID-Forge?

UUID-Forge solves a common problem in microservices and distributed systems: **How do you maintain consistent entity identifiers across multiple storage systems?**

```python
from uuid_forge import generate_uuid_only, IDConfig
import os

# Configure once
config = IDConfig(salt=os.getenv("UUID_FORGE_SALT"))

# Generate UUID from business data
invoice_uuid = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    number=12345
)

# Later, regenerate the exact same UUID - no database needed!
regenerated = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    number=12345
)

assert invoice_uuid == regenerated  # Always True!
```

## Core Principle

**Same Input + Same Config = Same UUID, Every Time**

This enables:

- ✅ **Zero coordination** between services
- ✅ **Direct access** to any storage system
- ✅ **No lookups** required
- ✅ **Deterministic testing**
- ✅ **Simple architecture**

## Quick Links

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quick Start__

    ---

    Get up and running in minutes with our step-by-step guide.

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-book-open-variant:{ .lg .middle } __User Guide__

    ---

    Learn core concepts and best practices for production use.

    [:octicons-arrow-right-24: User Guide](guide/concepts.md)

-   :material-application-brackets:{ .lg .middle } __API Reference__

    ---

    Complete API documentation with examples and type signatures.

    [:octicons-arrow-right-24: API Reference](api/core.md)

-   :material-code-braces:{ .lg .middle } __CLI Reference__

    ---

    Command-line interface for generating UUIDs and managing config.

    [:octicons-arrow-right-24: CLI Reference](guide/cli.md)

</div>

## Use Cases

### Microservices Architecture

Generate consistent IDs across multiple services without coordination:

```python
# Order Service
order_uuid = generate_uuid_only("order", config=config, order_number=12345)

# Invoice Service (different codebase, same UUID!)
invoice_order_uuid = generate_uuid_only("order", config=config, order_number=12345)

assert order_uuid == invoice_order_uuid
```

### Multi-Storage Systems

Use the same UUID across all your storage layers:

```python
# Postgres
db.execute("INSERT INTO invoices (id, ...) VALUES (%s, ...)", invoice_uuid)

# S3
s3.put_object(Key=f"invoices/{invoice_uuid}.pdf", ...)

# Redis
redis.set(f"invoice:{invoice_uuid}", ...)

# All accessible with the same UUID!
```

### Deterministic Testing

Reproduce exact UUIDs in tests for reliable assertions:

```python
def test_invoice_processing():
    test_config = IDConfig(salt="test-salt")

    # Known UUID for assertions
    expected_uuid = generate_uuid_only(
        "invoice",
        config=test_config,
        region="EUR",
        number=12345
    )

    # Test your code
    result = process_invoice(region="EUR", number=12345)

    assert result.id == expected_uuid
```

## Why UUID-Forge?

Traditional approaches to cross-system ID coordination have significant drawbacks:

| Approach | Problems |
|----------|----------|
| **Central ID Service** | Single point of failure, latency, complexity |
| **Database Lookups** | Performance impact, requires database access |
| **ID Mappings** | Additional storage, synchronization challenges |
| **Random UUIDs** | No reproducibility, requires storage everywhere |

UUID-Forge eliminates all of these problems with deterministic generation.

## Key Features

- **🔒 Secure**: Cryptographic salt prevents UUID prediction
- **🎯 Deterministic**: Identical inputs always produce identical UUIDs
- **🚀 Zero Coordination**: No inter-service communication needed
- **📦 Simple API**: Functional-first with optional OO wrapper
- **🔧 Production Ready**: Type-safe, tested, documented
- **🎨 CLI Included**: First-class command-line interface
- **🐍 Modern Python**: Requires Python 3.11+

## Installation

```bash
# With uv (recommended)
uv add uuid-forge

# With pip
pip install uuid-forge
```

[Learn more →](getting-started/installation.md){ .md-button .md-button--primary }

## Next Steps

1. [Install UUID-Forge](getting-started/installation.md)
2. [Follow the Quick Start guide](getting-started/quickstart.md)
3. [Learn core concepts](guide/concepts.md)
4. [Explore use cases](use-cases/microservices.md)

## Community and Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/uuid-forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/uuid-forge/discussions)
- **Contributing**: [Contributing Guide](development/contributing.md)

## License

UUID-Forge is released under the MIT License. See [License](about/license.md) for details.
