"""Test all code examples from README.md to ensure they work correctly."""

import os
from unittest.mock import patch

from uuid_forge import (
    UUID,
    IDConfig,
    Namespace,
    UUIDGenerator,
    generate_uuid_only,
    load_config_from_env,
)


class TestBasicFunctionalAPI:
    """Test basic functional API examples from README."""

    def test_basic_functional_example(self):
        """Test the basic functional API example."""
        config = IDConfig(salt="test-salt")

        # Generate UUID from business data
        invoice_uuid = generate_uuid_only("invoice", config=config, region="EUR", number=12345)

        # Later, regenerate the EXACT SAME UUID from the same data
        regenerated = generate_uuid_only("invoice", config=config, region="EUR", number=12345)

        assert invoice_uuid == regenerated
        assert isinstance(invoice_uuid, UUID)

    @patch.dict(os.environ, {"UUID_FORGE_SALT": "test-env-salt"})
    def test_config_from_env(self):
        """Test loading config from environment."""
        config = load_config_from_env()

        user_uuid = generate_uuid_only("user", config=config, email="alice@example.com")

        assert isinstance(user_uuid, UUID)


class TestObjectOrientedAPI:
    """Test OO API examples from README."""

    def test_basic_oo_example(self):
        """Test basic OO API example."""
        generator = UUIDGenerator(config=IDConfig(salt="test-salt"))

        # Generate multiple UUIDs with same config
        user_uuid = generator.generate("user", email="alice@example.com")
        invoice_uuid = generator.generate("invoice", number=12345, region="EUR")
        order_uuid = generator.generate("order", user_id=str(user_uuid), total=99.99)

        assert isinstance(user_uuid, UUID)
        assert isinstance(invoice_uuid, UUID)
        assert isinstance(order_uuid, UUID)

        # Test prefixed IDs
        prefixed_id = generator.generate_with_prefix(
            "user", prefix="USER", email="alice@example.com"
        )

        assert prefixed_id.startswith("USER-")
        assert isinstance(prefixed_id, str)

    def test_service_class_pattern(self):
        """Test service class encapsulation pattern."""

        class InvoiceService:
            def __init__(self, salt: str):
                self.uuid_gen = UUIDGenerator(config=IDConfig(salt=salt))

            def create_invoice_id(self, region: str, number: int) -> str:
                return self.uuid_gen.generate_with_prefix(
                    "invoice", prefix=f"INV-{region}", region=region, number=number
                )

        service = InvoiceService("test-salt")
        invoice_id = service.create_invoice_id("EUR", 12345)

        assert invoice_id.startswith("INV-EUR-")
        assert len(invoice_id.split("-")) == 7  # INV-EUR-uuid parts


class TestRepositoryPattern:
    """Test Repository Pattern examples from README."""

    def test_repository_interface(self):
        """Test Repository Pattern implementation."""
        from typing import Protocol

        class EntityRepository(Protocol):
            def generate_id(self, **kwargs) -> UUID: ...

        class InvoiceRepository:
            def __init__(self):
                self.uuid_generator = UUIDGenerator(
                    config=IDConfig(namespace=Namespace("invoices.mycompany.com"), salt="test-salt")
                )

            def generate_id(self, region: str, number: int) -> UUID:
                return self.uuid_generator.generate("invoice", region=region, number=number)

            def generate_prefixed_id(self, region: str, number: int) -> str:
                return self.uuid_generator.generate_with_prefix(
                    "invoice", prefix=f"INV-{region}", region=region, number=number
                )

        repo = InvoiceRepository()
        invoice_id = repo.generate_id("EUR", 12345)
        prefixed_id = repo.generate_prefixed_id("EUR", 12345)

        assert isinstance(invoice_id, UUID)
        assert prefixed_id.startswith("INV-EUR-")


class TestFactoryPattern:
    """Test Factory Pattern examples from README."""

    def test_uuid_factory(self):
        """Test UUID Factory implementation."""
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
                    entity_type.value, prefix=prefix_map[entity_type], **attributes
                )

        factory = UUIDFactory(config=IDConfig(salt="test-salt"))
        user_uuid = factory.create_uuid(EntityType.USER, email="alice@example.com")
        order_id = factory.create_prefixed_uuid(
            EntityType.ORDER, user_id=str(user_uuid), items=["A", "B"]
        )

        assert isinstance(user_uuid, UUID)
        assert order_id.startswith("ORD-")


class TestDependencyInjection:
    """Test Dependency Injection pattern examples from README."""

    def test_uuid_service_di(self):
        """Test UUID service with dependency injection."""
        from abc import ABC, abstractmethod

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

        # Test production service
        prod_service = ProductionUUIDService(IDConfig(salt="prod-salt"))
        user_uuid = prod_service.generate_user_uuid("alice@example.com")
        order_uuid = prod_service.generate_order_uuid(user_uuid, 1234567890)

        assert isinstance(user_uuid, UUID)
        assert isinstance(order_uuid, UUID)

        # Test service
        test_service = TestUUIDService()
        test_user_uuid = test_service.generate_user_uuid("alice@example.com")
        test_order_uuid = test_service.generate_order_uuid(test_user_uuid, 1234567890)

        assert isinstance(test_user_uuid, UUID)
        assert isinstance(test_order_uuid, UUID)

        # Same inputs should produce same outputs in test service
        test_user_uuid2 = test_service.generate_user_uuid("alice@example.com")
        test_order_uuid2 = test_service.generate_order_uuid(test_user_uuid2, 1234567890)

        assert test_user_uuid == test_user_uuid2
        assert test_order_uuid == test_order_uuid2


class TestConfigurationExamples:
    """Test configuration examples from README."""

    def test_basic_configuration_patterns(self):
        """Test basic configuration patterns."""
        # Default configuration (no salt - not recommended for production)
        config = IDConfig()
        assert config.salt == ""

        # Production configuration with salt
        config = IDConfig(salt="production-salt")
        assert config.salt == "production-salt"

        # Custom namespace for your organization
        namespace = Namespace("mycompany.com")
        config = IDConfig(namespace=namespace, salt="production-salt")
        assert config.namespace == namespace
        assert config.salt == "production-salt"

    @patch.dict(
        os.environ, {"UUID_FORGE_SALT": "test-salt", "UUID_FORGE_NAMESPACE": "test.example.com"}
    )
    def test_environment_configuration(self):
        """Test environment-based configuration."""
        # Load from default environment variables
        config = load_config_from_env()

        assert config.salt == "test-salt"
        # Environment config returns Namespace when domain is provided
        expected_namespace = Namespace("test.example.com")
        assert config.namespace == expected_namespace

    def test_service_based_configuration(self):
        """Test service-based configuration pattern."""

        class UserService:
            def __init__(self):
                self.uuid_generator = UUIDGenerator(
                    config=IDConfig(namespace=Namespace("users.mycompany.com"), salt="test-salt")
                )

            def create_user_uuid(self, email: str) -> UUID:
                return self.uuid_generator.generate("user", email=email)

        service = UserService()
        user_uuid = service.create_user_uuid("alice@example.com")

        assert isinstance(user_uuid, UUID)

    def test_multi_tenant_configuration(self):
        """Test multi-tenant configuration pattern."""

        class TenantUUIDService:
            def __init__(self, tenant_id: str):
                self.generator = UUIDGenerator(
                    config=IDConfig(
                        namespace=Namespace(f"tenant-{tenant_id}.mycompany.com"), salt="test-salt"
                    )
                )

            def generate_entity_uuid(self, entity_type: str, **kwargs) -> UUID:
                return self.generator.generate(entity_type, **kwargs)

        service = TenantUUIDService("acme-corp")
        entity_uuid = service.generate_entity_uuid("user", email="alice@acme.com")

        assert isinstance(entity_uuid, UUID)

        # Different tenants should produce different UUIDs for same data
        service2 = TenantUUIDService("beta-corp")
        entity_uuid2 = service2.generate_entity_uuid("user", email="alice@acme.com")

        assert entity_uuid != entity_uuid2


class TestNamespaceClass:
    """Test the new Namespace class functionality."""

    def test_namespace_creation(self):
        """Test creating namespaces from domain names."""
        ns = Namespace("mycompany.com")

        assert ns.domain == "mycompany.com"
        assert isinstance(ns.uuid, UUID)
        assert str(ns) == "Namespace(mycompany.com)"
        assert "mycompany.com" in repr(ns)

    def test_namespace_equality(self):
        """Test namespace equality and hashing."""
        ns1 = Namespace("mycompany.com")
        ns2 = Namespace("mycompany.com")
        ns3 = Namespace("other.com")

        assert ns1 == ns2
        assert ns1 != ns3
        assert hash(ns1) == hash(ns2)
        assert hash(ns1) != hash(ns3)

    def test_namespace_in_config(self):
        """Test using Namespace in IDConfig."""
        ns = Namespace("mycompany.com")
        config = IDConfig(namespace=ns, salt="test-salt")

        assert config.namespace == ns
        assert config.namespace_uuid == ns.uuid
        assert isinstance(config.namespace_uuid, UUID)

    def test_namespace_deterministic(self):
        """Test that namespaces are deterministic."""
        ns1 = Namespace("mycompany.com")
        ns2 = Namespace("mycompany.com")

        assert ns1.uuid == ns2.uuid

    def test_namespace_vs_traditional_approach(self):
        """Test that Namespace produces same UUIDs as traditional approach."""
        from uuid_forge import NAMESPACE_DNS, uuid5

        # Traditional approach
        traditional_uuid = uuid5(NAMESPACE_DNS, "mycompany.com")

        # New Namespace approach
        ns = Namespace("mycompany.com")

        assert ns.uuid == traditional_uuid


class TestImportPatterns:
    """Test that our self-contained imports work correctly."""

    def test_uuid_imports_from_package(self):
        """Test that UUID, uuid5, and NAMESPACE_DNS can be imported from uuid_forge."""
        import uuid as std_uuid

        from uuid_forge import NAMESPACE_DNS, UUID, uuid5

        # Verify they're the same as standard library
        assert UUID is std_uuid.UUID
        assert uuid5 is std_uuid.uuid5
        assert NAMESPACE_DNS is std_uuid.NAMESPACE_DNS

        # Test they work for creating namespaces
        namespace = uuid5(NAMESPACE_DNS, "test.example.com")
        assert isinstance(namespace, UUID)

    def test_self_contained_config_creation(self):
        """Test creating configs with the new Namespace class."""
        from uuid_forge import IDConfig, Namespace

        config = IDConfig(namespace=Namespace("mycompany.com"), salt="test-salt")

        assert isinstance(config.namespace, Namespace)
        assert config.salt == "test-salt"
