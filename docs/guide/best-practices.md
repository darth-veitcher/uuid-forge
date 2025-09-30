# Best Practices

Learn the optimal patterns and practices for using UUID-Forge effectively in production systems.

## Choosing the Right UUID Version

### Version 5 (Recommended)

Use UUID version 5 for most deterministic use cases:

```python
# Recommended for production
forge = UUIDForge(version=5)
```

**Benefits:**

- Strong SHA-1 hashing
- Excellent collision resistance
- Industry standard for deterministic UUIDs

### Version 3 (Legacy Support)

Only use version 3 when maintaining compatibility:

```python
# Only for legacy compatibility
forge = UUIDForge(version=3)
```

**Limitations:**

- Uses MD5 (considered cryptographically weak)
- Higher collision probability

### Version 4 (Random)

Use for non-deterministic requirements:

```python
# For truly random UUIDs
forge = UUIDForge(version=4)
```

## Namespace Design

### Hierarchical Namespaces

Design namespaces hierarchically for better organization:

```python
import uuid

# Root namespace for your organization
ROOT_NS = uuid.uuid5(uuid.NAMESPACE_DNS, "mycompany.com")

# Service-specific namespaces
USER_SERVICE_NS = uuid.uuid5(ROOT_NS, "user-service")
ORDER_SERVICE_NS = uuid.uuid5(ROOT_NS, "order-service")
PRODUCT_SERVICE_NS = uuid.uuid5(ROOT_NS, "product-service")

# Environment-specific namespaces
DEV_USER_NS = uuid.uuid5(USER_SERVICE_NS, "development")
PROD_USER_NS = uuid.uuid5(USER_SERVICE_NS, "production")
```

### Namespace Naming Conventions

Follow consistent naming patterns:

```python
# Good: Clear, hierarchical naming
namespaces = {
    "users.profiles": uuid.uuid5(ROOT_NS, "users.profiles"),
    "users.auth": uuid.uuid5(ROOT_NS, "users.auth"),
    "orders.processing": uuid.uuid5(ROOT_NS, "orders.processing"),
    "orders.fulfillment": uuid.uuid5(ROOT_NS, "orders.fulfillment")
}

# Avoid: Ambiguous or flat naming
# "ns1", "namespace_a", "temp_ns"
```

## Input Data Preparation

### Canonical Representation

Ensure consistent input representation:

```python
def prepare_user_input(user_data):
    """Prepare user data for consistent UUID generation"""
    return {
        "email": user_data["email"].lower().strip(),
        "username": user_data["username"].lower().strip(),
        "department": user_data.get("department", "").lower().strip()
    }

# Use prepared data
user_data = prepare_user_input(raw_user_data)
user_uuid = forge.generate(user_data)
```

### Handle Optional Fields

Be consistent with optional and null values:

```python
def normalize_data(data):
    """Normalize data structure for UUID generation"""
    normalized = {}
    for key, value in data.items():
        if value is None:
            normalized[key] = ""  # Consistent null representation
        elif isinstance(value, str):
            normalized[key] = value.strip().lower()
        else:
            normalized[key] = value
    return normalized
```

## Performance Optimization

### Reuse Forge Instances

Create forge instances once and reuse them:

```python
# Good: Reuse instances
class UserService:
    def __init__(self):
        self.user_forge = UUIDForge(namespace="users")

    def create_user_uuid(self, user_data):
        return self.user_forge.generate(user_data)

# Avoid: Creating new instances repeatedly
def create_user_uuid(user_data):
    forge = UUIDForge(namespace="users")  # Inefficient
    return forge.generate(user_data)
```

### Batch Processing

Process multiple items efficiently:

```python
def process_users_batch(users):
    """Process multiple users efficiently"""
    forge = UUIDForge(namespace="users")
    return [
        {
            "uuid": forge.generate(user),
            "data": user
        }
        for user in users
    ]
```

### Caching Strategies

Implement appropriate caching:

```python
from functools import lru_cache

class UUIDService:
    def __init__(self):
        self.forge = UUIDForge(namespace="default")

    @lru_cache(maxsize=1000)
    def get_cached_uuid(self, input_key):
        """Cache frequently accessed UUIDs"""
        return self.forge.generate(input_key)

    def clear_cache(self):
        """Clear cache when needed"""
        self.get_cached_uuid.cache_clear()
```

## Error Handling

### Robust Input Validation

Validate inputs before UUID generation:

```python
def safe_generate_uuid(forge, input_data):
    """Safely generate UUID with proper error handling"""
    try:
        if input_data is None:
            raise ValueError("Input data cannot be None")

        if isinstance(input_data, str) and not input_data.strip():
            raise ValueError("Input string cannot be empty")

        return forge.generate(input_data)

    except Exception as e:
        logger.error(f"UUID generation failed: {e}")
        raise
```

### Graceful Degradation

Handle failures gracefully:

```python
def generate_with_fallback(primary_forge, fallback_forge, input_data):
    """Generate UUID with fallback strategy"""
    try:
        return primary_forge.generate(input_data)
    except Exception as e:
        logger.warning(f"Primary forge failed: {e}, using fallback")
        return fallback_forge.generate(input_data)
```

## Testing Strategies

### Deterministic Testing

Leverage determinism for better tests:

```python
def test_user_uuid_generation():
    """Test that UUID generation is deterministic"""
    forge = UUIDForge(namespace="test-users")

    user_data = {"email": "test@example.com", "name": "Test User"}

    # Generate UUID multiple times
    uuid1 = forge.generate(user_data)
    uuid2 = forge.generate(user_data)

    # Should be identical
    assert uuid1 == uuid2

    # Should be valid UUID
    assert uuid.UUID(uuid1)
```

### Test Data Management

Use consistent test data:

```python
# Test fixtures
TEST_USERS = [
    {"email": "user1@test.com", "name": "User One"},
    {"email": "user2@test.com", "name": "User Two"},
    {"email": "user3@test.com", "name": "User Three"}
]

TEST_NAMESPACE = "test-environment"

def test_batch_uuid_generation():
    """Test batch UUID generation"""
    forge = UUIDForge(namespace=TEST_NAMESPACE)

    uuids = [forge.generate(user) for user in TEST_USERS]

    # All UUIDs should be unique
    assert len(set(uuids)) == len(uuids)

    # All should be valid UUIDs
    for uuid_str in uuids:
        assert uuid.UUID(uuid_str)
```

## Production Deployment

### Configuration Management

Use environment-specific configuration:

```python
import os
from uuid_forge import UUIDForge, Config

def create_production_forge():
    """Create forge with production configuration"""
    config = Config(
        namespace=os.environ["UUID_NAMESPACE"],
        version=int(os.environ.get("UUID_VERSION", "5")),
        format=os.environ.get("UUID_FORMAT", "hex")
    )
    return UUIDForge(config)
```

### Monitoring and Logging

Monitor UUID generation in production:

```python
import logging
import time

logger = logging.getLogger(__name__)

class MonitoredUUIDForge:
    def __init__(self, namespace=None):
        self.forge = UUIDForge(namespace=namespace)
        self.generation_count = 0

    def generate(self, input_data):
        start_time = time.time()

        try:
            result = self.forge.generate(input_data)
            self.generation_count += 1

            duration = time.time() - start_time
            logger.info(f"UUID generated in {duration:.3f}s")

            return result

        except Exception as e:
            logger.error(f"UUID generation failed: {e}")
            raise
```

## Security Considerations

### Sensitive Data Handling

Be careful with sensitive data in UUIDs:

```python
def generate_user_uuid_safe(user_data):
    """Generate UUID without exposing sensitive data"""
    # Use only non-sensitive identifiers
    safe_data = {
        "user_id": user_data["id"],
        "account_type": user_data["account_type"],
        "created_date": user_data["created_at"].date().isoformat()
    }
    # Don't include: passwords, PII, sensitive fields

    return forge.generate(safe_data)
```

### Namespace Isolation

Ensure proper namespace isolation:

```python
# Separate namespaces for different security contexts
PUBLIC_NS = uuid.uuid5(ROOT_NS, "public")
INTERNAL_NS = uuid.uuid5(ROOT_NS, "internal")
ADMIN_NS = uuid.uuid5(ROOT_NS, "admin")

# Use appropriate namespace based on context
def generate_context_uuid(data, context):
    namespaces = {
        "public": PUBLIC_NS,
        "internal": INTERNAL_NS,
        "admin": ADMIN_NS
    }

    forge = UUIDForge(namespace=namespaces[context])
    return forge.generate(data)
```

## Migration and Versioning

### Version Migration Strategy

Plan for UUID version migrations:

```python
class UUIDMigrationService:
    def __init__(self):
        self.old_forge = UUIDForge(version=3)  # Legacy
        self.new_forge = UUIDForge(version=5)  # New

    def migrate_uuid(self, input_data):
        """Migrate from old to new UUID version"""
        old_uuid = self.old_forge.generate(input_data)
        new_uuid = self.new_forge.generate(input_data)

        return {
            "old_uuid": old_uuid,
            "new_uuid": new_uuid,
            "input_data": input_data
        }
```

## Common Pitfalls to Avoid

### ❌ Inconsistent Input Preparation

```python
# Don't do this - inconsistent casing
uuid1 = forge.generate("User@Example.Com")
uuid2 = forge.generate("user@example.com")
# These will be different!
```

### ❌ Creating New Forge Instances Repeatedly

```python
# Don't do this - inefficient
def get_user_uuid(user_email):
    forge = UUIDForge(namespace="users")  # Creates new instance every time
    return forge.generate(user_email)
```

### ❌ Mixing UUID Versions for Same Entity

```python
# Don't do this - inconsistent versioning
user_uuid_v3 = UUIDForge(version=3).generate(user_data)
user_uuid_v5 = UUIDForge(version=5).generate(user_data)
# These will be different UUIDs for the same user!
```

## Next Steps

- [Use Cases](../use-cases/microservices.md) - See real-world implementation examples
- [API Reference](../api/core.md) - Detailed API documentation
- [Development](../development/contributing.md) - Contributing to UUID-Forge
