# Configuration

UUID-Forge provides flexible configuration options to suit different use cases and environments.

## Configuration File

UUID-Forge looks for configuration in the following locations (in order of precedence):

1. `uuid_forge.yaml` in the current directory
2. `~/.uuid_forge.yaml` in the user's home directory
3. `/etc/uuid_forge.yaml` system-wide configuration

## Configuration Format

```yaml
# uuid_forge.yaml
namespace: "my-application"
version: 1
format: "hex"
case: "lower"
separator: "-"

# Custom namespaces for different contexts
namespaces:
  users: "550e8400-e29b-41d4-a716-446655440000"
  orders: "550e8400-e29b-41d4-a716-446655440001"
  products: "550e8400-e29b-41d4-a716-446655440002"
```

## Configuration Options

### Core Settings

- `namespace`: Default namespace UUID (string or UUID)
- `version`: UUID version to generate (1, 3, 4, or 5)
- `format`: Output format (`hex`, `urn`, `bytes`)
- `case`: Case for hex output (`upper`, `lower`)
- `separator`: Separator character for hex format

### Advanced Settings

- `seed`: Random seed for reproducible generation
- `clock_seq`: Clock sequence for version 1 UUIDs
- `node`: Node ID for version 1 UUIDs

## Environment Variables

Configuration can also be set via environment variables:

```bash
export UUID_FORGE_NAMESPACE="my-app"
export UUID_FORGE_VERSION=5
export UUID_FORGE_FORMAT="hex"
```

## Programmatic Configuration

```python
from uuid_forge import UUIDGenerator, IDConfig

# Create configuration
config = IDConfig(
    namespace="my-application",
    version=5,
    format="hex",
    case="lower"
)

# Initialize with configuration
forge = UUIDGenerator(config)

# Or use default configuration
forge = UUIDGenerator()
```

## Configuration Validation

UUID-Forge validates all configuration values and provides helpful error messages for invalid settings.

## Next Steps

- [Core Concepts](../guide/concepts.md) - Understand UUID generation principles
- [Basic Usage](../guide/basic-usage.md) - Start generating UUIDs
