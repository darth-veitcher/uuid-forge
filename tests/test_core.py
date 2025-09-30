"""
Tests for uuid_forge.core module.

This test module ensures deterministic UUID generation works correctly
across all scenarios including idempotency, security, and edge cases.
"""

import uuid as uuid_module

import pytest

from uuid_forge.core import (
    IDConfig,
    UUIDGenerator,
    extract_uuid_from_prefixed,
    generate_salt,
    generate_uuid_only,
    generate_uuid_with_prefix,
)


class TestIDConfig:
    """Tests for IDConfig dataclass."""

    def test_default_config(self) -> None:
        """Test IDConfig with default values."""
        config = IDConfig()
        assert config.namespace == uuid_module.NAMESPACE_DNS
        assert config.salt == ""

    def test_custom_namespace(self) -> None:
        """Test IDConfig with custom namespace."""
        custom_ns = uuid_module.uuid4()
        config = IDConfig(namespace=custom_ns)
        assert config.namespace == custom_ns

    def test_custom_salt(self) -> None:
        """Test IDConfig with custom salt."""
        config = IDConfig(salt="my-secret-salt")
        assert config.salt == "my-secret-salt"

    def test_frozen_dataclass(self) -> None:
        """Test that IDConfig is immutable."""
        config = IDConfig()
        with pytest.raises(AttributeError):
            config.salt = "new-salt"  # type: ignore

    def test_invalid_namespace_type(self) -> None:
        """Test that non-UUID namespace raises TypeError."""
        with pytest.raises(TypeError, match="namespace must be a UUID"):
            IDConfig(namespace="not-a-uuid")  # type: ignore


class TestGenerateSalt:
    """Tests for generate_salt function."""

    def test_default_length(self) -> None:
        """Test salt generation with default length."""
        salt = generate_salt()
        assert isinstance(salt, str)
        assert len(salt) > 0
        # base64 encoding of 32 bytes should be ~43 characters
        assert len(salt) >= 40

    def test_custom_length(self) -> None:
        """Test salt generation with custom length."""
        salt_16 = generate_salt(16)
        salt_64 = generate_salt(64)
        assert len(salt_16) < len(salt_64)

    def test_minimum_length_validation(self) -> None:
        """Test that salt length below 16 raises ValueError."""
        with pytest.raises(ValueError, match="at least 16 bytes"):
            generate_salt(15)

    def test_uniqueness(self) -> None:
        """Test that each generated salt is unique."""
        salts = [generate_salt() for _ in range(10)]
        assert len(set(salts)) == 10, "All salts should be unique"

    def test_url_safe(self) -> None:
        """Test that generated salt is URL-safe."""
        salt = generate_salt()
        # URL-safe base64 should only contain alphanumeric, -, and _
        import re
        assert re.match(r'^[A-Za-z0-9_-]+$', salt), "Salt should be URL-safe"


class TestGenerateUUIDOnly:
    """Tests for generate_uuid_only function."""

    def test_basic_generation(self) -> None:
        """Test basic UUID generation."""
        uuid_obj = generate_uuid_only("test", key="value")
        assert isinstance(uuid_obj, uuid_module.UUID)

    def test_idempotency(self) -> None:
        """Test that same inputs produce same UUID."""
        uuid1 = generate_uuid_only("test", key="value")
        uuid2 = generate_uuid_only("test", key="value")
        assert uuid1 == uuid2

    def test_different_inputs_produce_different_uuids(self) -> None:
        """Test that different inputs produce different UUIDs."""
        uuid1 = generate_uuid_only("test", key="value1")
        uuid2 = generate_uuid_only("test", key="value2")
        assert uuid1 != uuid2

    def test_different_entity_types_produce_different_uuids(self) -> None:
        """Test that different entity types produce different UUIDs."""
        uuid1 = generate_uuid_only("invoice", key="value")
        uuid2 = generate_uuid_only("order", key="value")
        assert uuid1 != uuid2

    def test_kwargs_order_independence(self) -> None:
        """Test that kwargs order doesn't affect UUID generation."""
        uuid1 = generate_uuid_only("test", a=1, b=2, c=3)
        uuid2 = generate_uuid_only("test", c=3, a=1, b=2)
        uuid3 = generate_uuid_only("test", b=2, c=3, a=1)
        assert uuid1 == uuid2 == uuid3

    def test_with_config(self) -> None:
        """Test UUID generation with custom config."""
        config = IDConfig(salt="test-salt")
        uuid1 = generate_uuid_only("test", key="value", config=config)
        uuid2 = generate_uuid_only("test", key="value", config=config)
        assert uuid1 == uuid2

    def test_different_configs_produce_different_uuids(self) -> None:
        """Test that different configs produce different UUIDs."""
        config1 = IDConfig(salt="salt1")
        config2 = IDConfig(salt="salt2")
        uuid1 = generate_uuid_only("test", key="value", config=config1)
        uuid2 = generate_uuid_only("test", key="value", config=config2)
        assert uuid1 != uuid2

    def test_salt_affects_uuid(self) -> None:
        """Test that salt changes the generated UUID."""
        uuid_no_salt = generate_uuid_only("test", key="value")
        config_with_salt = IDConfig(salt="my-salt")
        uuid_with_salt = generate_uuid_only("test", key="value", config=config_with_salt)
        assert uuid_no_salt != uuid_with_salt

    def test_positional_args(self) -> None:
        """Test UUID generation with positional arguments."""
        uuid1 = generate_uuid_only("test", "arg1", "arg2")
        uuid2 = generate_uuid_only("test", "arg1", "arg2")
        assert uuid1 == uuid2

        # Different args should produce different UUID
        uuid3 = generate_uuid_only("test", "arg1", "arg3")
        assert uuid1 != uuid3

    def test_mixed_args_and_kwargs(self) -> None:
        """Test UUID generation with both positional and keyword arguments."""
        uuid1 = generate_uuid_only("test", "pos1", key1="val1", key2="val2")
        uuid2 = generate_uuid_only("test", "pos1", key1="val1", key2="val2")
        assert uuid1 == uuid2

    def test_invalid_config_type(self) -> None:
        """Test that invalid config type raises TypeError."""
        with pytest.raises(TypeError, match="config must be IDConfig"):
            generate_uuid_only("test", config="not-a-config")  # type: ignore

    def test_complex_values(self) -> None:
        """Test UUID generation with complex value types."""
        uuid1 = generate_uuid_only("test", count=42, price=19.99, active=True)
        uuid2 = generate_uuid_only("test", count=42, price=19.99, active=True)
        assert uuid1 == uuid2

    def test_empty_kwargs(self) -> None:
        """Test UUID generation with only entity type."""
        uuid1 = generate_uuid_only("test")
        uuid2 = generate_uuid_only("test")
        assert uuid1 == uuid2


class TestGenerateUUIDWithPrefix:
    """Tests for generate_uuid_with_prefix function."""

    def test_without_prefix(self) -> None:
        """Test that without prefix, only UUID is returned."""
        result = generate_uuid_with_prefix("test", key="value")
        assert "-" in result  # UUID contains dashes
        # Should be valid UUID string
        uuid_module.UUID(result)

    def test_with_prefix(self) -> None:
        """Test UUID generation with prefix."""
        result = generate_uuid_with_prefix("test", prefix="TST", key="value")
        assert result.startswith("TST-")
        # Extract UUID part
        uuid_part = result.split("-", 1)[1]
        uuid_module.UUID(uuid_part)

    def test_idempotency_with_prefix(self) -> None:
        """Test that same inputs produce same prefixed result."""
        result1 = generate_uuid_with_prefix("test", prefix="TST", key="value")
        result2 = generate_uuid_with_prefix("test", prefix="TST", key="value")
        assert result1 == result2

    def test_prefix_doesnt_affect_uuid(self) -> None:
        """Test that different prefixes don't change the UUID part."""
        result1 = generate_uuid_with_prefix("test", prefix="PREFIX1", key="value")
        result2 = generate_uuid_with_prefix("test", prefix="PREFIX2", key="value")

        # Extract UUID parts
        uuid1 = result1.split("-", 1)[1]
        uuid2 = result2.split("-", 1)[1]

        assert uuid1 == uuid2, "UUID should be same regardless of prefix"

    def test_custom_separator(self) -> None:
        """Test custom separator between prefix and UUID."""
        result = generate_uuid_with_prefix(
            "test",
            prefix="TST",
            separator="_",
            key="value"
        )
        assert result.startswith("TST_")
        assert "-" in result  # UUID still has dashes

    def test_complex_prefix(self) -> None:
        """Test with complex multi-segment prefix."""
        result = generate_uuid_with_prefix(
            "invoice",
            prefix="INV-EUR-2024",
            key="value"
        )
        assert result.startswith("INV-EUR-2024-")

    def test_with_config(self) -> None:
        """Test prefixed generation with custom config."""
        config = IDConfig(salt="test-salt")
        result1 = generate_uuid_with_prefix(
            "test",
            prefix="TST",
            config=config,
            key="value"
        )
        result2 = generate_uuid_with_prefix(
            "test",
            prefix="TST",
            config=config,
            key="value"
        )
        assert result1 == result2


class TestExtractUUIDFromPrefixed:
    """Tests for extract_uuid_from_prefixed function."""

    def test_extract_from_prefixed(self) -> None:
        """Test extracting UUID from prefixed identifier."""
        original_uuid = generate_uuid_only("test", key="value")
        prefixed = generate_uuid_with_prefix("test", prefix="TST", key="value")
        extracted = extract_uuid_from_prefixed(prefixed)
        assert extracted == original_uuid

    def test_extract_from_plain_uuid(self) -> None:
        """Test extracting from plain UUID string (no prefix)."""
        original_uuid = generate_uuid_only("test", key="value")
        uuid_str = str(original_uuid)
        extracted = extract_uuid_from_prefixed(uuid_str)
        assert extracted == original_uuid

    def test_extract_with_custom_separator(self) -> None:
        """Test extraction with custom separator."""
        original_uuid = generate_uuid_only("test", key="value")
        prefixed = generate_uuid_with_prefix(
            "test",
            prefix="TST",
            separator="_",
            key="value"
        )
        extracted = extract_uuid_from_prefixed(prefixed, separator="_")
        assert extracted == original_uuid

    def test_extract_complex_prefix(self) -> None:
        """Test extraction from complex multi-segment prefix."""
        original_uuid = generate_uuid_only("test", key="value")
        prefixed = generate_uuid_with_prefix(
            "test",
            prefix="INV-EUR-2024",
            key="value"
        )
        extracted = extract_uuid_from_prefixed(prefixed)
        assert extracted == original_uuid

    def test_invalid_input_raises_error(self) -> None:
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError, match="No valid UUID found"):
            extract_uuid_from_prefixed("not-a-uuid")

    def test_roundtrip(self) -> None:
        """Test full roundtrip: generate -> extract -> regenerate."""
        config = IDConfig(salt="test-salt")

        # Generate prefixed ID
        prefixed = generate_uuid_with_prefix(
            "invoice",
            prefix="INV-EUR",
            config=config,
            region="EUR",
            number=12345
        )

        # Extract UUID
        extracted = extract_uuid_from_prefixed(prefixed)

        # Regenerate from business data
        regenerated = generate_uuid_only(
            "invoice",
            config=config,
            region="EUR",
            number=12345
        )

        assert extracted == regenerated


class TestUUIDGenerator:
    """Tests for UUIDGenerator class."""

    def test_default_initialization(self) -> None:
        """Test generator with default config."""
        generator = UUIDGenerator()
        assert generator.config.namespace == uuid_module.NAMESPACE_DNS
        assert generator.config.salt == ""

    def test_custom_config(self) -> None:
        """Test generator with custom config."""
        config = IDConfig(salt="test-salt")
        generator = UUIDGenerator(config=config)
        assert generator.config.salt == "test-salt"

    def test_generate_method(self) -> None:
        """Test UUID generation via generate method."""
        generator = UUIDGenerator()
        uuid1 = generator.generate("test", key="value")
        uuid2 = generator.generate("test", key="value")
        assert uuid1 == uuid2

    def test_generate_with_prefix_method(self) -> None:
        """Test prefixed generation via generate_with_prefix method."""
        generator = UUIDGenerator()
        result1 = generator.generate_with_prefix("test", prefix="TST", key="value")
        result2 = generator.generate_with_prefix("test", prefix="TST", key="value")
        assert result1 == result2
        assert result1.startswith("TST-")

    def test_config_consistency(self) -> None:
        """Test that generator applies config consistently."""
        config = IDConfig(salt="test-salt")
        generator = UUIDGenerator(config=config)

        # Generate via generator
        uuid_gen = generator.generate("test", key="value")

        # Generate via function with same config
        uuid_func = generate_uuid_only("test", config=config, key="value")

        assert uuid_gen == uuid_func

    def test_multiple_generators_with_same_config(self) -> None:
        """Test that multiple generators with same config produce same UUIDs."""
        config = IDConfig(salt="test-salt")
        gen1 = UUIDGenerator(config=config)
        gen2 = UUIDGenerator(config=config)

        uuid1 = gen1.generate("test", key="value")
        uuid2 = gen2.generate("test", key="value")

        assert uuid1 == uuid2

    def test_different_generators_with_different_configs(self) -> None:
        """Test that different configs produce different UUIDs."""
        gen1 = UUIDGenerator(config=IDConfig(salt="salt1"))
        gen2 = UUIDGenerator(config=IDConfig(salt="salt2"))

        uuid1 = gen1.generate("test", key="value")
        uuid2 = gen2.generate("test", key="value")

        assert uuid1 != uuid2


class TestIntegration:
    """Integration tests for cross-system UUID coordination scenarios."""

    def test_cross_system_coordination(self) -> None:
        """Test UUID coordination across simulated storage systems."""
        config = IDConfig(salt="production-salt")

        # Service A generates UUID for invoice
        invoice_uuid = generate_uuid_only(
            "invoice",
            config=config,
            region="EUR",
            number=12345
        )

        # Service B regenerates UUID from business data (no communication needed)
        regenerated_uuid = generate_uuid_only(
            "invoice",
            config=config,
            region="EUR",
            number=12345
        )

        # Should be identical
        assert invoice_uuid == regenerated_uuid

        # Both services can use this UUID for:
        # - Postgres primary key
        # - S3 object key
        # - Redis cache key
        # - QDrant document ID
        # - MinIO object key

    def test_microservices_scenario(self) -> None:
        """Test realistic microservices scenario with multiple entity types."""
        config = IDConfig(salt="microservices-salt")

        # Order Service creates order
        order_uuid = generate_uuid_only(
            "order",
            config=config,
            customer_id=789,
            order_number=12345
        )

        # Invoice Service generates invoice for the same order
        invoice_uuid = generate_uuid_only(
            "invoice",
            config=config,
            order_id=str(order_uuid),
            invoice_number=1
        )

        # Shipping Service regenerates order UUID from business data
        shipping_order_uuid = generate_uuid_only(
            "order",
            config=config,
            customer_id=789,
            order_number=12345
        )

        # Should match original
        assert order_uuid == shipping_order_uuid

        # Different entities should have different UUIDs
        assert order_uuid != invoice_uuid

    def test_testing_and_reproduction(self) -> None:
        """Test that UUIDs can be reproduced for testing."""
        # Test environment uses known salt
        test_config = IDConfig(salt="test-environment-salt")

        # Generate UUID in test
        test_uuid = generate_uuid_only(
            "user",
            config=test_config,
            email="test@example.com"
        )

        # Later, regenerate for assertions
        expected_uuid = generate_uuid_only(
            "user",
            config=test_config,
            email="test@example.com"
        )

        assert test_uuid == expected_uuid

        # Can use in database queries, API calls, etc.
        # without needing to store the UUID anywhere
