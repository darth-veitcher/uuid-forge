# Advanced Usage

Explore the advanced features and customization options of UUID-Forge for complex use cases.

## Custom Namespaces and Hierarchies

### Creating Namespace Hierarchies

```python
from uuid_forge import UUIDForge
import uuid

# Create a root namespace for your organization
org_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "mycompany.com")

# Create service-specific namespaces
user_service_ns = uuid.uuid5(org_namespace, "user-service")
order_service_ns = uuid.uuid5(org_namespace, "order-service")

# Use hierarchical namespaces
user_forge = UUIDForge(namespace=user_service_ns)
order_forge = UUIDForge(namespace=order_service_ns)
```

### Namespace Factories

```python
class NamespaceFactory:
    def __init__(self, root_namespace):
        self.root = root_namespace
        self._namespaces = {}

    def get_namespace(self, service_name):
        if service_name not in self._namespaces:
            self._namespaces[service_name] = uuid.uuid5(
                self.root, service_name
            )
        return self._namespaces[service_name]

# Usage
factory = NamespaceFactory(org_namespace)
user_ns = factory.get_namespace("users")
product_ns = factory.get_namespace("products")
```

## Complex Data Processing

### Nested Dictionary Handling

```python
complex_data = {
    "user": {
        "id": 12345,
        "profile": {
            "email": "john@example.com",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
    },
    "metadata": {
        "created_at": "2024-01-15T10:30:00Z",
        "version": "2.1"
    }
}

# UUID-Forge handles nested structures automatically
uuid_result = forge.generate(complex_data)
```

### Custom Serialization

```python
import json
from datetime import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Use custom serialization for consistent UUIDs
forge = UUIDForge(json_encoder=CustomEncoder)
```

## Performance Optimization

### Batch Processing

```python
# Efficient batch processing
def process_batch(items, namespace="default"):
    forge = UUIDForge(namespace=namespace)
    return [(item, forge.generate(item)) for item in items]

# Process large datasets
large_dataset = ["item_{}".format(i) for i in range(10000)]
results = process_batch(large_dataset)
```

### Caching Strategies

```python
from functools import lru_cache

class CachedUUIDForge:
    def __init__(self, namespace=None):
        self.forge = UUIDForge(namespace=namespace)

    @lru_cache(maxsize=1000)
    def generate_cached(self, input_data):
        return self.forge.generate(input_data)

# Use cached version for frequently accessed items
cached_forge = CachedUUIDForge()
```

## Multi-Version Support

### Version-Specific Generation

```python
# Different UUID versions for different use cases
v3_forge = UUIDForge(version=3)  # MD5-based
v4_forge = UUIDForge(version=4)  # Random
v5_forge = UUIDForge(version=5)  # SHA-1-based (recommended)

# Same input, different versions
input_data = "test@example.com"
uuid_v3 = v3_forge.generate(input_data)
uuid_v4 = v4_forge.generate(input_data)  # Non-deterministic
uuid_v5 = v5_forge.generate(input_data)
```

### Version Migration

```python
def migrate_uuids(old_items, old_version=3, new_version=5):
    """Migrate UUIDs from one version to another"""
    old_forge = UUIDForge(version=old_version)
    new_forge = UUIDForge(version=new_version)

    migrations = {}
    for item in old_items:
        old_uuid = old_forge.generate(item)
        new_uuid = new_forge.generate(item)
        migrations[old_uuid] = new_uuid

    return migrations
```

## Custom Input Processors

### Custom Object Handling

```python
class CustomProcessor:
    @staticmethod
    def process_object(obj):
        if hasattr(obj, 'to_uuid_string'):
            return obj.to_uuid_string()
        elif hasattr(obj, '__dict__'):
            return json.dumps(obj.__dict__, sort_keys=True)
        else:
            return str(obj)

# Register custom processor
forge = UUIDForge(object_processor=CustomProcessor.process_object)
```

## Integration Patterns

### Database Integration

```python
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = sa.Column(UUID(as_uuid=True), primary_key=True)
    email = sa.Column(sa.String, unique=True, nullable=False)

    def __init__(self, email):
        self.email = email
        # Generate deterministic UUID from email
        forge = UUIDForge(namespace="users")
        self.id = uuid.UUID(forge.generate(email))

# Usage
user = User("john@example.com")
# user.id is now a deterministic UUID
```

### Message Queue Integration

```python
import json
from uuid_forge import UUIDForge

class MessageHandler:
    def __init__(self):
        self.forge = UUIDForge(namespace="messages")

    def create_message(self, data):
        # Create deterministic message ID
        message_id = self.forge.generate(data)

        return {
            "id": message_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

    def is_duplicate(self, message_data, processed_ids):
        message_id = self.forge.generate(message_data)
        return message_id in processed_ids
```

## Configuration Management

### Environment-Based Configuration

```python
import os
from uuid_forge import UUIDForge, Config

def create_forge_from_env():
    config = Config(
        namespace=os.getenv('UUID_NAMESPACE', 'default'),
        version=int(os.getenv('UUID_VERSION', '5')),
        format=os.getenv('UUID_FORMAT', 'hex'),
        case=os.getenv('UUID_CASE', 'lower')
    )
    return UUIDForge(config)

# Use environment-specific configuration
forge = create_forge_from_env()
```

## Next Steps

- [CLI Reference](cli.md) - Master the command-line interface
- [Best Practices](best-practices.md) - Learn optimization techniques
- [Use Cases](../use-cases/microservices.md) - See real-world applications
