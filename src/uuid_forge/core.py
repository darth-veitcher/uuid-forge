"""Core UUID generation utilities for deterministic, idempotent UUID creation.

This module provides the fundamental building blocks for generating deterministic
UUIDs that remain consistent across multiple systems without requiring coordination.
Perfect for microservices architectures where the same entity needs consistent
identifiers across Postgres, S3, Redis, QDrant, MinIO, and other storage systems.

The core principle: Same input + Same config = Same UUID, every time.
"""

import secrets
import uuid as uuid_module
from dataclasses import dataclass
from typing import Any, Protocol


class Representable(Protocol):
    """Protocol for objects that can be represented as strings.

    Any object implementing __repr__ satisfies this protocol and can be
    used directly with UUID generation functions.
    """

    def __repr__(self) -> str:
        """Return string representation of object."""
        ...


class Namespace:
    """A UUID namespace for logical separation of entity types.

    Provides a clean, simple way to create UUID namespaces without exposing
    the underlying uuid module complexity. Most users just need domain-based
    namespaces, so this class encapsulates that common pattern.

    Examples:
        ```python
        from uuid_forge import Namespace, IDConfig, UUIDGenerator

        # Simple domain-based namespace
        ns = Namespace("mycompany.com")

        # Service-specific namespace
        ns = Namespace("users.mycompany.com")

        # Multi-tenant namespace
        ns = Namespace(f"tenant-{tenant_id}.mycompany.com")

        # Use in configuration
        config = IDConfig(namespace=ns, salt="your-salt")
        ```
    """

    def __init__(self, domain: str):
        """Create a namespace from a domain name.

        Args:
            domain: Domain name to create namespace from (e.g., "mycompany.com")
        """
        self.domain = domain
        self._uuid = uuid_module.uuid5(uuid_module.NAMESPACE_DNS, domain)

    @property
    def uuid(self) -> uuid_module.UUID:
        """Get the underlying UUID for this namespace."""
        return self._uuid

    def __str__(self) -> str:
        """String representation shows the domain."""
        return f"Namespace({self.domain})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Namespace(domain='{self.domain}', uuid='{self._uuid}')"

    def __eq__(self, other: object) -> bool:
        """Two namespaces are equal if they have the same domain."""
        if isinstance(other, Namespace):
            return self.domain == other.domain
        return False

    def __hash__(self) -> int:
        """Hash based on domain for use in sets/dicts."""
        return hash(self.domain)


@dataclass(frozen=True)
class IDConfig:
    """Configuration for deterministic UUID generation.

    This configuration ensures consistent UUID generation across different
    services and deployments. The namespace provides logical separation
    between different entity types or applications, while the salt adds
    security by preventing UUID prediction attacks.

    Attributes:
        namespace: UUID namespace for generation. Can be a UUID object or a Namespace.
            Defaults to DNS-based namespace. For custom namespaces, use Namespace("domain.com").
        salt: Random salt for security. CRITICAL: Keep this secret! Generate once
            per deployment and store securely in environment variables. Without a salt,
            UUIDs are predictable, which may be a security risk.

    Examples:
        ```python
        from uuid_forge.core import IDConfig, Namespace

        # Simple domain-based namespace
        config = IDConfig(
            namespace=Namespace("mycompany.com"),
            salt="xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB"
        )

        # Service-specific namespace
        config = IDConfig(
            namespace=Namespace("users.mycompany.com"),
            salt="xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB"
        )
        ```

    Examples:
        >>> from uuid_forge.core import IDConfig
        >>> import uuid
        >>> config = IDConfig(namespace=uuid.NAMESPACE_DNS, salt="test-salt")
        >>> config.namespace == uuid.NAMESPACE_DNS
        True
        >>> config.salt == "test-salt"
        True
        >>> # Test immutability - this should raise FrozenInstanceError
        >>> config.salt = "new-salt"  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        FrozenInstanceError: cannot assign to field 'salt'
    """

    namespace: uuid_module.UUID | Namespace = uuid_module.NAMESPACE_DNS
    salt: str = ""

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not isinstance(self.namespace, uuid_module.UUID | Namespace):
            raise TypeError(
                f"namespace must be a UUID or Namespace, got {type(self.namespace).__name__}"
            )

    @property
    def namespace_uuid(self) -> uuid_module.UUID:
        """Get the UUID representation of the namespace."""
        if isinstance(self.namespace, Namespace):
            return self.namespace.uuid
        return self.namespace


def generate_salt(length: int = 32) -> str:
    """Generate a cryptographically secure random salt for UUID generation.

    This function creates a URL-safe, base64-encoded random string suitable
    for use as a salt in IDConfig. The salt should be generated once per
    deployment and stored securely in environment variables.

    Args:
        length: Length of the generated salt in bytes. Default is 32 bytes,
            which produces a 43-character base64 string.

    Returns:
        A URL-safe base64-encoded string suitable for use as a salt.

    Raises:
        ValueError: If length is less than 16 bytes (minimum recommended).

    Example:
        ```python
        from uuid_forge.core import generate_salt

        # Generate a new salt for your deployment
        salt = generate_salt()
        # Add this to your .env file: UUID_SALT={salt}
        ```

    Examples:
        >>> from uuid_forge.core import generate_salt
        >>> salt = generate_salt()
        >>> isinstance(salt, str)
        True
        >>> len(salt) > 0
        True
        >>> # Test different lengths
        >>> salt_16 = generate_salt(16)
        >>> salt_64 = generate_salt(64)
        >>> len(salt_16) < len(salt_64)
        True
        >>> # Test minimum length validation
        >>> generate_salt(15)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: Salt length must be at least 16 bytes for security, got 15
    """
    if length < 16:
        raise ValueError(f"Salt length must be at least 16 bytes for security, got {length}")

    return secrets.token_urlsafe(length)


def _normalize_input(*args: Any, **kwargs: Any) -> str:
    """Normalize input arguments into a consistent string representation.

    This internal function converts various input types into a canonical
    string format for UUID generation. It handles positional arguments,
    keyword arguments, and objects with __repr__ methods.

    Args:
        *args: Positional arguments to normalize. Can be strings, objects
            with __repr__, or any other type that can be converted to string.
        **kwargs: Keyword arguments to normalize. Keys are sorted alphabetically
            for consistency.

    Returns:
        A normalized string representation of all inputs, suitable for hashing.

    Example:
        ```python
        from uuid_forge.core import _normalize_input

        # Different input styles produce different outputs
        result1 = _normalize_input("invoice", region="EUR", number=123)
        result2 = _normalize_input("order", customer_id=456)
        ```

    Examples:
        >>> from uuid_forge.core import _normalize_input
        >>> # Test with positional args
        >>> result1 = _normalize_input("invoice", "EUR", 123)
        >>> "invoice" in result1
        True
        >>> # Test with kwargs (should be sorted)
        >>> result2 = _normalize_input(region="EUR", number=123)
        >>> result3 = _normalize_input(number=123, region="EUR")
        >>> result2 == result3  # kwargs should be sorted for consistency
        True
        >>> # Test with mixed args
        >>> result4 = _normalize_input("invoice", region="EUR")
        >>> "invoice" in result4 and "region" in result4
        True
    """
    parts = []

    # Add positional arguments
    for arg in args:
        if hasattr(arg, "__repr__"):
            parts.append(repr(arg))
        else:
            parts.append(str(arg))

    # Add keyword arguments (sorted for consistency)
    for key in sorted(kwargs.keys()):
        value = kwargs[key]
        if hasattr(value, "__repr__"):
            parts.append(f"{key}={repr(value)}")
        else:
            parts.append(f"{key}={value}")

    return "|".join(parts)


def generate_uuid_only(
    entity_type: str, *args: Any, config: IDConfig | None = None, **kwargs: Any
) -> uuid_module.UUID:
    """Generate a deterministic UUID from entity type and business data.

    This is the core function for generating idempotent UUIDs. Given the same
    inputs and configuration, it will always produce the same UUID. This enables
    zero-coordination ID generation across multiple services and storage systems.

    The function uses UUIDv5 (name-based, SHA-1) for deterministic generation,
    with an optional salt for security. The entity_type provides logical separation
    between different kinds of entities (e.g., "invoice", "order", "user").

    Args:
        entity_type: Type of entity being identified (e.g., "invoice", "order").
            This provides namespace separation between different entity types.
        *args: Positional arguments contributing to the UUID. Can be any
            serializable data that uniquely identifies the entity.
        config: Configuration for UUID generation. If None, uses default
            configuration (DNS namespace, no salt). IMPORTANT: In production,
            always provide a config with a salt for security.
        **kwargs: Keyword arguments contributing to the UUID. Keys are sorted
            alphabetically to ensure consistency regardless of argument order.

    Returns:
        A deterministic UUID that will be identical for the same inputs and config.

    Raises:
        TypeError: If config is provided but is not an IDConfig instance.

    Example:
        ```python
        from uuid_forge.core import generate_uuid_only, IDConfig
        import uuid
        import os

        # Production usage with config
        config = IDConfig(
            namespace=uuid.uuid5(uuid.NAMESPACE_DNS, "mycompany.com"),
            salt=os.getenv("UUID_SALT", "")
        )

        # Generate UUID for an invoice
        invoice_uuid = generate_uuid_only(
            "invoice",
            region="EUR",
            invoice_number=12345,
            config=config
        )

        # Later, regenerate the same UUID from business data
        regenerated = generate_uuid_only(
            "invoice",
            region="EUR",
            invoice_number=12345,
            config=config
        )

        assert invoice_uuid == regenerated  # Always the same!
        ```

    Examples:
        >>> from uuid_forge.core import generate_uuid_only, IDConfig
        >>> import uuid
        >>> # Test basic generation
        >>> uuid1 = generate_uuid_only("test", key="value")
        >>> isinstance(uuid1, uuid.UUID)
        True
        >>> # Test idempotency
        >>> uuid2 = generate_uuid_only("test", key="value")
        >>> uuid1 == uuid2  # Same inputs should produce same UUID
        True
        >>> # Test with different inputs
        >>> uuid3 = generate_uuid_only("test", key="other")
        >>> uuid1 != uuid3  # Different inputs should produce different UUIDs
        True
        >>> # Test with config
        >>> config = IDConfig(salt="test-salt")
        >>> uuid4 = generate_uuid_only("test", key="value", config=config)
        >>> uuid5 = generate_uuid_only("test", key="value", config=config)
        >>> uuid4 == uuid5  # Same config should produce same UUID
        True
        >>> # Test that different config produces different UUID
        >>> uuid6 = generate_uuid_only("test", key="value")
        >>> uuid4 != uuid6  # Different config should produce different UUID
        True
        >>> # Test kwargs order doesn't matter
        >>> uuid7 = generate_uuid_only("test", a=1, b=2)
        >>> uuid8 = generate_uuid_only("test", b=2, a=1)
        >>> uuid7 == uuid8  # Kwargs order shouldn't matter
        True
    """
    if config is None:
        config = IDConfig()
    elif not isinstance(config, IDConfig):
        raise TypeError(f"config must be IDConfig, got {type(config).__name__}")

    # Build the name string from entity type, salt, and normalized inputs
    parts = [entity_type]

    if config.salt:
        parts.append(f"salt:{config.salt}")

    normalized = _normalize_input(*args, **kwargs)
    if normalized:
        parts.append(normalized)

    name = "|".join(parts)

    # Generate deterministic UUID
    return uuid_module.uuid5(config.namespace_uuid, name)


def generate_uuid_with_prefix(
    entity_type: str,
    *args: Any,
    prefix: str | None = None,
    separator: str = "-",
    config: IDConfig | None = None,
    **kwargs: Any,
) -> str:
    """Generate a deterministic UUID with an optional human-readable prefix.

    This function extends generate_uuid_only by adding a human-readable prefix
    to the UUID. The prefix can be useful for:
    - Quick visual identification of entity types (e.g., "INV-" for invoices)
    - Including business context (e.g., "EUR-2024-" for European 2024 invoices)
    - Making logs and debugging more human-friendly

    The prefix does NOT affect the UUID generation - it's purely cosmetic.
    The same business data will always produce the same UUID, regardless of
    prefix used.

    Args:
        entity_type: Type of entity being identified (e.g., "invoice", "order").
        *args: Positional arguments contributing to the UUID.
        prefix: Human-readable prefix to prepend to the UUID. If None, only
            the UUID is returned (as a string). Can include business context
            like region codes, year, or entity type abbreviations.
        separator: Character(s) to use between prefix and UUID. Default is "-".
        config: Configuration for UUID generation. If None, uses default config.
        **kwargs: Keyword arguments contributing to the UUID.

    Returns:
        A string in the format "{prefix}{separator}{uuid}" if prefix is provided,
        or just "{uuid}" if prefix is None.

    Raises:
        TypeError: If config is provided but is not an IDConfig instance.

    Example:
        ```python
        from uuid_forge.core import generate_uuid_with_prefix, IDConfig
        import os

        config = IDConfig(salt=os.getenv("UUID_SALT", ""))

        # With prefix
        invoice_id = generate_uuid_with_prefix(
            "invoice",
            prefix="INV-EUR",
            region="EUR",
            number=12345,
            config=config
        )
        # Result: "INV-EUR-550e8400-e29b-41d4-a716-446655440000"

        # Without prefix (just UUID as string)
        invoice_id = generate_uuid_with_prefix(
            "invoice",
            region="EUR",
            number=12345,
            config=config
        )
        # Result: "550e8400-e29b-41d4-a716-446655440000"

        # Custom separator
        invoice_id = generate_uuid_with_prefix(
            "invoice",
            prefix="INV",
            separator="_",
            region="EUR",
            number=12345,
            config=config
        )
        # Result: "INV_550e8400-e29b-41d4-a716-446655440000"
        ```

    Examples:
        >>> from uuid_forge.core import generate_uuid_with_prefix, IDConfig
        >>> # Test without prefix
        >>> id1 = generate_uuid_with_prefix("test", key="value")
        >>> "-" in id1  # Should be a UUID string
        True
        >>> not id1.startswith("test")  # No prefix
        True
        >>> # Test with prefix
        >>> id2 = generate_uuid_with_prefix("test", prefix="TST", key="value")
        >>> id2.startswith("TST-")
        True
        >>> # Test idempotency with prefix
        >>> id3 = generate_uuid_with_prefix("test", prefix="TST", key="value")
        >>> id2 == id3  # Same inputs should produce same result
        True
        >>> # Test that different prefixes don't change UUID part
        >>> id4 = generate_uuid_with_prefix("test", prefix="OTHER", key="value")
        >>> uuid_part_2 = id2.split("-", 1)[1]
        >>> uuid_part_4 = id4.split("-", 1)[1]
        >>> uuid_part_2 == uuid_part_4  # UUID should be same regardless of prefix
        True
        >>> # Test custom separator
        >>> id5 = generate_uuid_with_prefix("test", prefix="TST", separator="_", key="value")
        >>> id5.startswith("TST_")  # Should use custom separator
        True
        >>> # Test with config
        >>> config = IDConfig(salt="test-salt")
        >>> id6 = generate_uuid_with_prefix("test", prefix="TST", config=config, key="value")
        >>> id7 = generate_uuid_with_prefix("test", prefix="TST", config=config, key="value")
        >>> id6 == id7  # Config should be applied consistently
        True
    """
    generated_uuid = generate_uuid_only(entity_type, *args, config=config, **kwargs)
    uuid_str = str(generated_uuid)

    if prefix:
        return f"{prefix}{separator}{uuid_str}"
    return uuid_str


def extract_uuid_from_prefixed(prefixed_id: str, separator: str = "-") -> uuid_module.UUID:
    """Extract the UUID from a prefixed identifier.

    This function parses a prefixed identifier string (created with
    generate_uuid_with_prefix) and extracts just the UUID portion.
    It intelligently handles both prefixed and non-prefixed UUIDs.

    Args:
        prefixed_id: The prefixed identifier string. Can be either:
            - A prefixed UUID: "INV-EUR-550e8400-e29b-41d4-a716-446655440000"
            - A plain UUID: "550e8400-e29b-41d4-a716-446655440000"
        separator: The separator used between prefix and UUID. Default is "-".

    Returns:
        The extracted UUID object.

    Raises:
        ValueError: If no valid UUID can be found in the input string.

    Example:
        ```python
        from uuid_forge.core import (
            generate_uuid_with_prefix,
            extract_uuid_from_prefixed,
            IDConfig
        )

        config = IDConfig(salt="my-secret-salt")

        # Generate a prefixed ID
        prefixed = generate_uuid_with_prefix(
            "invoice",
            prefix="INV-EUR",
            region="EUR",
            number=12345,
            config=config
        )
        # Result: "INV-EUR-550e8400-e29b-41d4-a716-446655440000"

        # Extract the UUID
        extracted_uuid = extract_uuid_from_prefixed(prefixed)

        # Regenerate from business data
        regenerated_uuid = generate_uuid_only(
            "invoice",
            region="EUR",
            number=12345,
            config=config
        )

        assert extracted_uuid == regenerated_uuid
        ```

    Examples:
        >>> from uuid_forge.core import (
        ...     generate_uuid_with_prefix,
        ...     extract_uuid_from_prefixed,
        ...     generate_uuid_only
        ... )
        >>> import uuid
        >>> # Test with prefixed UUID
        >>> prefixed = generate_uuid_with_prefix("test", prefix="TST", key="value")
        >>> extracted = extract_uuid_from_prefixed(prefixed)
        >>> isinstance(extracted, uuid.UUID)
        True
        >>> # Verify extracted UUID matches original
        >>> original = generate_uuid_only("test", key="value")
        >>> extracted == original
        True
        >>> # Test with plain UUID string
        >>> plain_uuid = str(generate_uuid_only("test", key="other"))
        >>> extracted2 = extract_uuid_from_prefixed(plain_uuid)
        >>> isinstance(extracted2, uuid.UUID)
        True
        >>> str(extracted2) == plain_uuid
        True
        >>> # Test with custom separator
        >>> prefixed_custom = generate_uuid_with_prefix("test", prefix="TST", separator="_", key="value")
        >>> extracted3 = extract_uuid_from_prefixed(prefixed_custom, separator="_")
    >>> extracted3 == original
    True
    >>> # Test with invalid input
    >>> extract_uuid_from_prefixed("not-a-uuid")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: No valid UUID found in 'not-a-uuid'
    """
    # Split by separator and try to find UUID pattern
    parts = prefixed_id.split(separator)

    # Try each part from the end (UUID is typically at the end)
    for i in range(len(parts)):
        # Join remaining parts in case UUID has dashes
        potential_uuid = separator.join(parts[i:])
        try:
            return uuid_module.UUID(potential_uuid)
        except ValueError:
            continue

    raise ValueError(f"No valid UUID found in '{prefixed_id}'")


class UUIDGenerator:
    """Object-oriented convenience wrapper for UUID generation.

    This class provides a stateful interface for UUID generation, holding
    a configuration that's applied to all generated UUIDs. This is useful
    when you're generating many UUIDs with the same configuration, as it
    reduces boilerplate and ensures consistency.

    The functional API (generate_uuid_only, generate_uuid_with_prefix) is
    recommended for most use cases. Use this class when you need:
    - Multiple UUIDs with the same configuration
    - Encapsulation of configuration in a service/repository
    - Dependency injection patterns

    Attributes:
        config: The IDConfig used for all UUID generation operations.

    Example:
        ```python
        from uuid_forge.core import UUIDGenerator, IDConfig
        import uuid
        import os

        # Create generator with production config
        generator = UUIDGenerator(
            config=IDConfig(
                namespace=uuid.uuid5(uuid.NAMESPACE_DNS, "mycompany.com"),
                salt=os.getenv("UUID_SALT", "")
            )
        )

        # Generate multiple UUIDs with same config
        invoice_uuid = generator.generate("invoice", region="EUR", number=123)
        order_uuid = generator.generate("order", customer_id=456)

        # With prefixes
        prefixed_invoice = generator.generate_with_prefix(
            "invoice",
            prefix="INV",
            region="EUR",
            number=123
        )
        ```

    Examples:
        >>> from uuid_forge.core import UUIDGenerator, IDConfig
        >>> import uuid
        >>> # Test with default config
        >>> gen = UUIDGenerator()
        >>> uuid1 = gen.generate("test", key="value")
        >>> isinstance(uuid1, uuid.UUID)
        True
        >>> # Test idempotency
        >>> uuid2 = gen.generate("test", key="value")
        >>> uuid1 == uuid2
        True
        >>> # Test with custom config
        >>> config = IDConfig(salt="test-salt")
        >>> gen_custom = UUIDGenerator(config=config)
        >>> uuid3 = gen_custom.generate("test", key="value")
        >>> uuid4 = gen_custom.generate("test", key="value")
        >>> uuid3 == uuid4
        True
        >>> # Different config produces different UUID
        >>> uuid1 != uuid3
        True
        >>> # Test generate_with_prefix
        >>> prefixed = gen.generate_with_prefix("test", prefix="TST", key="value")
        >>> prefixed.startswith("TST-")
        True
        >>> # Verify UUID part matches
        >>> from uuid_forge.core import extract_uuid_from_prefixed
        >>> extracted = extract_uuid_from_prefixed(prefixed)
        >>> extracted == uuid1
        True
    """

    def __init__(self, config: IDConfig | None = None) -> None:
        """Initialize the UUID generator with a configuration.

        Args:
            config: Configuration for UUID generation. If None, uses default
                configuration (DNS namespace, no salt).
        """
        self.config = config or IDConfig()

    def generate(self, entity_type: str, *args: Any, **kwargs: Any) -> uuid_module.UUID:
        """Generate a deterministic UUID using this generator's configuration.

        This is a convenience method that calls generate_uuid_only with the
        generator's stored configuration.

        Args:
            entity_type: Type of entity being identified.
            *args: Positional arguments contributing to the UUID.
            **kwargs: Keyword arguments contributing to the UUID.

        Returns:
            A deterministic UUID.
        """
        return generate_uuid_only(entity_type, *args, config=self.config, **kwargs)

    def generate_with_prefix(
        self,
        entity_type: str,
        *args: Any,
        prefix: str | None = None,
        separator: str = "-",
        **kwargs: Any,
    ) -> str:
        """Generate a deterministic UUID with prefix using this generator's configuration.

        This is a convenience method that calls generate_uuid_with_prefix with the
        generator's stored configuration.

        Args:
            entity_type: Type of entity being identified.
            *args: Positional arguments contributing to the UUID.
            prefix: Human-readable prefix to prepend to the UUID.
            separator: Character(s) to use between prefix and UUID.
            **kwargs: Keyword arguments contributing to the UUID.

        Returns:
            A string with optional prefix and UUID.
        """
        return generate_uuid_with_prefix(
            entity_type, *args, prefix=prefix, separator=separator, config=self.config, **kwargs
        )
