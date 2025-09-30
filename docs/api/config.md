# Config API Reference

Complete reference for UUID-Forge configuration system.

## Configuration Management

The configuration system in UUID-Forge provides utilities for loading and managing UUID generation settings.

## Configuration Methods

### Load Configuration

Load configuration from various sources:

```python
from uuid_forge.config import load_config_from_env
from uuid_forge.core import IDConfig

# Load from environment variables
config = load_config_from_env()

# Create configuration directly
config = IDConfig(namespace="my-app", salt="custom-salt")
```

### Validation

Configuration is automatically validated:

```python
# Valid configuration
config = IDConfig(
    namespace="my-app",
    salt="custom-salt"
)

# Invalid configuration raises ValueError
try:
    config = IDConfig(namespace="invalid-uuid-string")  # Invalid namespace
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Configuration Options

### Core Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `namespace` | `str` or `UUID` | `None` | Default namespace for UUID generation |
| `version` | `int` | `5` | UUID version (3, 4, or 5) |
| `format` | `str` | `"hex"` | Output format (`hex`, `urn`, `bytes`) |
| `case` | `str` | `"lower"` | Case for hex output (`upper`, `lower`) |
| `separator` | `str` | `"-"` | Separator character for hex format |

### Advanced Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `seed` | `int` | `None` | Random seed for reproducible generation |
| `clock_seq` | `int` | `None` | Clock sequence for version 1 UUIDs |
| `node` | `int` | `None` | Node ID for version 1 UUIDs |
| `json_encoder` | `JSONEncoder` | `None` | Custom JSON encoder for object serialization |

## Configuration File Format

### YAML Configuration

```yaml
# uuid_forge.yaml
namespace: "my-application"
version: 5
format: "hex"
case: "lower"
separator: "-"

# Custom namespaces
namespaces:
  users: "550e8400-e29b-41d4-a716-446655440000"
  orders: "550e8400-e29b-41d4-a716-446655440001"
  products: "550e8400-e29b-41d4-a716-446655440002"

# Environment-specific settings
environments:
  development:
    namespace: "dev-app"
    seed: 12345
  production:
    namespace: "prod-app"
    seed: null
```

### JSON Configuration

```json
{
  "namespace": "my-application",
  "version": 5,
  "format": "hex",
  "case": "lower",
  "separator": "-",
  "namespaces": {
    "users": "550e8400-e29b-41d4-a716-446655440000",
    "orders": "550e8400-e29b-41d4-a716-446655440001"
  }
}
```

## Environment Variables

Configuration via environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `UUID_FORGE_NAMESPACE` | Default namespace | `my-app` |
| `UUID_FORGE_VERSION` | UUID version | `5` |
| `UUID_FORGE_FORMAT` | Output format | `hex` |
| `UUID_FORGE_CASE` | Case for hex output | `lower` |
| `UUID_FORGE_SEPARATOR` | Separator character | `-` |
| `UUID_FORGE_CONFIG_FILE` | Configuration file path | `/path/to/config.yaml` |

## Examples

### Basic Configuration

```python
from uuid_forge import Config, UUIDForge

# Simple configuration
config = Config(
    namespace="my-app",
    version=5
)

forge = UUIDForge(config)
uuid_result = forge.generate("test")
```

### Advanced Configuration

```python
import json
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

config = Config(
    namespace="advanced-app",
    version=5,
    format="hex",
    case="upper",
    separator="",
    json_encoder=CustomJSONEncoder
)

forge = UUIDForge(config)
```

### Environment-Specific Configuration

```python
import os

def create_config():
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return Config(
            namespace="prod-app",
            version=5,
            format="hex"
        )
    else:
        return Config(
            namespace="dev-app",
            version=5,
            format="hex",
            seed=12345  # Consistent for testing
        )

config = create_config()
forge = UUIDForge(config)
```

### Configuration Inheritance

```python
# Base configuration
base_config = Config(
    version=5,
    format="hex",
    case="lower"
)

# Service-specific configurations
user_config = Config(
    namespace="users",
    **base_config.to_dict()
)

order_config = Config(
    namespace="orders",
    **base_config.to_dict()
)
```

## Validation Rules

### Namespace Validation

- Must be a valid UUID string or UUID object
- Empty string is converted to `None`
- Invalid UUID strings raise `ValueError`

### Version Validation

- Must be 3, 4, or 5
- Other values raise `ValueError`

### Format Validation

- Must be one of: `"hex"`, `"urn"`, `"bytes"`
- Case-insensitive matching
- Invalid formats raise `ValueError`

### Case Validation

- Must be one of: `"upper"`, `"lower"`
- Case-insensitive matching
- Invalid cases raise `ValueError`

## Configuration Precedence

Configuration is loaded in order of precedence:

1. **Explicit parameters** - Passed to `Config()` constructor
2. **Configuration file** - Loaded from file path
3. **Environment variables** - System environment
4. **Default values** - Built-in defaults

## Error Handling

```python
from uuid_forge.config import Config, ConfigError

try:
    config = Config.load_from_file("invalid_config.yaml")
except ConfigError as e:
    print(f"Configuration error: {e}")
except FileNotFoundError:
    print("Configuration file not found")
```

## Migration and Compatibility

### Version Migration

```python
def migrate_config_v1_to_v2(old_config_dict):
    """Migrate configuration from v1 to v2 format"""
    new_config = {}

    # Map old keys to new keys
    key_mapping = {
        "uuid_namespace": "namespace",
        "uuid_version": "version",
        "output_format": "format"
    }

    for old_key, new_key in key_mapping.items():
        if old_key in old_config_dict:
            new_config[new_key] = old_config_dict[old_key]

    return Config(**new_config)
```

### Backward Compatibility

UUID-Forge maintains backward compatibility for configuration:

```python
# Old style (still supported)
config = Config(
    uuid_namespace="my-app",  # Deprecated
    uuid_version=5           # Deprecated
)

# New style (recommended)
config = Config(
    namespace="my-app",
    version=5
)
```

## Testing Configuration

```python
import pytest
from uuid_forge.config import Config

def test_config_validation():
    """Test configuration validation"""
    # Valid configuration
    config = Config(namespace="test", version=5)
    assert config.namespace == "test"
    assert config.version == 5

    # Invalid version
    with pytest.raises(ValueError):
        Config(version=99)

    # Invalid format
    with pytest.raises(ValueError):
        Config(format="invalid")

def test_config_loading():
    """Test configuration loading from various sources"""
    # From dict
    config_dict = {"namespace": "test", "version": 5}
    config = Config(**config_dict)

    # From environment (mock)
    import os
    os.environ["UUID_FORGE_NAMESPACE"] = "env-test"
    config = Config.load_from_env()
    assert config.namespace == "env-test"
```
