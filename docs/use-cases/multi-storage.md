# Multi-Storage Systems

Learn how UUID-Forge ensures consistency across different storage systems and databases.

## Overview

In modern applications, data often spans multiple storage systems - SQL databases, NoSQL stores, message queues, caches, and file systems. UUID-Forge provides deterministic UUID generation to maintain consistent entity identification across all these systems.

## Common Challenges

### Storage System Inconsistencies

Different storage systems may handle UUIDs differently:

- **SQL databases**: Native UUID columns with specific formatting
- **NoSQL stores**: String or binary UUID representations
- **Message queues**: UUID as message correlation IDs
- **Caches**: UUID as cache keys
- **File systems**: UUID in filenames or directory structures

### Synchronization Issues

Traditional approaches face challenges:

- **Database sequences**: Not available across all systems
- **Auto-generated UUIDs**: Different for same entity
- **Centralized ID generation**: Single point of failure
- **Manual coordination**: Error-prone and complex

## UUID-Forge Solution

### Deterministic Generation

Same input always produces the same UUID:

```python
from uuid_forge import UUIDGenerator

# Initialize generator
generator = UUIDGenerator(namespace="users")

# Same UUID across all storage systems
user_email = "john@example.com"
user_uuid = generator.generate(user_email)

# Use in SQL database
sql_insert = f"INSERT INTO users (id, email) VALUES ('{user_uuid}', '{user_email}')"

# Use in MongoDB
mongo_doc = {"_id": user_uuid, "email": user_email}

# Use as Redis key
redis_key = f"user:{user_uuid}"
```

## Implementation Patterns

### Database Integration

#### PostgreSQL with UUID Column

```python
import psycopg2
from uuid_forge import UUIDGenerator

class UserRepository:
    def __init__(self):
        self.generator = UUIDGenerator(namespace="users")
        self.conn = psycopg2.connect("postgresql://...")

    def create_user(self, email, name):
        user_id = self.generator.generate(email)

        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (id, email, name) VALUES (%s, %s, %s)",
                (user_id, email, name)
            )

        return user_id

    def get_user_id(self, email):
        """Get consistent user ID without database lookup"""
        return self.generator.generate(email)
```

#### MongoDB Integration

```python
from pymongo import MongoClient
from uuid_forge import UUIDGenerator

class DocumentStore:
    def __init__(self):
        self.generator = UUIDGenerator(namespace="documents")
        self.client = MongoClient("mongodb://...")
        self.db = self.client.myapp

    def store_document(self, content, metadata):
        doc_data = {
            "content": content,
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }

        # Generate deterministic ID from content and metadata
        doc_id = self.generator.generate(doc_data)

        # Store in MongoDB
        self.db.documents.insert_one({
            "_id": doc_id,
            **doc_data
        })

        return doc_id
```

### Cache Integration

#### Redis Caching

```python
import redis
from uuid_forge import UUIDGenerator

class CacheManager:
    def __init__(self):
        self.user_generator = UUIDGenerator(namespace="users")
        self.session_generator = UUIDGenerator(namespace="sessions")
        self.redis = redis.Redis(host="localhost", port=6379)

    def cache_user_data(self, email, user_data):
        user_id = self.user_generator.generate(email)
        cache_key = f"user:{user_id}"

        # Store in Redis with deterministic key
        self.redis.setex(cache_key, 3600, json.dumps(user_data))

        return cache_key

    def get_cached_user(self, email):
        user_id = self.user_generator.generate(email)
        cache_key = f"user:{user_id}"

        cached_data = self.redis.get(cache_key)
        return json.loads(cached_data) if cached_data else None
```

### Message Queue Integration

#### RabbitMQ with Correlation IDs

```python
import pika
from uuid_forge import UUIDGenerator

class MessagePublisher:
    def __init__(self):
        self.message_generator = UUIDGenerator(namespace="messages")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()

    def publish_user_event(self, user_email, event_type, event_data):
        # Generate deterministic correlation ID
        correlation_data = {
            "user_email": user_email,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        correlation_id = self.message_generator.generate(correlation_data)

        message = {
            "correlation_id": correlation_id,
            "user_email": user_email,
            "event_type": event_type,
            "data": event_data
        }

        self.channel.basic_publish(
            exchange="user_events",
            routing_key=event_type,
            body=json.dumps(message),
            properties=pika.BasicProperties(correlation_id=correlation_id)
        )

        return correlation_id
```

## Cross-System Consistency Examples

### E-commerce Order Processing

```python
class OrderProcessingSystem:
    def __init__(self):
        self.user_gen = UUIDGenerator(namespace="users")
        self.order_gen = UUIDGenerator(namespace="orders")
        self.product_gen = UUIDGenerator(namespace="products")

        # Multiple storage systems
        self.postgres = psycopg2.connect("postgresql://...")
        self.redis = redis.Redis()
        self.mongo = MongoClient()
        self.es = Elasticsearch()

    def process_order(self, user_email, product_skus, quantities):
        # Generate consistent IDs
        user_id = self.user_gen.generate(user_email)

        order_items = []
        for sku, qty in zip(product_skus, quantities):
            product_id = self.product_gen.generate(sku)
            order_items.append({
                "product_id": product_id,
                "sku": sku,
                "quantity": qty
            })

        order_data = {
            "user_id": user_id,
            "items": sorted(order_items, key=lambda x: x["sku"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        order_id = self.order_gen.generate(order_data)

        # Store in PostgreSQL (transactional data)
        with self.postgres.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (id, user_id, status, created_at) VALUES (%s, %s, %s, %s)",
                (order_id, user_id, "pending", datetime.utcnow())
            )

            for item in order_items:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, item["product_id"], item["quantity"])
                )

        # Cache in Redis (fast access)
        self.redis.setex(
            f"order:{order_id}",
            3600,
            json.dumps(order_data)
        )

        # Store in MongoDB (document store)
        self.mongo.orders.insert_one({
            "_id": order_id,
            **order_data
        })

        # Index in Elasticsearch (search)
        self.es.index(
            index="orders",
            id=order_id,
            body={
                **order_data,
                "searchable_text": f"{user_email} {' '.join(product_skus)}"
            }
        )

        return order_id
```

### File System Integration

```python
import os
from pathlib import Path
from uuid_forge import UUIDGenerator

class FileManager:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.file_generator = UUIDGenerator(namespace="files")

    def store_file(self, content, metadata):
        # Generate deterministic file UUID
        file_data = {
            "content_hash": hashlib.md5(content).hexdigest(),
            "metadata": metadata,
            "size": len(content)
        }
        file_uuid = self.file_generator.generate(file_data)

        # Create directory structure using UUID segments
        dir_path = self.base_path / file_uuid[:2] / file_uuid[2:4]
        dir_path.mkdir(parents=True, exist_ok=True)

        # Store file with UUID name
        file_path = dir_path / f"{file_uuid}.dat"
        with open(file_path, "wb") as f:
            f.write(content)

        # Store metadata in database with same UUID
        self.store_metadata_in_db(file_uuid, metadata, str(file_path))

        return file_uuid

    def get_file_path(self, content, metadata):
        """Get file path without creating file"""
        file_data = {
            "content_hash": hashlib.md5(content).hexdigest(),
            "metadata": metadata,
            "size": len(content)
        }
        file_uuid = self.file_generator.generate(file_data)

        return self.base_path / file_uuid[:2] / file_uuid[2:4] / f"{file_uuid}.dat"
```

## Testing Multi-Storage Consistency

### Integration Testing

```python
import pytest
from uuid_forge import UUIDGenerator

class TestMultiStorageConsistency:
    def setUp(self):
        self.user_gen = UUIDGenerator(namespace="test-users")
        self.order_gen = UUIDGenerator(namespace="test-orders")

        # Initialize test storage systems
        self.setup_test_databases()

    def test_user_id_consistency(self):
        """Test user ID consistency across all storage systems"""
        email = "test@example.com"

        # Generate UUID from different components
        user_id_1 = self.user_gen.generate(email)
        user_id_2 = self.get_user_id_from_postgres(email)
        user_id_3 = self.get_user_id_from_cache(email)
        user_id_4 = self.get_user_id_from_mongo(email)

        # All should be identical
        assert user_id_1 == user_id_2 == user_id_3 == user_id_4

    def test_cross_system_query(self):
        """Test querying data across multiple systems using consistent UUIDs"""
        email = "customer@example.com"
        user_id = self.user_gen.generate(email)

        # Store user in different systems
        self.store_user_in_postgres(user_id, email)
        self.cache_user_in_redis(user_id, {"name": "Test User"})
        self.index_user_in_elasticsearch(user_id, email)

        # Query from different systems using same UUID
        pg_user = self.get_user_from_postgres(user_id)
        cached_user = self.get_user_from_cache(user_id)
        indexed_user = self.search_user_in_elasticsearch(user_id)

        # Verify data consistency
        assert pg_user["id"] == cached_user["id"] == indexed_user["id"] == user_id
```

## Monitoring and Debugging

### UUID Consistency Validation

```python
class ConsistencyValidator:
    def __init__(self):
        self.generators = {
            "users": UUIDGenerator(namespace="users"),
            "orders": UUIDGenerator(namespace="orders"),
            "products": UUIDGenerator(namespace="products")
        }

    def validate_storage_consistency(self, entity_type, identifier):
        """Validate UUID consistency across storage systems"""
        expected_uuid = self.generators[entity_type].generate(identifier)

        results = {
            "postgres": self.get_uuid_from_postgres(entity_type, identifier),
            "redis": self.get_uuid_from_redis(entity_type, identifier),
            "mongodb": self.get_uuid_from_mongodb(entity_type, identifier),
            "elasticsearch": self.get_uuid_from_elasticsearch(entity_type, identifier)
        }

        inconsistencies = []
        for system, uuid_value in results.items():
            if uuid_value != expected_uuid:
                inconsistencies.append({
                    "system": system,
                    "expected": expected_uuid,
                    "actual": uuid_value
                })

        return {
            "consistent": len(inconsistencies) == 0,
            "expected_uuid": expected_uuid,
            "inconsistencies": inconsistencies
        }
```

## Next Steps

- [Testing Use Case](testing.md) - Testing strategies with consistent UUIDs
- [Migration Use Case](migration.md) - Data migration patterns
- [Best Practices](../guide/best-practices.md) - Optimization and patterns
