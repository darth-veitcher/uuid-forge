# CLI API Reference

Complete API reference for UUID-Forge command-line interface.

## Overview

The UUID-Forge CLI provides command-line access to all core functionality including UUID generation, configuration management, and security validation.

## CLI Module Reference

::: uuid_forge.cli
    options:
      show_root_heading: true
      show_source: false
      heading_level: 2
      members:
        - app
        - generate
        - extract
        - new_salt
        - init
        - validate
        - info
        - docs
        - test

## Commands

### generate

Generate a deterministic UUID for an entity.

**Signature:**
```python
def generate(
    entity_type: str,
    prefix: str | None = None,
    separator: str = "-",
    namespace: str | None = None,
    salt: str | None = None,
    use_env: bool = True,
    attributes: list[str] | None = None,
) -> None
```

**Arguments:**
- `entity_type` - Type of entity (e.g., 'invoice', 'order', 'user') **[required]**

**Options:**
- `--prefix, -p` - Human-readable prefix for the UUID
- `--separator, -s` - Separator between prefix and UUID (default: -)
- `--namespace, -n` - Custom namespace domain
- `--salt` - Cryptographic salt
- `--env/--no-env` - Load configuration from environment variables (default: True)
- `--attr, -a` - Attributes in key=value format (repeatable)

**Example:**
```bash
uuid-forge generate invoice --attr region=EUR --attr number=12345
```

### extract

Extract the UUID portion from a prefixed identifier.

**Signature:**
```python
def extract(
    prefixed_id: str
) -> None
```

**Arguments:**
- `prefixed_id` - Prefixed identifier (e.g., "INV-EUR-550e8400-...") **[required]**

**Example:**
```bash
uuid-forge extract "INV-EUR-550e8400-e29b-41d4-a716-446655440000"
```

### new-salt

Generate a new cryptographically secure salt.

**Signature:**
```python
def new_salt() -> None
```

**Example:**
```bash
uuid-forge new-salt
```

### init

Initialize a new configuration file with generated salt.

**Signature:**
```python
def init(
    file: str | None = None,
    force: bool = False
) -> None
```

**Options:**
- `--file, -f` - Configuration file path (default: .env)
- `--force` - Overwrite existing file

**Example:**
```bash
uuid-forge init --file .env.production
```

### validate

Validate current configuration for security best practices.

**Signature:**
```python
def validate() -> None
```

**Example:**
```bash
uuid-forge validate
```

### info

Display information about current configuration and usage.

**Signature:**
```python
def info() -> None
```

**Example:**
```bash
uuid-forge info
```

### docs

Build or serve the documentation locally.

**Signature:**
```python
def docs(
    command: str = "serve"
) -> None
```

**Arguments:**
- `command` - Either 'serve' or 'build' (default: serve)

**Example:**
```bash
uuid-forge docs serve
uuid-forge docs build
```

### test

Run the test suite with pytest.

**Signature:**
```python
def test(
    args: list[str] | None = None
) -> None
```

**Arguments:**
- `args` - Additional pytest arguments (optional)

**Example:**
```bash
uuid-forge test
uuid-forge test --cov
```

## Environment Variables

The CLI respects the following environment variables:

| Variable | Type | Description |
|----------|------|-------------|
| `UUID_FORGE_SALT` | str | Cryptographic salt for UUID generation |
| `UUID_FORGE_NAMESPACE` | str | Default namespace domain |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (invalid input, missing configuration, etc.) |
| 2 | Validation failure |

## Integration with Python API

The CLI is built on top of the core Python API. All functionality available via CLI is also available programmatically:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid_forge.core import generate_salt, generate_uuid_with_prefix
from uuid_forge.config import init_config_file, validate_config_security

# Generate salt (equivalent to: uuid-forge new-salt)
salt = generate_salt()

# Generate UUID (equivalent to: uuid-forge generate)
config = IDConfig(namespace=Namespace("myapp.com"), salt=salt)
generator = UUIDGenerator(config)
uuid = generator.generate("user", email="alice@example.com")

# With prefix (equivalent to: uuid-forge generate --prefix)
prefixed = generate_uuid_with_prefix(
    entity_type="invoice",
    prefix="INV-EUR",
    namespace=Namespace("myapp.com"),
    salt=salt,
    region="EUR",
    number=12345
)
```

## See Also

- [CLI User Guide](../guide/cli.md) - Practical CLI usage examples
- [Configuration Guide](../getting-started/configuration.md) - Environment setup
- [Core API Reference](core.md) - Python API documentation
