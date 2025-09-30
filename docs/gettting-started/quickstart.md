# Quick Start Guide

This guide will get you up and running with UUID-Forge in under 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Basic understanding of UUIDs
- A text editor or IDE

## Step 1: Installation

Install UUID-Forge using your preferred package manager:

=== "uv (recommended)"

    ```bash
    uv add uuid-forge
    ```

=== "pip"

    ```bash
    pip install uuid-forge
    ```

=== "poetry"

    ```bash
    poetry add uuid-forge
    ```

## Step 2: Generate a Salt

Security first! Generate a cryptographic salt for production use:

```bash
uuid-forge new-salt
```

This will output something like:

```
xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB
```

!!! warning "Keep This Secret!"
    Store this salt securely and never commit it to version control.

### Set Environment Variable

Add the salt to your environment:

```bash
export UUID_FORGE_SALT='xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB'
```

Or create a `.env` file:

```bash
uuid-forge init
```

This creates a `.env` file with a generated salt and usage instructions.

## Step 3: Your First UUID

Create a Python file `example.py`:

```python
from uuid_forge import generate_uuid_only, load_config_from_env

# Load configuration from environment
config = load_config_from_env()

# Generate a deterministic UUID for an invoice
invoice_uuid = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    invoice_number=12345
)

print(f"Invoice UUID: {invoice_uuid}")
```

Run it:

```bash
python example.py
```

Output:

```
Invoice UUID: 550e8400-e29b-41d4-a716-446655440000
```

## Step 4: Verify Idempotency

The magic of UUID-Forge is that the same inputs always produce the same UUID. Add this to your script:

```python
# Regenerate the UUID from the same business data
regenerated_uuid = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    invoice_number=12345
)

# They're identical!
assert invoice_uuid == regenerated_uuid
print("✓ UUIDs are identical!")
```

Run again:

```bash
python example.py
```

Output:

```
Invoice UUID: 550e8400-e29b-41d4-a716-446655440000
✓ UUIDs are identical!
```

## Step 5: Use Across Systems

Now use this UUID consistently across all your storage systems:

```python
import psycopg2
import boto3
import redis

# Database - Primary key
db = psycopg2.connect("...")
cursor = db.cursor()
cursor.execute(
    "INSERT INTO invoices (id, region, number, amount) VALUES (%s, %s, %s, %s)",
    (invoice_uuid, "EUR", 12345, 1500.50)
)

# S3 - Object storage
s3 = boto3.client('s3')
s3.put_object(
    Bucket='invoices',
    Key=f'invoices/2024/EUR/{invoice_uuid}.pdf',
    Body=pdf_data
)

# Redis - Cache
r = redis.Redis()
r.setex(
    f'invoice:{invoice_uuid}',
    3600,  # 1 hour TTL
    json.dumps({'region': 'EUR', 'number': 12345})
)

print(f"✓ Stored invoice {invoice_uuid} in Postgres, S3, and Redis")
```

## Step 6: Retrieve Without Lookups

The real power: retrieve from any system without database lookups!

```python
# User requests invoice by business data
requested_region = "EUR"
requested_number = 12345

# Regenerate UUID from business data (no database query!)
lookup_uuid = generate_uuid_only(
    "invoice",
    config=config,
    region=requested_region,
    invoice_number=requested_number
)

# Now access any storage system directly
pdf_data = s3.get_object(
    Bucket='invoices',
    Key=f'invoices/2024/EUR/{lookup_uuid}.pdf'
)

cached_data = r.get(f'invoice:{lookup_uuid}')

db_record = cursor.execute(
    "SELECT * FROM invoices WHERE id = %s",
    (lookup_uuid,)
).fetchone()

print("✓ Retrieved from all systems without any UUID lookups!")
```

## Common Patterns

### Pattern 1: With Prefixes for Human Readability

```python
from uuid_forge import generate_uuid_with_prefix

# Generate with prefix
prefixed_id = generate_uuid_with_prefix(
    "invoice",
    prefix="INV-EUR",
    config=config,
    region="EUR",
    invoice_number=12345
)

print(prefixed_id)
# Output: INV-EUR-550e8400-e29b-41d4-a716-446655440000
```

### Pattern 2: Using the OO API

```python
from uuid_forge import UUIDGenerator

# Create generator once
generator = UUIDGenerator(config=config)

# Generate multiple UUIDs
order_uuid = generator.generate("order", order_number=123)
invoice_uuid = generator.generate("invoice", order_id=str(order_uuid))
shipment_uuid = generator.generate("shipment", order_id=str(order_uuid))
```

### Pattern 3: Different Entity Types

```python
# Each entity type has its own UUID space
user_uuid = generate_uuid_only("user", config=config, email="alice@example.com")
order_uuid = generate_uuid_only("order", config=config, user_id=str(user_uuid), number=123)
invoice_uuid = generate_uuid_only("invoice", config=config, order_id=str(order_uuid))

# Same business data, different entity types = different UUIDs
assert user_uuid != order_uuid != invoice_uuid
```

## CLI Usage

UUID-Forge includes a powerful CLI for quick UUID generation:

```bash
# Generate UUID
uuid-forge generate invoice --attr region=EUR --attr number=12345

# With prefix
uuid-forge generate invoice --prefix INV-EUR --attr region=EUR --attr number=12345

# Extract UUID from prefixed ID
uuid-forge extract "INV-EUR-550e8400-e29b-41d4-a716-446655440000"

# Validate configuration
uuid-forge validate

# Show current configuration
uuid-forge info
```

## Next Steps

Now that you've got the basics, explore:

- [Core Concepts](../guide/concepts.md) - Understand how it works
- [Best Practices](../guide/best-practices.md) - Production guidelines
- [Use Cases](../use-cases/microservices.md) - Real-world examples
- [API Reference](../api/core.md) - Complete documentation

## Troubleshooting

### Issue: "No salt configured" warning

**Solution**: Set the `UUID_FORGE_SALT` environment variable or use `uuid-forge init` to create a config file.

### Issue: Different UUIDs on different machines

**Solution**: Ensure all machines use the same salt and namespace configuration.

### Issue: UUIDs change after restart

**Solution**: Verify environment variables are set correctly and persistently.

## Get Help

- [GitHub Issues](https://github.com/yourusername/uuid-forge/issues)
- [GitHub Discussions](https://github.com/yourusername/uuid-forge/discussions)
- [API Reference](../api/core.md)
