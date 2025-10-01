# Advanced Usage

Explore the advanced features and customization options of UUID-Forge for complex use cases.

## Custom Namespaces and Hierarchies

### Creating Namespace Hierarchies

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

# Create a root namespace for your organization
org_namespace = Namespace("mycompany.com")

# Create service-specific namespaces using the Namespace class
user_service_ns = Namespace("mycompany.com/user-service")
order_service_ns = Namespace("mycompany.com/order-service")

# Configure generators for each service
user_config = IDConfig(namespace=user_service_ns, salt="user-service-v1")
order_config = IDConfig(namespace=order_service_ns, salt="order-service-v1")

user_generator = UUIDGenerator(user_config)
order_generator = UUIDGenerator(order_config)

# Generate UUIDs in each service
user_uuid = user_generator.generate("user", email="alice@example.com")
order_uuid = order_generator.generate("order", order_id=12345)
```

### Namespace Factories

```python
from uuid_forge import Namespace, IDConfig, UUIDGenerator

class ServiceNamespaceFactory:
    """Factory for creating service-specific UUID generators"""
    def __init__(self, organization_domain: str, base_salt: str = "v1"):
        self.organization = organization_domain
        self.base_salt = base_salt
        self._generators = {}

    def get_generator(self, service_name: str) -> UUIDGenerator:
        """Get or create a generator for a specific service"""
        if service_name not in self._generators:
            namespace = Namespace(f"{self.organization}/{service_name}")
            config = IDConfig(
                namespace=namespace,
                salt=f"{service_name}-{self.base_salt}"
            )
            self._generators[service_name] = UUIDGenerator(config)
        return self._generators[service_name]

# Usage
factory = ServiceNamespaceFactory("mycompany.com")
user_gen = factory.get_generator("users")
product_gen = factory.get_generator("products")
order_gen = factory.get_generator("orders")

# Each service generates UUIDs in its own namespace
user_uuid = user_gen.generate("user", id=123)
product_uuid = product_gen.generate("product", sku="ABC-123")
```

## Complex Data Processing

### Multi-Attribute UUID Generation

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# Configure generator
config = IDConfig(namespace=Namespace("mycompany.com"), salt="v1")
generator = UUIDGenerator(config)

# Generate UUIDs from multiple attributes
# All attributes are combined deterministically
user_uuid = generator.generate(
    "user",
    id=12345,
    email="john@example.com",
    region="us-west"
)

# Same attributes in different order produce the same UUID
same_uuid = generator.generate(
    "user",
    region="us-west",
    email="john@example.com",
    id=12345
)

assert user_uuid == same_uuid  # ✅ Deterministic

# Complex nested data can be flattened
order_uuid = generator.generate(
    "order",
    user_id=12345,
    user_email="john@example.com",
    order_date="2024-01-15",
    order_version="2.1",
    theme="dark",
    notifications=True
)
```

### Date and Time Handling

```python
from datetime import datetime, date
from uuid_forge import UUIDGenerator, IDConfig, Namespace

config = IDConfig(namespace=Namespace("events.myapp.com"), salt="v1")
generator = UUIDGenerator(config)

# Use ISO format strings for consistent date/time handling
event_uuid = generator.generate(
    "event",
    user_id=123,
    timestamp="2024-01-15T10:30:00Z",  # ISO format
    event_type="login"
)

# For Python datetime objects, convert to ISO format
now = datetime.utcnow()
event_uuid = generator.generate(
    "event",
    user_id=123,
    timestamp=now.isoformat(),
    event_type="login"
)

# Date-based partitioning
today = date.today()
daily_uuid = generator.generate(
    "daily_report",
    date=today.isoformat(),
    region="us-west"
)
```

## Performance Optimization

### Batch Processing

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# Create generator once, reuse for many UUIDs
config = IDConfig(namespace=Namespace("items.myapp.com"), salt="v1")
generator = UUIDGenerator(config)

# Efficient batch processing
def process_batch(items, entity_type="item"):
    """Generate UUIDs for a batch of items"""
    return [
        (item_id, generator.generate(entity_type, id=item_id))
        for item_id in items
    ]

# Process large datasets efficiently
large_dataset = list(range(10000))
results = process_batch(large_dataset)

# Batch with different attributes
user_data = [
    {"email": "user1@example.com", "region": "us"},
    {"email": "user2@example.com", "region": "eu"},
    {"email": "user3@example.com", "region": "asia"},
]

user_uuids = [
    generator.generate("user", **user)
    for user in user_data
]
```

### Reusing Generators

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

class EntityUUIDManager:
    """Manager for generating UUIDs across multiple entity types"""

    def __init__(self, namespace: str, salt: str):
        config = IDConfig(namespace=Namespace(namespace), salt=salt)
        self.generator = UUIDGenerator(config)

    def user_uuid(self, email: str) -> UUID:
        """Generate user UUID from email"""
        return self.generator.generate("user", email=email)

    def order_uuid(self, user_email: str, order_id: int) -> UUID:
        """Generate order UUID from user and order ID"""
        return self.generator.generate("order", user_email=user_email, order_id=order_id)

    def product_uuid(self, sku: str) -> UUID:
        """Generate product UUID from SKU"""
        return self.generator.generate("product", sku=sku)

# Create once, use throughout application
manager = EntityUUIDManager("myapp.com", "prod-v1")

# Fast UUID generation for any entity
user_uuid = manager.user_uuid("alice@example.com")
order_uuid = manager.order_uuid("alice@example.com", 12345)
product_uuid = manager.product_uuid("WIDGET-001")
```

## Namespace Versioning and Migration

### Versioning with Salts

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace

# Version 1 of your UUID generation
config_v1 = IDConfig(namespace=Namespace("myapp.com"), salt="v1")
generator_v1 = UUIDGenerator(config_v1)

# Later, when you need to change UUID generation (e.g., schema change)
config_v2 = IDConfig(namespace=Namespace("myapp.com"), salt="v2")
generator_v2 = UUIDGenerator(config_v2)

# Same input, different UUIDs due to different salt
email = "user@example.com"
uuid_v1 = generator_v1.generate("user", email=email)
uuid_v2 = generator_v2.generate("user", email=email)

assert uuid_v1 != uuid_v2  # Different UUIDs for migration purposes
```

### Migration Strategy

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import Dict
from uuid import UUID

class UUIDMigrationManager:
    """Manage UUID migrations between versions"""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.generators = {}

    def get_generator(self, version: str) -> UUIDGenerator:
        """Get or create a generator for a specific version"""
        if version not in self.generators:
            config = IDConfig(
                namespace=Namespace(self.namespace),
                salt=version
            )
            self.generators[version] = UUIDGenerator(config)
        return self.generators[version]

    def create_migration_map(
        self,
        items: list,
        old_version: str,
        new_version: str,
        entity_type: str,
        key_field: str
    ) -> Dict[UUID, UUID]:
        """Create a mapping from old UUIDs to new UUIDs"""
        old_gen = self.get_generator(old_version)
        new_gen = self.get_generator(new_version)

        migration_map = {}
        for item in items:
            old_uuid = old_gen.generate(entity_type, **{key_field: item})
            new_uuid = new_gen.generate(entity_type, **{key_field: item})
            migration_map[old_uuid] = new_uuid

        return migration_map

# Usage
manager = UUIDMigrationManager("myapp.com")

# Migrate user UUIDs from v1 to v2
user_emails = ["alice@example.com", "bob@example.com", "carol@example.com"]
migration_map = manager.create_migration_map(
    items=user_emails,
    old_version="v1",
    new_version="v2",
    entity_type="user",
    key_field="email"
)

# Update database
for old_uuid, new_uuid in migration_map.items():
    # db.execute("UPDATE users SET id = %s WHERE id = %s", (new_uuid, old_uuid))
    pass
```

## Integration Patterns

### Database Integration with SQLAlchemy

```python
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

Base = declarative_base()

# Create a shared generator for user entities
user_config = IDConfig(namespace=Namespace("users.myapp.com"), salt="v1")
user_uuid_generator = UUIDGenerator(user_config)

class User(Base):
    __tablename__ = 'users'

    id = sa.Column(PGUUID(as_uuid=True), primary_key=True)
    email = sa.Column(sa.String, unique=True, nullable=False)
    region = sa.Column(sa.String, nullable=False)

    def __init__(self, email: str, region: str):
        self.email = email
        self.region = region
        # Generate deterministic UUID from email and region
        self.id = user_uuid_generator.generate("user", email=email, region=region)

# Usage
user = User(email="john@example.com", region="us-west")
# user.id is now a deterministic UUID: same email+region = same UUID
print(user.id)  # UUID('...')

# Later, recreate the same UUID without database lookup
same_uuid = user_uuid_generator.generate("user", email="john@example.com", region="us-west")
assert user.id == same_uuid
```

### Database Integration with Django

```python
from django.db import models
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

# Configure generator at module level
product_config = IDConfig(namespace=Namespace("products.myshop.com"), salt="v1")
product_uuid_generator = UUIDGenerator(product_config)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Generate UUID before first save
        if not self.id:
            self.id = product_uuid_generator.generate(
                "product",
                sku=self.sku,
                category=self.category
            )
        super().save(*args, **kwargs)

# Usage
product = Product(sku="WIDGET-001", name="Premium Widget", category="widgets")
product.save()
# product.id is now a deterministic UUID

# Regenerate UUID for lookups
product_uuid = product_uuid_generator.generate(
    "product",
    sku="WIDGET-001",
    category="widgets"
)
product = Product.objects.get(id=product_uuid)
```

### Message Queue Integration

```python
import json
from datetime import datetime
from uuid import UUID
from typing import Dict, Set, Any
from uuid_forge import UUIDGenerator, IDConfig, Namespace

class MessageHandler:
    """Handle message queue messages with deduplication"""

    def __init__(self, queue_namespace: str):
        config = IDConfig(namespace=Namespace(queue_namespace), salt="v1")
        self.generator = UUIDGenerator(config)
        self.processed_ids: Set[UUID] = set()

    def create_message(self, user_id: int, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a message with deterministic ID for deduplication"""
        # Generate UUID from user, event type, and data
        message_id = self.generator.generate(
            "message",
            user_id=user_id,
            event_type=event_type,
            data=json.dumps(data, sort_keys=True)  # Ensure consistent ordering
        )

        return {
            "id": str(message_id),
            "user_id": user_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

    def is_duplicate(self, user_id: int, event_type: str, data: Dict[str, Any]) -> bool:
        """Check if message has already been processed"""
        message_id = self.generator.generate(
            "message",
            user_id=user_id,
            event_type=event_type,
            data=json.dumps(data, sort_keys=True)
        )
        return message_id in self.processed_ids

    def mark_processed(self, user_id: int, event_type: str, data: Dict[str, Any]):
        """Mark a message as processed"""
        message_id = self.generator.generate(
            "message",
            user_id=user_id,
            event_type=event_type,
            data=json.dumps(data, sort_keys=True)
        )
        self.processed_ids.add(message_id)

# Usage
handler = MessageHandler("events.myapp.com")

# Create message
message = handler.create_message(
    user_id=123,
    event_type="user.login",
    data={"ip": "192.168.1.1", "device": "mobile"}
)

# Check for duplicates before processing
if not handler.is_duplicate(123, "user.login", {"ip": "192.168.1.1", "device": "mobile"}):
    # Process message
    print(f"Processing message {message['id']}")
    handler.mark_processed(123, "user.login", {"ip": "192.168.1.1", "device": "mobile"})
else:
    print("Duplicate message, skipping")
```

## Configuration Management

### Environment-Based Configuration

```python
import os
from uuid_forge import UUIDGenerator, IDConfig, Namespace

def create_generator_from_env(service_name: str) -> UUIDGenerator:
    """Create a UUID generator from environment variables"""
    # Get namespace from environment or use default
    namespace_domain = os.getenv('UUID_NAMESPACE_DOMAIN', 'myapp.com')
    namespace = Namespace(f"{namespace_domain}/{service_name}")

    # Get salt from environment with version/environment suffix
    environment = os.getenv('APP_ENVIRONMENT', 'production')  # dev, staging, production
    version = os.getenv('UUID_VERSION', 'v1')
    salt = f"{service_name}-{environment}-{version}"

    config = IDConfig(namespace=namespace, salt=salt)
    return UUIDGenerator(config)

# Usage: different environments get different UUIDs
# Production
# os.environ['APP_ENVIRONMENT'] = 'production'
# os.environ['UUID_NAMESPACE_DOMAIN'] = 'mycompany.com'

prod_generator = create_generator_from_env('users')

# Staging - same inputs, different UUIDs
# os.environ['APP_ENVIRONMENT'] = 'staging'

staging_generator = create_generator_from_env('users')

# Same user data generates different UUIDs in different environments
email = "test@example.com"
prod_uuid = prod_generator.generate("user", email=email)
staging_uuid = staging_generator.generate("user", email=email)

assert prod_uuid != staging_uuid  # Different environments = different UUIDs
```

### Multi-Tenant Configuration

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from typing import Dict

class TenantUUIDManager:
    """Manage UUID generation for multi-tenant applications"""

    def __init__(self, base_namespace: str):
        self.base_namespace = base_namespace
        self.generators: Dict[str, UUIDGenerator] = {}

    def get_generator(self, tenant_id: str) -> UUIDGenerator:
        """Get or create a generator for a specific tenant"""
        if tenant_id not in self.generators:
            # Each tenant gets its own namespace
            namespace = Namespace(f"{self.base_namespace}/tenant/{tenant_id}")
            config = IDConfig(namespace=namespace, salt=f"tenant-{tenant_id}-v1")
            self.generators[tenant_id] = UUIDGenerator(config)
        return self.generators[tenant_id]

    def generate_for_tenant(self, tenant_id: str, entity_type: str, **kwargs):
        """Generate a UUID for a specific tenant"""
        generator = self.get_generator(tenant_id)
        return generator.generate(entity_type, **kwargs)

# Usage
manager = TenantUUIDManager("saas.myapp.com")

# Tenant A
tenant_a_user = manager.generate_for_tenant(
    "tenant-a",
    "user",
    email="john@tenanta.com"
)

# Tenant B - same email, different UUID
tenant_b_user = manager.generate_for_tenant(
    "tenant-b",
    "user",
    email="john@tenanta.com"  # Same email, but different tenant
)

assert tenant_a_user != tenant_b_user  # Tenant isolation
```

## Next Steps

- [CLI Reference](cli.md) - Master the command-line interface
- [Best Practices](best-practices.md) - Learn optimization techniques
- [Use Cases](../use-cases/microservices.md) - See real-world applications
