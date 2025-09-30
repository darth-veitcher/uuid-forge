# Basic Usage

This guide covers the fundamental ways to use UUID-Forge in your applications.

## Quick Start

```python
from uuid_forge import UUIDForge

# Create a forge instance
forge = UUIDForge()

# Generate a UUID from a string
user_id = forge.generate("john.doe@example.com")
print(user_id)  # 550e8400-e29b-41d4-a716-446655440000
```

## Creating UUIDs from Different Input Types

### From Strings

```python
# Simple string
uuid1 = forge.generate("user123")

# Email addresses
uuid2 = forge.generate("user@example.com")

# Complex identifiers
uuid3 = forge.generate("order:2024:Q1:12345")
```

### From Dictionaries

```python
# User data
user_data = {
    "email": "john@example.com",
    "username": "john_doe",
    "department": "engineering"
}
user_uuid = forge.generate(user_data)

# Order data
order_data = {
    "customer_id": "12345",
    "product_id": "67890",
    "timestamp": "2024-01-15T10:30:00Z"
}
order_uuid = forge.generate(order_data)
```

### From Objects

```python
class User:
    def __init__(self, email, name):
        self.email = email
        self.name = name

    def __str__(self):
        return f"{self.email}:{self.name}"

user = User("john@example.com", "John Doe")
user_uuid = forge.generate(user)
```

## Different Output Formats

```python
# Default hex format with dashes
uuid_hex = forge.generate("test", format="hex")
# Output: 550e8400-e29b-41d4-a716-446655440000

# URN format
uuid_urn = forge.generate("test", format="urn")
# Output: urn:uuid:550e8400-e29b-41d4-a716-446655440000

# Raw bytes
uuid_bytes = forge.generate("test", format="bytes")
# Output: b'U\x0e\x84\x00\xe2\x9b...'

# Hex without dashes
uuid_plain = forge.generate("test", format="hex", separator="")
# Output: 550e8400e29b41d4a716446655440000
```

## Using Different Namespaces

```python
# Different namespaces produce different UUIDs for same input
forge_users = UUIDForge(namespace="users")
forge_orders = UUIDForge(namespace="orders")

user_uuid = forge_users.generate("john@example.com")
order_uuid = forge_orders.generate("john@example.com")

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

uuids = [forge.generate(email) for email in emails]

# Or with custom namespace per UUID
namespaces = ["users", "admins", "guests"]
uuids = [
    UUIDForge(namespace=ns).generate(email)
    for ns, email in zip(namespaces, emails)
]
```

## Working with Existing UUIDs

```python
import uuid

# Convert existing UUID to different format
existing_uuid = uuid.uuid4()
uuid_string = str(existing_uuid)

# Regenerate deterministically
regenerated = forge.generate(uuid_string)
```

## Error Handling

```python
try:
    # This will work
    valid_uuid = forge.generate("valid_input")

    # This might raise an exception
    invalid_uuid = forge.generate(None)

except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Validation

```python
import uuid

# Validate generated UUID
generated = forge.generate("test")

# Check if it's a valid UUID
try:
    parsed = uuid.UUID(generated)
    print(f"Valid UUID: {parsed}")
except ValueError:
    print("Invalid UUID generated")
```

## Next Steps

- [Advanced Usage](advanced-usage.md) - Explore advanced features and customization
- [CLI Reference](cli.md) - Learn about command-line usage
- [Best Practices](best-practices.md) - Optimize your UUID generation patterns
