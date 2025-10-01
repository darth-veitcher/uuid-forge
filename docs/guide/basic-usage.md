# Basic Usage

This guide covers the fundamental ways to use UUID-Forge in your applications.

## Quick Start

```python
from uuid_forge import UUIDGenerator, IDConfig
import os

# Create a generator with configuration
config = IDConfig(salt=os.getenv("UUID_FORGE_SALT"))
generator = UUIDGenerator(config=config)

# Generate a UUID from entity type and business data
user_id = generator.generate("user", email="john.doe@example.com")
print(user_id)  # 550e8400-e29b-41d4-a716-446655440000
```

## Creating UUIDs from Business Data

### Basic Entity Generation

```python
# User entity by email
user_uuid = generator.generate("user", email="user@example.com")

# Order entity by customer and timestamp
order_uuid = generator.generate("order", customer_id="12345", timestamp="2024-01-15")

# Product entity by SKU
product_uuid = generator.generate("product", sku="WIDGET-001")
```

### Multiple Attributes

```python
# Invoice with multiple identifying attributes
invoice_uuid = generator.generate(
    "invoice",
    region="EUR",
    year=2024,
    quarter="Q1",
    number=12345
)

# User with multiple identifiers
user_uuid = generator.generate(
    "user",
    email="john@example.com",
    username="john_doe",
    department="engineering"
)
```

### Using Different Entity Types

```python
# Each entity type creates a separate UUID namespace
user_uuid = generator.generate("user", identifier="alice@example.com")
order_uuid = generator.generate("order", identifier="alice@example.com")
invoice_uuid = generator.generate("invoice", identifier="alice@example.com")

# All different UUIDs, even though the identifier is the same
assert user_uuid != order_uuid != invoice_uuid
```

## Working with UUID Objects

```python
from uuid_forge import UUID

# The generate() method returns a standard UUID object
user_uuid = generator.generate("user", email="alice@example.com")

# Access UUID properties
print(user_uuid.hex)        # Hex string without dashes
print(user_uuid.bytes)      # Raw bytes
print(str(user_uuid))       # Standard hyphenated format
print(user_uuid.urn)        # URN format
print(user_uuid.int)        # Integer representation

# UUID comparison and operations
another_uuid = generator.generate("user", email="bob@example.com")
print(user_uuid < another_uuid)  # UUIDs are comparable
```

## Using Different Namespaces

```python
from uuid_forge import Namespace

# Different namespaces produce different UUIDs for same input
users_config = IDConfig(
    namespace=Namespace("users.mycompany.com"),
    salt=os.getenv("UUID_FORGE_SALT")
)
orders_config = IDConfig(
    namespace=Namespace("orders.mycompany.com"),
    salt=os.getenv("UUID_FORGE_SALT")
)

user_generator = UUIDGenerator(config=users_config)
order_generator = UUIDGenerator(config=orders_config)

# Same business data, different namespaces = different UUIDs
user_uuid = user_generator.generate("user", email="john@example.com")
order_uuid = order_generator.generate("order", email="john@example.com")

print(user_uuid != order_uuid)  # True
```

## Batch Generation

```python
# Generate multiple UUIDs efficiently
emails = [
    "user1@example.com",
    "user2@example.com",
    "user3@example.com"
]

# All with same entity type
user_uuids = [generator.generate("user", email=email) for email in emails]

# Different entity types
entities = [
    ("user", {"email": "user1@example.com"}),
    ("admin", {"email": "admin@example.com"}),
    ("guest", {"session_id": "12345"}),
]
uuids = [generator.generate(entity_type, **attrs) for entity_type, attrs in entities]
```

## Working with UUIDs Across Systems

```python
# Generate UUID in one system
invoice_uuid = generator.generate("invoice", region="EUR", number=12345)

# Store in database
db.execute(
    "INSERT INTO invoices (id, region, number) VALUES (%s, %s, %s)",
    (invoice_uuid, "EUR", 12345)
)

# Later, in a different service/system, regenerate the same UUID
# No database lookup needed!
same_uuid = generator.generate("invoice", region="EUR", number=12345)

# Retrieve from S3 directly
s3_object = s3.get_object(
    Bucket="invoices",
    Key=f"invoices/{same_uuid}.pdf"
)
```

## Using with Prefixes

```python
from uuid_forge import generate_uuid_with_prefix, extract_uuid_from_prefixed

# Generate with human-readable prefix
prefixed_id = generator.generate_with_prefix(
    "invoice",
    prefix="INV-EUR",
    region="EUR",
    number=12345
)
print(prefixed_id)  # INV-EUR-550e8400-e29b-41d4-a716-446655440000

# Extract UUID when needed
uuid_only = extract_uuid_from_prefixed(prefixed_id)
print(uuid_only)  # 550e8400-e29b-41d4-a716-446655440000
```

## UUID Properties and Operations

```python
# Generate a UUID
user_uuid = generator.generate("user", email="alice@example.com")

# UUID is a standard Python uuid.UUID object
print(isinstance(user_uuid, UUID))  # True

# String conversion
print(str(user_uuid))  # Standard format with hyphens

# UUIDs are hashable and can be used in sets/dicts
uuid_set = {user_uuid}
uuid_dict = {user_uuid: "alice"}

# UUIDs are comparable
uuid1 = generator.generate("user", email="alice@example.com")
uuid2 = generator.generate("user", email="bob@example.com")
print(uuid1 < uuid2)  # Deterministic comparison
```

## Next Steps

- [Advanced Usage](advanced-usage.md) - Explore advanced features and customization
- [CLI Reference](cli.md) - Learn about command-line usage
- [Best Practices](best-practices.md) - Optimize your UUID generation patterns
