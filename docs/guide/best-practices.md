# Best Practices

Learn the optimal patterns and practices for using UUID-Forge effectively in production systems.

## UUID Generation Fundamentals

### Understanding Deterministic UUIDs

UUID-Forge generates UUIDv5 deterministic identifiers:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# Configure generator with namespace and salt
config = IDConfig(
    namespace=Namespace("myapp.com"),
    salt="v1"
)
generator = UUIDGenerator(config)

# Same inputs always produce the same UUID
uuid1 = generator.generate("user", email="alice@example.com")
uuid2 = generator.generate("user", email="alice@example.com")
assert uuid1 == uuid2  # ✅ Always deterministic
```

**Benefits:**

- UUIDv5 uses strong SHA-1 hashing
- Excellent collision resistance
- Industry standard for deterministic UUIDs
- No database lookups needed to find existing IDs

### When to Use Deterministic UUIDs

**✅ Good Use Cases:**

- Distributed systems needing consistent IDs
- Event deduplication in message queues
- Cache keys that need to be regenerated
- Cross-service entity identification
- Idempotent API operations

**❌ Not Suitable For:**

- Security tokens or session IDs (use random UUIDs)
- Cryptographic keys (use proper key generation)
- When inputs might contain PII that shouldn't be hashed

## Namespace Design

### Hierarchical Namespaces

Design namespaces hierarchically for better organization:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# Root namespace for your organization
ROOT_DOMAIN = "mycompany.com"

# Service-specific namespaces with hierarchical structure
user_service_config = IDConfig(
    namespace=Namespace(f"{ROOT_DOMAIN}/user-service"),
    salt="user-service-v1"
)
order_service_config = IDConfig(
    namespace=Namespace(f"{ROOT_DOMAIN}/order-service"),
    salt="order-service-v1"
)
product_service_config = IDConfig(
    namespace=Namespace(f"{ROOT_DOMAIN}/product-service"),
    salt="product-service-v1"
)

# Environment-specific separation through salts
dev_user_config = IDConfig(
    namespace=Namespace(f"{ROOT_DOMAIN}/user-service"),
    salt="user-service-dev"
)
prod_user_config = IDConfig(
    namespace=Namespace(f"{ROOT_DOMAIN}/user-service"),
    salt="user-service-prod"
)

# Create generators
user_generator = UUIDGenerator(user_service_config)
order_generator = UUIDGenerator(order_service_config)
```

### Namespace Naming Conventions

Follow consistent, URL-like naming patterns:

```python
from uuid_forge import Namespace

# ✅ Good: Clear, hierarchical domain-style naming
good_namespaces = [
    Namespace("mycompany.com/users/profiles"),
    Namespace("mycompany.com/users/auth"),
    Namespace("mycompany.com/orders/processing"),
    Namespace("mycompany.com/orders/fulfillment"),
]

# ❌ Avoid: Ambiguous or flat naming
# "ns1", "namespace_a", "temp_ns", "users"

# ✅ Include version in the salt instead
config = IDConfig(
    namespace=Namespace("mycompany.com/users"),
    salt="v2"  # Version here for easier migration
)
```

### Namespace Strategy for Multi-Service Architectures

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import Dict

class ServiceNamespaceManager:
    """Central manager for service namespaces"""

    def __init__(self, organization: str, environment: str = "production"):
        self.organization = organization
        self.environment = environment
        self.generators: Dict[str, UUIDGenerator] = {}

    def get_generator(self, service: str, version: str = "v1") -> UUIDGenerator:
        """Get generator for a service"""
        key = f"{service}-{version}"
        if key not in self.generators:
            config = IDConfig(
                namespace=Namespace(f"{self.organization}/{service}"),
                salt=f"{self.environment}-{version}"
            )
            self.generators[key] = UUIDGenerator(config)
        return self.generators[key]

# Usage
manager = ServiceNamespaceManager("mycompany.com", "production")
user_gen = manager.get_generator("users", "v1")
order_gen = manager.get_generator("orders", "v1")
```

## Input Data Preparation

### Canonical Representation

Ensure consistent input representation for deterministic UUIDs:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
generator = UUIDGenerator(config)

def prepare_user_attributes(user_data: dict) -> dict:
    """Prepare user data for consistent UUID generation"""
    return {
        "email": user_data["email"].lower().strip(),
        "username": user_data["username"].lower().strip(),
        "department": user_data.get("department", "").lower().strip()
    }

# Use prepared attributes
raw_data = {"email": " Alice@Example.COM ", "username": "ALICE", "department": "Engineering"}
clean_attrs = prepare_user_attributes(raw_data)
user_uuid = generator.generate("user", **clean_attrs)
```

### Handle Optional and Null Values

Be consistent with optional, null, and empty values:

```python
def normalize_attributes(data: dict) -> dict:
    """Normalize attributes for UUID generation"""
    normalized = {}

    for key, value in data.items():
        if value is None:
            normalized[key] = ""  # Consistent null representation
        elif isinstance(value, str):
            normalized[key] = value.strip().lower()
        elif isinstance(value, (int, float, bool)):
            normalized[key] = value
        else:
            # Convert other types to string
            normalized[key] = str(value)

    return normalized

# Usage
raw_attrs = {
    "email": "user@example.com",
    "age": 30,
    "verified": True,
    "middle_name": None,  # Optional field
}

clean_attrs = normalize_attributes(raw_attrs)
user_uuid = generator.generate("user", **clean_attrs)
```

### Attribute Ordering and Consistency

UUID-Forge handles attribute ordering automatically:

```python
# These all produce the SAME UUID - order doesn't matter
uuid1 = generator.generate("user", email="a@example.com", id=123, region="us")
uuid2 = generator.generate("user", region="us", id=123, email="a@example.com")
uuid3 = generator.generate("user", id=123, email="a@example.com", region="us")

assert uuid1 == uuid2 == uuid3  # ✅ All identical

# But different attribute VALUES produce different UUIDs
uuid4 = generator.generate("user", email="a@example.com", id=123, region="eu")
assert uuid1 != uuid4  # ✅ Different region = different UUID
```

## Performance Optimization

### Reuse Generator Instances

Create `UUIDGenerator` instances once and reuse them:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# ✅ Good: Create once, reuse many times
class UserService:
    def __init__(self):
        config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
        self.generator = UUIDGenerator(config)

    def create_user_uuid(self, email: str, region: str):
        return self.generator.generate("user", email=email, region=region)

# ❌ Avoid: Creating new instances repeatedly
def create_user_uuid_bad(email: str, region: str):
    # Inefficient - creates new generator every call
    config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
    generator = UUIDGenerator(config)
    return generator.generate("user", email=email, region=region)
```

### Batch Processing

Process multiple items efficiently by reusing the generator:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import List, Dict
from uuid import UUID

def process_users_batch(users: List[Dict[str, str]]) -> List[Dict]:
    """Process multiple users efficiently"""
    config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
    generator = UUIDGenerator(config)

    return [
        {
            "uuid": generator.generate("user", **user),
            "data": user
        }
        for user in users
    ]

# Process thousands of items efficiently
users = [
    {"email": "user1@example.com", "region": "us"},
    {"email": "user2@example.com", "region": "eu"},
    # ... thousands more
]
results = process_users_batch(users)
```

### Caching for Repeated Lookups

Cache UUIDs when the same inputs are queried frequently:

```python
from functools import lru_cache
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class CachedUUIDService:
    def __init__(self, namespace: str, salt: str):
        config = IDConfig(namespace=Namespace(namespace), salt=salt)
        self.generator = UUIDGenerator(config)

    @lru_cache(maxsize=10000)
    def get_user_uuid(self, email: str) -> UUID:
        """Cache frequently accessed user UUIDs"""
        return self.generator.generate("user", email=email)

    @lru_cache(maxsize=10000)
    def get_product_uuid(self, sku: str) -> UUID:
        """Cache frequently accessed product UUIDs"""
        return self.generator.generate("product", sku=sku)

    def clear_caches(self):
        """Clear all caches when needed"""
        self.get_user_uuid.cache_clear()
        self.get_product_uuid.cache_clear()

# Usage
service = CachedUUIDService("myapp.com", "v1")

# First call - generates UUID
uuid1 = service.get_user_uuid("alice@example.com")

# Second call - returned from cache (fast!)
uuid2 = service.get_user_uuid("alice@example.com")

assert uuid1 == uuid2
```

### When NOT to Cache

**Don't cache when:**

- Inputs are highly varied (low cache hit rate)
- Memory is constrained
- UUID generation is already fast enough (it's very fast!)

**Do cache when:**

- Same inputs queried frequently
- Lookup patterns are predictable
- Cache hit rate will be high (>50%)

## Error Handling

### Robust Input Validation

Validate inputs before UUID generation:

```python
import logging
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID
from typing import Optional

logger = logging.getLogger(__name__)

def safe_generate_uuid(
    generator: UUIDGenerator,
    entity_type: str,
    **attributes
) -> Optional[UUID]:
    """Safely generate UUID with proper error handling"""
    try:
        # Validate entity type
        if not entity_type or not isinstance(entity_type, str):
            raise ValueError("entity_type must be a non-empty string")

        # Validate attributes
        if not attributes:
            raise ValueError("At least one attribute must be provided")

        # Check for None or empty string values
        for key, value in attributes.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Attribute '{key}' cannot be None or empty")

        return generator.generate(entity_type, **attributes)

    except ValueError as e:
        logger.error(f"Invalid input for UUID generation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during UUID generation: {e}")
        raise

# Usage
config = IDConfig(namespace=Namespace("myapp.com"), salt="v1")
generator = UUIDGenerator(config)

try:
    user_uuid = safe_generate_uuid(
        generator,
        "user",
        email="alice@example.com",
        region="us"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Environment-Based Fallback

Handle different environments with fallback configurations:

```python
import os
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import Optional

def create_generator_with_fallback(
    service_name: str,
    primary_namespace: Optional[str] = None,
    fallback_namespace: str = "default.local"
) -> UUIDGenerator:
    """Create generator with environment-based fallback"""
    try:
        # Try to get namespace from environment
        namespace_domain = (
            primary_namespace
            or os.environ.get("UUID_NAMESPACE_DOMAIN")
            or fallback_namespace
        )

        config = IDConfig(
            namespace=Namespace(f"{namespace_domain}/{service_name}"),
            salt=os.environ.get("UUID_SALT_VERSION", "v1")
        )

        logger.info(f"Created UUID generator for {service_name} with namespace {namespace_domain}")
        return UUIDGenerator(config)

    except Exception as e:
        logger.warning(f"Failed to create primary generator: {e}, using fallback")
        # Use fallback configuration
        config = IDConfig(
            namespace=Namespace(f"{fallback_namespace}/{service_name}"),
            salt="v1"
        )
        return UUIDGenerator(config)

# Usage
generator = create_generator_with_fallback("users", primary_namespace="mycompany.com")
```

## Testing Strategies

### Deterministic Testing

Leverage determinism for reliable, reproducible tests:

```python
import pytest
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

def test_user_uuid_generation_is_deterministic():
    """Test that UUID generation is deterministic"""
    config = IDConfig(namespace=Namespace("test.myapp.com"), salt="test-v1")
    generator = UUIDGenerator(config)

    # Generate UUID multiple times with same inputs
    uuid1 = generator.generate("user", email="test@example.com", name="Test User")
    uuid2 = generator.generate("user", email="test@example.com", name="Test User")

    # Should be identical
    assert uuid1 == uuid2
    assert isinstance(uuid1, UUID)

def test_different_inputs_produce_different_uuids():
    """Test that different inputs produce different UUIDs"""
    config = IDConfig(namespace=Namespace("test.myapp.com"), salt="test-v1")
    generator = UUIDGenerator(config)

    uuid1 = generator.generate("user", email="alice@example.com")
    uuid2 = generator.generate("user", email="bob@example.com")

    # Different inputs = different UUIDs
    assert uuid1 != uuid2

def test_attribute_order_independence():
    """Test that attribute order doesn't matter"""
    config = IDConfig(namespace=Namespace("test.myapp.com"), salt="test-v1")
    generator = UUIDGenerator(config)

    uuid1 = generator.generate("user", email="test@example.com", id=123, region="us")
    uuid2 = generator.generate("user", region="us", id=123, email="test@example.com")

    # Same attributes in different order = same UUID
    assert uuid1 == uuid2
```

### Test Data Management

Use consistent test fixtures:

```python
import pytest
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# Test fixtures
@pytest.fixture
def test_generator():
    """Create a generator for testing"""
    config = IDConfig(namespace=Namespace("test.example.com"), salt="test-v1")
    return UUIDGenerator(config)

@pytest.fixture
def test_users():
    """Sample test users"""
    return [
        {"email": "user1@test.com", "region": "us"},
        {"email": "user2@test.com", "region": "eu"},
        {"email": "user3@test.com", "region": "asia"},
    ]

def test_batch_uuid_generation(test_generator, test_users):
    """Test batch UUID generation"""
    uuids = [
        test_generator.generate("user", **user)
        for user in test_users
    ]

    # All UUIDs should be unique (different inputs)
    assert len(set(uuids)) == len(uuids)

    # All should be valid UUID objects
    for uuid_obj in uuids:
        assert isinstance(uuid_obj, UUID)

def test_uuid_regeneration(test_generator, test_users):
    """Test that UUIDs can be regenerated"""
    # Generate UUIDs for all users
    original_uuids = [
        test_generator.generate("user", **user)
        for user in test_users
    ]

    # Regenerate UUIDs for same users
    regenerated_uuids = [
        test_generator.generate("user", **user)
        for user in test_users
    ]

    # Should be identical
    assert original_uuids == regenerated_uuids
```

## Production Deployment

### Configuration Management

Use environment-specific configuration:

```python
import os
from uuid_forge import UUIDGenerator, IDConfig, Namespace
import logging

logger = logging.getLogger(__name__)

def create_production_generator(service_name: str) -> UUIDGenerator:
    """Create generator with production configuration from environment"""
    # Get configuration from environment variables
    namespace_domain = os.environ.get(
        "UUID_NAMESPACE_DOMAIN",
        "myapp.com"  # fallback
    )

    environment = os.environ.get("APP_ENVIRONMENT", "production")
    version = os.environ.get("UUID_VERSION", "v1")

    # Create configuration
    config = IDConfig(
        namespace=Namespace(f"{namespace_domain}/{service_name}"),
        salt=f"{environment}-{version}"
    )

    logger.info(
        f"Created UUID generator: service={service_name}, "
        f"namespace={namespace_domain}, env={environment}, version={version}"
    )

    return UUIDGenerator(config)

# Usage
user_generator = create_production_generator("users")
order_generator = create_production_generator("orders")
```

### Monitoring and Logging

Monitor UUID generation in production:

```python
import logging
import time
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID
from typing import Any

logger = logging.getLogger(__name__)

class MonitoredUUIDGenerator:
    """UUID generator with monitoring and metrics"""

    def __init__(self, namespace: str, salt: str):
        config = IDConfig(namespace=Namespace(namespace), salt=salt)
        self.generator = UUIDGenerator(config)
        self.generation_count = 0
        self.total_time = 0.0

    def generate(self, entity_type: str, **attributes) -> UUID:
        """Generate UUID with monitoring"""
        start_time = time.time()

        try:
            result = self.generator.generate(entity_type, **attributes)
            self.generation_count += 1

            duration = time.time() - start_time
            self.total_time += duration

            # Log every 1000 generations
            if self.generation_count % 1000 == 0:
                avg_time = self.total_time / self.generation_count
                logger.info(
                    f"UUID stats: count={self.generation_count}, "
                    f"avg_time={avg_time*1000:.2f}ms"
                )

            return result

        except Exception as e:
            logger.error(f"UUID generation failed: entity_type={entity_type}, error={e}")
            raise

    def get_stats(self) -> dict:
        """Get generation statistics"""
        return {
            "generation_count": self.generation_count,
            "total_time_seconds": self.total_time,
            "average_time_ms": (self.total_time / self.generation_count * 1000)
            if self.generation_count > 0
            else 0,
        }

# Usage
generator = MonitoredUUIDGenerator("myapp.com/users", "prod-v1")

# Generate many UUIDs
for i in range(10000):
    uuid = generator.generate("user", id=i, region="us")

# Check stats
stats = generator.get_stats()
print(f"Generated {stats['generation_count']} UUIDs")
print(f"Average time: {stats['average_time_ms']:.2f}ms")
```

## Security Considerations

### Sensitive Data Handling

**⚠️ Important:** UUID-Forge UUIDs are deterministic. Anyone with the same inputs can generate the same UUID.

**Do NOT use for:**

- Session tokens
- Authentication tokens
- Password reset tokens
- API keys
- Cryptographic keys

**Best Practices:**

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from datetime import date

config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
generator = UUIDGenerator(config)

def generate_user_uuid_safe(user_data: dict):
    """Generate UUID using only non-sensitive identifiers"""
    # ✅ Safe: Use non-sensitive business identifiers
    safe_attributes = {
        "user_id": user_data["id"],  # Internal ID
        "account_type": user_data["account_type"],  # Public info
        "created_date": user_data["created_at"].date().isoformat()  # Public info
    }

    # ❌ NEVER include in UUIDs:
    # - passwords (even hashed)
    # - social security numbers
    # - credit card numbers
    # - health information
    # - other PII that shouldn't be deterministically exposed

    return generator.generate("user", **safe_attributes)

# Good: Email addresses CAN be used if acceptable in your use case
def generate_user_uuid_from_email(email: str):
    """Generate UUID from email (if appropriate for your security model)"""
    # This is deterministic - same email always produces same UUID
    # Only use if this behavior is acceptable in your system
    return generator.generate("user", email=email.lower())
```

### Namespace Isolation by Security Context

Isolate UUIDs by security level or access context:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import Dict
from enum import Enum

class SecurityContext(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    ADMIN = "admin"

class ContextualUUIDGenerator:
    """Generate UUIDs with security context isolation"""

    def __init__(self, base_namespace: str):
        self.generators: Dict[SecurityContext, UUIDGenerator] = {}

        # Create separate generators for each context
        for context in SecurityContext:
            config = IDConfig(
                namespace=Namespace(f"{base_namespace}/{context.value}"),
                salt=f"{context.value}-v1"
            )
            self.generators[context] = UUIDGenerator(config)

    def generate(self, context: SecurityContext, entity_type: str, **attributes):
        """Generate UUID for a specific security context"""
        return self.generators[context].generate(entity_type, **attributes)

# Usage
manager = ContextualUUIDGenerator("myapp.com")

# Public-facing resource UUIDs
public_uuid = manager.generate(
    SecurityContext.PUBLIC,
    "article",
    slug="hello-world"
)

# Internal system UUIDs
internal_uuid = manager.generate(
    SecurityContext.INTERNAL,
    "audit_log",
    user_id=123,
    action="login"
)

# Admin-only resource UUIDs
admin_uuid = manager.generate(
    SecurityContext.ADMIN,
    "system_config",
    key="database_connection"
)

# Same inputs, different contexts = different UUIDs
assert public_uuid != internal_uuid != admin_uuid
```

## Migration and Versioning

### Salt-Based Version Migration

Use salts to version your UUID generation scheme:

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import Dict, Tuple
from uuid import UUID

class UUIDMigrationService:
    """Manage UUID schema migrations using salts"""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.generators = {}

    def get_generator(self, version: str) -> UUIDGenerator:
        """Get generator for a specific version"""
        if version not in self.generators:
            config = IDConfig(
                namespace=Namespace(self.namespace),
                salt=version
            )
            self.generators[version] = UUIDGenerator(config)
        return self.generators[version]

    def migrate_entity(
        self,
        entity_type: str,
        old_version: str,
        new_version: str,
        **attributes
    ) -> Tuple[UUID, UUID]:
        """Generate both old and new UUIDs for migration"""
        old_gen = self.get_generator(old_version)
        new_gen = self.get_generator(new_version)

        old_uuid = old_gen.generate(entity_type, **attributes)
        new_uuid = new_gen.generate(entity_type, **attributes)

        return old_uuid, new_uuid

# Usage: Migrating from v1 to v2 UUID scheme
migration = UUIDMigrationService("users.myapp.com")

# Generate migration mapping
users = [
    {"email": "alice@example.com", "region": "us"},
    {"email": "bob@example.com", "region": "eu"},
]

migration_map = {}
for user in users:
    old_uuid, new_uuid = migration.migrate_entity(
        "user",
        old_version="v1",
        new_version="v2",
        **user
    )
    migration_map[old_uuid] = new_uuid
    print(f"Migrate {old_uuid} -> {new_uuid}")

# Update database
# for old_uuid, new_uuid in migration_map.items():
#     db.execute("UPDATE users SET id = %s WHERE id = %s", (new_uuid, old_uuid))
```

### Zero-Downtime Migration Strategy

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID
from typing import Optional

class DualVersionUUIDGenerator:
    """Support both old and new UUID versions during migration"""

    def __init__(self, namespace: str, old_salt: str, new_salt: str):
        old_config = IDConfig(namespace=Namespace(namespace), salt=old_salt)
        new_config = IDConfig(namespace=Namespace(namespace), salt=new_salt)

        self.old_generator = UUIDGenerator(old_config)
        self.new_generator = UUIDGenerator(new_config)
        self.use_new_version = False  # Feature flag

    def generate(self, entity_type: str, **attributes) -> UUID:
        """Generate UUID using current version"""
        if self.use_new_version:
            return self.new_generator.generate(entity_type, **attributes)
        return self.old_generator.generate(entity_type, **attributes)

    def lookup_uuid(self, entity_type: str, **attributes) -> UUID:
        """Try new version first, fallback to old for lookups"""
        if self.use_new_version:
            return self.new_generator.generate(entity_type, **attributes)

        # During migration, might need to check both versions
        return self.old_generator.generate(entity_type, **attributes)

# Migration phases:
# Phase 1: Deploy code with both generators, use_new_version=False
dual = DualVersionUUIDGenerator("users.myapp.com", "v1", "v2")

# Phase 2: Run migration script to update all UUIDs in database

# Phase 3: Enable new version via feature flag
dual.use_new_version = True

# Phase 4: After verification, remove old generator code
```

## Common Pitfalls to Avoid

### ❌ Inconsistent Input Normalization

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
generator = UUIDGenerator(config)

# ❌ DON'T: Inconsistent casing and whitespace
uuid1 = generator.generate("user", email="User@Example.Com ")
uuid2 = generator.generate("user", email="user@example.com")
# These will be DIFFERENT because inputs differ!

# ✅ DO: Always normalize inputs
def normalize_email(email: str) -> str:
    return email.lower().strip()

uuid1 = generator.generate("user", email=normalize_email("User@Example.Com "))
uuid2 = generator.generate("user", email=normalize_email("user@example.com"))
# Now these are the SAME ✓
```

### ❌ Creating New Generator Instances Repeatedly

```python
# ❌ DON'T: Create new generator every call (inefficient)
def get_user_uuid_bad(user_email: str):
    config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
    generator = UUIDGenerator(config)  # New instance every time!
    return generator.generate("user", email=user_email)

# ✅ DO: Create once, reuse many times
class UserService:
    def __init__(self):
        config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
        self.generator = UUIDGenerator(config)  # Created once

    def get_user_uuid(self, user_email: str):
        return self.generator.generate("user", email=user_email)
```

### ❌ Mixing Salts/Namespaces for Same Entity

```python
# ❌ DON'T: Use different configurations for the same entity type
config_a = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
config_b = IDConfig(namespace=Namespace("users.myapp.com"), salt="v2")

gen_a = UUIDGenerator(config_a)
gen_b = UUIDGenerator(config_b)

# These will be DIFFERENT UUIDs for the same user!
uuid_a = gen_a.generate("user", email="alice@example.com")
uuid_b = gen_b.generate("user", email="alice@example.com")
assert uuid_a != uuid_b  # Different salts = different UUIDs

# ✅ DO: Use consistent configuration throughout your application
```

### ❌ Including Timestamps in Deterministic UUIDs

```python
from datetime import datetime

# ❌ DON'T: Include current timestamp (non-deterministic!)
def create_event_uuid_bad(event_type: str, user_id: int):
    return generator.generate(
        "event",
        event_type=event_type,
        user_id=user_id,
        timestamp=datetime.utcnow().isoformat()  # Changes every call!
    )

# This defeats the purpose - UUIDs will be different every time!

# ✅ DO: Only include deterministic attributes
def create_event_uuid_good(event_type: str, user_id: int, event_date: str):
    return generator.generate(
        "event",
        event_type=event_type,
        user_id=user_id,
        event_date=event_date  # Use date, not timestamp
    )
```

### ❌ Forgetting Entity Type Parameter

```python
# ❌ DON'T: Forget the entity_type parameter
# uuid = generator.generate(email="alice@example.com")  # TypeError!

# ✅ DO: Always include entity_type as first argument
uuid = generator.generate("user", email="alice@example.com")
```

## Next Steps

- [Use Cases](../use-cases/microservices.md) - See real-world implementation examples
- [API Reference](../api/core.md) - Detailed API documentation
- [Development](../development/contributing.md) - Contributing to UUID-Forge
