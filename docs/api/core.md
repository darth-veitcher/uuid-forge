# Core API Reference

This page documents the core UUID generation functionality provided by `uuid_forge.core`.

## Overview

The core module provides three main approaches to generating deterministic UUIDs:

1. **Functional API** (recommended): Pure functions for UUID generation
2. **Object-Oriented API**: Class-based wrapper for convenience
3. **Utility Functions**: Helper functions for salt generation and UUID extraction

## Configuration

::: uuid_forge.core.IDConfig
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Primary Functions

### generate_uuid_only

::: uuid_forge.core.generate_uuid_only
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### generate_uuid_with_prefix

::: uuid_forge.core.generate_uuid_with_prefix
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### extract_uuid_from_prefixed

::: uuid_forge.core.extract_uuid_from_prefixed
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Utility Functions

### generate_salt

::: uuid_forge.core.generate_salt
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Object-Oriented API

### UUIDGenerator

::: uuid_forge.core.UUIDGenerator
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - __init__
        - generate
        - generate_with_prefix

## Protocols

### Representable

::: uuid_forge.core.Representable
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Usage Examples

### Basic UUID Generation

```python
from uuid_forge.core import generate_uuid_only, IDConfig

# Create configuration
config = IDConfig(salt="production-secret-salt")

# Generate UUID
user_uuid = generate_uuid_only(
    "user",
    config=config,
    email="alice@example.com"
)

print(user_uuid)  # UUID object
```

### With Human-Readable Prefix

```python
from uuid_forge.core import generate_uuid_with_prefix

# Generate prefixed ID
invoice_id = generate_uuid_with_prefix(
    "invoice",
    prefix="INV-EUR",
    config=config,
    region="EUR",
    number=12345
)

print(invoice_id)  # "INV-EUR-550e8400-e29b-41d4-a716-446655440000"
```

### Using the OO API

```python
from uuid_forge.core import UUIDGenerator, IDConfig

# Create generator with configuration
generator = UUIDGenerator(
    config=IDConfig(salt="production-secret-salt")
)

# Generate multiple UUIDs with same config
order_uuid = generator.generate("order", order_number=123)
invoice_uuid = generator.generate("invoice", order_id=str(order_uuid))
```

### Extracting UUIDs

```python
from uuid_forge.core import extract_uuid_from_prefixed

# Extract UUID from prefixed string
prefixed = "INV-EUR-550e8400-e29b-41d4-a716-446655440000"
uuid = extract_uuid_from_prefixed(prefixed)

print(uuid)  # UUID('550e8400-e29b-41d4-a716-446655440000')
```

## Type Information

All functions in the core module are fully typed. Import types for type hints:

```python
from uuid import UUID
from uuid_forge.core import IDConfig, Representable
from typing import Optional

def process_entity(
    entity_type: str,
    config: Optional[IDConfig] = None,
    **kwargs: Any
) -> UUID:
    return generate_uuid_only(entity_type, config=config, **kwargs)
```

## Thread Safety

All functions in the core module are thread-safe. They have no shared mutable state and can be called concurrently from multiple threads.

## Performance Considerations

- UUID generation is **fast**: ~10 microseconds per call
- No I/O operations are performed
- Memory usage is minimal (< 1KB per call)
- Consider caching UUIDs if generating millions per second

## Security Notes

!!! warning "Always Use a Salt in Production"
    Without a salt, UUIDs are predictable and may pose a security risk. Always configure a cryptographic salt using `generate_salt()`.

!!! danger "Keep Your Salt Secret"
    The salt is effectively a secret key. Anyone with your salt can predict your UUIDs. Store it securely:

    - Environment variables
    - Secret management systems (AWS Secrets Manager, Vault, etc.)
    - **Never commit to version control**

## See Also

- [Configuration API](config.md) - Loading configuration from environment
- [CLI Reference](../guide/cli.md) - Command-line interface
- [Best Practices](../guide/best-practices.md) - Production guidelines
