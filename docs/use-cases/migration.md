# Data Migration with UUID-Forge

Learn how to use deterministic UUIDs for seamless data migration across systems, databases, and platforms.

## Overview

Data migration often involves moving data between different systems while maintaining referential integrity and consistency. UUID-Forge's deterministic generation ensures that the same entities receive the same UUIDs across different environments and migration phases.

## Migration Challenges

### Traditional Migration Problems

- **ID Mapping**: Translating IDs between different systems
- **Referential Integrity**: Maintaining relationships during migration
- **Incremental Migration**: Handling partial migrations over time
- **Rollback Scenarios**: Reverting migrations safely
- **Cross-System Consistency**: Ensuring same entity has same ID everywhere

### UUID-Forge Solutions

- **Deterministic IDs**: Same input always generates same UUID
- **No ID Mapping Required**: UUIDs are consistent across systems
- **Referential Integrity Maintained**: Related entities get related UUIDs
- **Idempotent Migration**: Running migration multiple times is safe
- **Cross-Platform Consistency**: Same UUIDs on any system

## Migration Patterns

### Database-to-Database Migration

#### Legacy System to Modern Database

```python
from uuid_forge import UUIDGenerator
import psycopg2
import sqlite3

class DatabaseMigrator:
    def __init__(self):
        # Generators for different entity types
        self.user_gen = UUIDGenerator(namespace="users")
        self.order_gen = UUIDGenerator(namespace="orders")
        self.product_gen = UUIDGenerator(namespace="products")

        # Database connections
        self.legacy_db = sqlite3.connect("legacy.db")
        self.modern_db = psycopg2.connect("postgresql://...")

    def migrate_users(self):
        """Migrate users from legacy SQLite to PostgreSQL"""
        legacy_cursor = self.legacy_db.cursor()
        modern_cursor = self.modern_db.cursor()

        # Read from legacy database
        legacy_cursor.execute("SELECT email, name, created_at FROM users")
        legacy_users = legacy_cursor.fetchall()

        for email, name, created_at in legacy_users:
            # Generate deterministic UUID for user
            user_uuid = self.user_gen.generate(email)

            # Insert into modern database
            modern_cursor.execute(
                "INSERT INTO users (id, email, name, created_at) VALUES (%s, %s, %s, %s)",
                (user_uuid, email, name, created_at)
            )

        self.modern_db.commit()
        print(f"Migrated {len(legacy_users)} users")

    def migrate_orders(self):
        """Migrate orders maintaining user relationships"""
        legacy_cursor = self.legacy_db.cursor()
        modern_cursor = self.modern_db.cursor()

        # Read orders with user email for UUID generation
        legacy_cursor.execute("""
            SELECT o.id, u.email, o.total, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
        """)
        legacy_orders = legacy_cursor.fetchall()

        for legacy_order_id, user_email, total, created_at in legacy_orders:
            # Generate consistent UUIDs
            user_uuid = self.user_gen.generate(user_email)

            # Generate order UUID from user and legacy order data
            order_data = {
                "user_email": user_email,
                "legacy_id": legacy_order_id,
                "total": total,
                "created_at": created_at
            }
            order_uuid = self.order_gen.generate(order_data)

            # Insert into modern database
            modern_cursor.execute(
                "INSERT INTO orders (id, user_id, total, created_at) VALUES (%s, %s, %s, %s)",
                (order_uuid, user_uuid, total, created_at)
            )

        self.modern_db.commit()
        print(f"Migrated {len(legacy_orders)} orders")
```

### NoSQL to SQL Migration

```python
from pymongo import MongoClient
import psycopg2
from uuid_forge import UUIDGenerator

class NoSQLToSQLMigrator:
    def __init__(self):
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client.legacy_app

        self.postgres_conn = psycopg2.connect("postgresql://...")

        # UUID generators
        self.user_gen = UUIDGenerator(namespace="users")
        self.post_gen = UUIDGenerator(namespace="posts")
        self.comment_gen = UUIDGenerator(namespace="comments")

    def migrate_user_posts(self):
        """Migrate nested document structure to relational tables"""
        cursor = self.postgres_conn.cursor()

        # Read MongoDB documents
        for user_doc in self.mongo_db.users.find():
            user_email = user_doc["email"]
            user_uuid = self.user_gen.generate(user_email)

            # Migrate user
            cursor.execute(
                "INSERT INTO users (id, email, name) VALUES (%s, %s, %s)",
                (user_uuid, user_doc["email"], user_doc["name"])
            )

            # Migrate embedded posts
            for post in user_doc.get("posts", []):
                post_data = {
                    "user_email": user_email,
                    "title": post["title"],
                    "content": post["content"],
                    "created_at": post["created_at"].isoformat()
                }
                post_uuid = self.post_gen.generate(post_data)

                cursor.execute(
                    "INSERT INTO posts (id, user_id, title, content, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (post_uuid, user_uuid, post["title"], post["content"], post["created_at"])
                )

                # Migrate embedded comments
                for comment in post.get("comments", []):
                    comment_data = {
                        "post_id": post_uuid,
                        "author": comment["author"],
                        "content": comment["content"],
                        "created_at": comment["created_at"].isoformat()
                    }
                    comment_uuid = self.comment_gen.generate(comment_data)

                    cursor.execute(
                        "INSERT INTO comments (id, post_id, author, content, created_at) VALUES (%s, %s, %s, %s, %s)",
                        (comment_uuid, post_uuid, comment["author"], comment["content"], comment["created_at"])
                    )

        self.postgres_conn.commit()
```

## Cloud Migration

### On-Premises to Cloud Migration

```python
import boto3
from uuid_forge import UUIDGenerator

class CloudMigrator:
    def __init__(self):
        # Local database connection
        self.local_db = psycopg2.connect("postgresql://localhost/app")

        # AWS services
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.s3 = boto3.client('s3')

        # UUID generators
        self.user_gen = UUIDGenerator(namespace="cloud-users")
        self.file_gen = UUIDGenerator(namespace="cloud-files")

    def migrate_to_dynamodb(self):
        """Migrate relational data to DynamoDB"""
        cursor = self.local_db.cursor()
        table = self.dynamodb.Table('Users')

        cursor.execute("SELECT email, name, profile_data FROM users")

        for email, name, profile_data in cursor.fetchall():
            user_uuid = self.user_gen.generate(email)

            # Store in DynamoDB with UUID as partition key
            table.put_item(
                Item={
                    'user_id': user_uuid,
                    'email': email,
                    'name': name,
                    'profile_data': profile_data,
                    'migrated_at': datetime.utcnow().isoformat()
                }
            )

    def migrate_files_to_s3(self):
        """Migrate files to S3 with deterministic keys"""
        cursor = self.local_db.cursor()

        cursor.execute("SELECT file_path, metadata, content FROM files")

        for file_path, metadata, content in cursor.fetchall():
            # Generate deterministic S3 key
            file_data = {
                "original_path": file_path,
                "size": len(content),
                "metadata": metadata
            }
            file_uuid = self.file_gen.generate(file_data)
            s3_key = f"migrated-files/{file_uuid}"

            # Upload to S3
            self.s3.put_object(
                Bucket='migration-bucket',
                Key=s3_key,
                Body=content,
                Metadata={
                    'original-path': file_path,
                    'file-uuid': file_uuid,
                    **metadata
                }
            )
```

## Incremental Migration

### Phased Migration Strategy

```python
class IncrementalMigrator:
    def __init__(self):
        self.source_db = psycopg2.connect("postgresql://source/")
        self.target_db = psycopg2.connect("postgresql://target/")

        self.user_gen = UUIDGenerator(namespace="incremental-users")

        # Track migration progress
        self.migration_state = {
            "last_migrated_id": 0,
            "batch_size": 1000,
            "total_migrated": 0
        }

    def migrate_batch(self):
        """Migrate a batch of records"""
        source_cursor = self.source_db.cursor()
        target_cursor = self.target_db.cursor()

        # Get next batch
        source_cursor.execute(
            "SELECT id, email, name FROM users WHERE id > %s ORDER BY id LIMIT %s",
            (self.migration_state["last_migrated_id"], self.migration_state["batch_size"])
        )

        batch = source_cursor.fetchall()
        if not batch:
            print("Migration complete!")
            return False

        # Migrate batch with deterministic UUIDs
        for source_id, email, name in batch:
            user_uuid = self.user_gen.generate(email)

            # Use ON CONFLICT for idempotent migration
            target_cursor.execute(
                """
                INSERT INTO users (id, email, name, source_id, migrated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    name = EXCLUDED.name,
                    migrated_at = EXCLUDED.migrated_at
                """,
                (user_uuid, email, name, source_id, datetime.utcnow())
            )

            self.migration_state["last_migrated_id"] = source_id

        self.target_db.commit()
        self.migration_state["total_migrated"] += len(batch)

        print(f"Migrated batch: {len(batch)} records, Total: {self.migration_state['total_migrated']}")
        return True

    def run_incremental_migration(self):
        """Run migration in batches"""
        while self.migrate_batch():
            time.sleep(1)  # Brief pause between batches
```

## Data Synchronization

### Bidirectional Sync

```python
class DataSynchronizer:
    def __init__(self):
        self.system_a = psycopg2.connect("postgresql://system-a/")
        self.system_b = psycopg2.connect("postgresql://system-b/")

        self.user_gen = UUIDGenerator(namespace="sync-users")
        self.sync_log = []

    def sync_user_changes(self):
        """Synchronize user changes between systems"""
        cursor_a = self.system_a.cursor()
        cursor_b = self.system_b.cursor()

        # Get changes from system A
        cursor_a.execute(
            "SELECT email, name, updated_at FROM users WHERE updated_at > %s",
            (self.last_sync_time,)
        )

        changes_a = cursor_a.fetchall()

        for email, name, updated_at in changes_a:
            user_uuid = self.user_gen.generate(email)

            # Apply change to system B
            cursor_b.execute(
                """
                INSERT INTO users (id, email, name, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    updated_at = EXCLUDED.updated_at
                WHERE users.updated_at < EXCLUDED.updated_at
                """,
                (user_uuid, email, name, updated_at)
            )

            self.sync_log.append({
                "user_id": user_uuid,
                "direction": "A->B",
                "timestamp": datetime.utcnow()
            })

        self.system_b.commit()
```

## Migration Validation

### Data Integrity Verification

```python
class MigrationValidator:
    def __init__(self):
        self.source_db = psycopg2.connect("postgresql://source/")
        self.target_db = psycopg2.connect("postgresql://target/")

        self.user_gen = UUIDGenerator(namespace="validation-users")

    def validate_user_migration(self):
        """Validate that all users migrated correctly"""
        source_cursor = self.source_db.cursor()
        target_cursor = self.target_db.cursor()

        source_cursor.execute("SELECT email, name FROM users ORDER BY email")
        source_users = source_cursor.fetchall()

        target_cursor.execute("SELECT email, name FROM users ORDER BY email")
        target_users = target_cursor.fetchall()

        validation_results = {
            "total_source": len(source_users),
            "total_target": len(target_users),
            "missing_users": [],
            "data_mismatches": []
        }

        source_dict = {email: name for email, name in source_users}
        target_dict = {email: name for email, name in target_users}

        # Check for missing users
        for email in source_dict:
            if email not in target_dict:
                validation_results["missing_users"].append(email)
            elif source_dict[email] != target_dict[email]:
                validation_results["data_mismatches"].append({
                    "email": email,
                    "source_name": source_dict[email],
                    "target_name": target_dict[email]
                })

        return validation_results

    def validate_referential_integrity(self):
        """Validate that relationships are maintained"""
        target_cursor = self.target_db.cursor()

        # Check that all orders have valid user references
        target_cursor.execute("""
            SELECT COUNT(*) FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE u.id IS NULL
        """)

        orphaned_orders = target_cursor.fetchone()[0]

        return {
            "orphaned_orders": orphaned_orders,
            "integrity_valid": orphaned_orders == 0
        }
```

## Rollback Strategies

### Safe Migration Rollback

```python
class MigrationRollback:
    def __init__(self):
        self.target_db = psycopg2.connect("postgresql://target/")
        self.backup_db = psycopg2.connect("postgresql://backup/")

    def create_rollback_point(self):
        """Create a rollback point before migration"""
        target_cursor = self.target_db.cursor()
        backup_cursor = self.backup_db.cursor()

        # Backup current state
        target_cursor.execute("SELECT * FROM users")
        users = target_cursor.fetchall()

        # Clear backup and restore
        backup_cursor.execute("DELETE FROM users")

        for user in users:
            backup_cursor.execute(
                "INSERT INTO users VALUES (%s, %s, %s, %s)",
                user
            )

        self.backup_db.commit()
        print("Rollback point created")

    def rollback_migration(self):
        """Rollback to previous state"""
        target_cursor = self.target_db.cursor()
        backup_cursor = self.backup_db.cursor()

        # Clear target
        target_cursor.execute("DELETE FROM users")

        # Restore from backup
        backup_cursor.execute("SELECT * FROM users")
        backup_users = backup_cursor.fetchall()

        for user in backup_users:
            target_cursor.execute(
                "INSERT INTO users VALUES (%s, %s, %s, %s)",
                user
            )

        self.target_db.commit()
        print("Migration rolled back successfully")
```

## Migration Monitoring

### Progress Tracking

```python
class MigrationMonitor:
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "records_processed": 0,
            "records_failed": 0,
            "current_phase": None,
            "estimated_completion": None
        }

    def start_monitoring(self, total_records):
        """Start migration monitoring"""
        self.metrics["start_time"] = datetime.utcnow()
        self.metrics["total_records"] = total_records
        print(f"Migration started: {total_records} records to process")

    def update_progress(self, records_processed, current_phase="processing"):
        """Update migration progress"""
        self.metrics["records_processed"] = records_processed
        self.metrics["current_phase"] = current_phase

        elapsed = datetime.utcnow() - self.metrics["start_time"]
        progress_pct = (records_processed / self.metrics["total_records"]) * 100

        if records_processed > 0:
            avg_time_per_record = elapsed / records_processed
            remaining_records = self.metrics["total_records"] - records_processed
            eta = datetime.utcnow() + (avg_time_per_record * remaining_records)
            self.metrics["estimated_completion"] = eta

        print(f"Progress: {progress_pct:.1f}% ({records_processed}/{self.metrics['total_records']}) - ETA: {eta}")

    def log_error(self, record_id, error):
        """Log migration error"""
        self.metrics["records_failed"] += 1
        print(f"Error processing record {record_id}: {error}")

    def complete_monitoring(self):
        """Complete migration monitoring"""
        total_time = datetime.utcnow() - self.metrics["start_time"]
        success_rate = ((self.metrics["records_processed"] - self.metrics["records_failed"]) /
                       self.metrics["total_records"]) * 100

        print(f"Migration completed in {total_time}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Records processed: {self.metrics['records_processed']}")
        print(f"Records failed: {self.metrics['records_failed']}")
```

## Next Steps

- [Testing Use Case](testing.md) - Testing migration strategies
- [Best Practices](../guide/best-practices.md) - Migration optimization
- [Development Guide](../development/setup.md) - Development environment setup
