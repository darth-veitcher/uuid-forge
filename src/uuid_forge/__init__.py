"""UUID-Forge: Deterministic UUID Generation for Cross-System Coordination.

UUID-Forge provides a simple, secure way to generate deterministic UUIDs that
remain consistent across multiple storage systems (Postgres, S3, Redis, QDrant,
MinIO, etc.) without requiring inter-service communication or centralized ID
generation.

Core Principles:
- Same input + Same config = Same UUID, every time
- Security via cryptographic salt
- Zero coordination between services
- Simple functional API with optional OO convenience

Basic Usage:
    ```python
    from uuid_forge import generate_uuid_only, IDConfig
    import os

    # Configure with salt from environment
    config = IDConfig(salt=os.getenv("UUID_FORGE_SALT", ""))

    # Generate deterministic UUID
    invoice_uuid = generate_uuid_only(
        "invoice",
        config=config,
        region="EUR",
        number=12345
    )

    # Later, regenerate the exact same UUID from business data
    regenerated = generate_uuid_only(
        "invoice",
        config=config,
        region="EUR",
        number=12345
    )

    assert invoice_uuid == regenerated  # Always True!
    ```

With Prefixes:
    ```python
    from uuid_forge import generate_uuid_with_prefix, extract_uuid_from_prefixed

    # Generate with human-readable prefix
    prefixed_id = generate_uuid_with_prefix(
        "invoice",
        prefix="INV-EUR",
        config=config,
        region="EUR",
        number=12345
    )
    # Result: "INV-EUR-550e8400-e29b-41d4-a716-446655440000"

    # Extract UUID when needed
    uuid = extract_uuid_from_prefixed(prefixed_id)
    ```

Configuration from Environment:
    ```python
    from uuid_forge.config import load_config_from_env

    # Automatically loads UUID_FORGE_SALT and UUID_FORGE_NAMESPACE
    config = load_config_from_env()
    ```

See https://github.com/yourusername/uuid-forge for full documentation.
"""

from uuid_forge.config import (
    get_default_config,
    init_config_file,
    load_config_from_env,
    validate_config_security,
)
from uuid_forge.core import (
    IDConfig,
    Representable,
    UUIDGenerator,
    extract_uuid_from_prefixed,
    generate_salt,
    generate_uuid_only,
    generate_uuid_with_prefix,
)

# Version handling with graceful fallback
try:
    from uuid_forge._version import __version__
except ImportError:
    # Fallback version when _version.py doesn't exist or import fails
    __version__ = "0.1.0.dev0"

__all__ = [
    # Core functionality
    "generate_uuid_only",
    "generate_uuid_with_prefix",
    "extract_uuid_from_prefixed",
    "generate_salt",
    # Configuration
    "IDConfig",
    "load_config_from_env",
    "get_default_config",
    "init_config_file",
    "validate_config_security",
    # Optional OO interface
    "UUIDGenerator",
    # Protocols
    "Representable",
    # Version
    "__version__",
]
