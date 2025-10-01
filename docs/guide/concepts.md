# Core Concepts

Understanding the core concepts behind UUID-Forge will help you use it effectively in your applications.

## What are UUIDs?

UUIDs (Universally Unique Identifiers) are 128-bit values used to uniquely identify information in computer systems. They are designed to be unique across space and time without requiring a central authority.

## Deterministic Generation

UUID-Forge specializes in **deterministic UUID generation**, meaning that given the same input, it will always produce the same UUID. This is crucial for:

- **Cross-system coordination**: Different services can generate the same UUID for the same entity
- **Data consistency**: Ensures referential integrity across distributed systems
- **Testing**: Predictable UUIDs make testing easier and more reliable
- **Migration**: Consistent UUIDs during data migration and transformation

## UUID Versions

UUID-Forge supports multiple UUID versions:

### Version 3 (MD5 Hash)

- Uses MD5 hashing algorithm
- Deterministic based on namespace and name
- Legacy support (MD5 is considered weak)

### Version 4 (Random)

- Randomly generated
- Not deterministic by nature
- Highest entropy

### Version 5 (SHA-1 Hash)

- Uses SHA-1 hashing algorithm
- Deterministic based on namespace and name
- **Recommended** for most deterministic use cases

## Namespaces

Namespaces are used to create logical groupings of UUIDs. They ensure that:

- UUIDs generated with different namespaces are unique
- Same name in different namespaces produces different UUIDs
- Hierarchical organization of UUID generation

### Standard Namespaces

UUID-Forge provides several predefined namespaces:

- `DNS`: For domain names
- `URL`: For URLs
- `OID`: For ISO OIDs
- `X500`: For X.500 Distinguished Names

### Custom Namespaces

You can define custom namespaces for your application:

```python
from uuid_forge import UUIDGenerator
import uuid

# Create a custom namespace for your application
my_namespace = uuid.uuid4()
forge = UUIDGenerator(namespace=my_namespace)
```

## Input Processing

UUID-Forge can process various input types:

- **Strings**: Text data, identifiers, names
- **Dictionaries**: Structured data converted to canonical form
- **Objects**: Any object with string representation
- **Binary data**: Raw bytes

## Determinism Guarantees

UUID-Forge guarantees that:

1. Same input → Same UUID (within same namespace and configuration)
2. Different input → Different UUID (with high probability)
3. Cross-platform consistency (same UUID on different systems)
4. Version consistency (same UUID across UUID-Forge versions)

## Next Steps

- [Basic Usage](basic-usage.md) - Learn how to generate your first UUIDs
- [Advanced Usage](advanced-usage.md) - Explore advanced features
- [Best Practices](best-practices.md) - Learn optimal usage patterns
