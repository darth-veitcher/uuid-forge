# Testing with UUID-Forge

Learn how to leverage deterministic UUIDs for more effective testing strategies.

## Overview

Deterministic UUID generation provides significant advantages for testing by making UUIDs predictable and reproducible. This enables more reliable tests, easier debugging, and better test data management.

## Benefits for Testing

### Predictable Test Data

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

def test_user_creation():
    """Test with predictable UUIDs"""
    config = IDConfig(namespace=Namespace("test.example.com"), salt="test-v1")
    generator = UUIDGenerator(config)

    # Always generates the same UUID for same input
    user_id = generator.generate("user", email="test@example.com")

    # Test assertions can verify UUID properties
    assert isinstance(user_id, UUID)
    assert str(user_id)  # Can convert to string

    # Deterministic - same input always produces same UUID
    user_id_2 = generator.generate("user", email="test@example.com")
    assert user_id == user_id_2
```

### Reproducible Test Scenarios

```python
import pytest
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestOrderProcessing:
    def setUp(self):
        user_config = IDConfig(namespace=Namespace("test.example.com/users"), salt="test-v1")
        order_config = IDConfig(namespace=Namespace("test.example.com/orders"), salt="test-v1")

        self.user_gen = UUIDGenerator(user_config)
        self.order_gen = UUIDGenerator(order_config)

    def test_order_workflow(self):
        """Test complete order workflow with predictable UUIDs"""
        # Same UUIDs generated every test run
        user_id = self.user_gen.generate("user", email="customer@test.com")

        order_id = self.order_gen.generate(
            "order",
            user_id=str(user_id),
            item1="product1",
            item2="product2",
            timestamp="2024-01-15T10:00:00Z"
        )

        # Test can rely on deterministic UUID generation
        # Same inputs always produce same UUIDs
        expected_user_id = self.user_gen.generate("user", email="customer@test.com")
        assert user_id == expected_user_id

        expected_order_id = self.order_gen.generate(
            "order",
            user_id=str(user_id),
            item1="product1",
            item2="product2",
            timestamp="2024-01-15T10:00:00Z"
        )
        assert order_id == expected_order_id
```

## Test Data Management

### Fixture-Based Testing

```python
import pytest
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID
from typing import Dict

@pytest.fixture
def test_generators() -> Dict[str, UUIDGenerator]:
    """Provide test UUID generators"""
    return {
        "users": UUIDGenerator(
            IDConfig(namespace=Namespace("test.example.com/users"), salt="test-v1")
        ),
        "orders": UUIDGenerator(
            IDConfig(namespace=Namespace("test.example.com/orders"), salt="test-v1")
        ),
        "products": UUIDGenerator(
            IDConfig(namespace=Namespace("test.example.com/products"), salt="test-v1")
        ),
    }

@pytest.fixture
def test_users(test_generators):
    """Generate test user data with deterministic UUIDs"""
    users = [
        {"email": "user1@test.com", "name": "User One", "region": "us"},
        {"email": "user2@test.com", "name": "User Two", "region": "eu"},
        {"email": "user3@test.com", "name": "User Three", "region": "asia"},
    ]

    for user in users:
        user["id"] = test_generators["users"].generate(
            "user",
            email=user["email"],
            region=user["region"]
        )

    return users

def test_user_processing(test_users):
    """Test using predictable user data"""
    assert len(test_users) == 3
    assert all(isinstance(user["id"], UUID) for user in test_users)

    # UUIDs are deterministic - same every test run
    first_user_id = test_users[0]["id"]
    assert isinstance(first_user_id, UUID)

    # All users have unique UUIDs (different inputs)
    user_ids = [user["id"] for user in test_users]
    assert len(set(user_ids)) == len(user_ids)
```

### Database Testing

```python
import pytest
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestDatabaseOperations:
    def setUp(self):
        user_config = IDConfig(namespace=Namespace("test.example.com/users"), salt="test-v1")
        self.user_gen = UUIDGenerator(user_config)
        self.setup_test_database()

    def test_user_crud_operations(self):
        """Test CRUD operations with deterministic UUIDs"""
        user_email = "dbtest@example.com"
        user_id = self.user_gen.generate("user", email=user_email)

        # Create
        self.db.create_user(user_id, user_email, "Test User")

        # Read - can regenerate UUID to lookup
        stored_user = self.db.get_user(user_id)
        assert stored_user["id"] == user_id
        assert stored_user["email"] == user_email

        # Can also regenerate UUID for lookup without storing it
        lookup_id = self.user_gen.generate("user", email=user_email)
        assert lookup_id == user_id
        stored_user_2 = self.db.get_user(lookup_id)
        assert stored_user_2["email"] == user_email

        # Update
        self.db.update_user(user_id, {"name": "Updated Name"})
        updated_user = self.db.get_user(user_id)
        assert updated_user["name"] == "Updated Name"

        # Delete
        self.db.delete_user(user_id)
        assert self.db.get_user(user_id) is None

    def test_relationship_integrity(self):
        """Test foreign key relationships"""
        user_id = self.user_gen.generate("user", email="parent@test.com")

        order_config = IDConfig(namespace=Namespace("test.example.com/orders"), salt="test-v1")
        order_gen = UUIDGenerator(order_config)

        # Create parent record
        self.db.create_user(user_id, "parent@test.com", "Parent User")

        # Create child record with deterministic UUID
        order_id = order_gen.generate(
            "order",
            user_email="parent@test.com",
            total=100.00
        )
        self.db.create_order(order_id, user_id, 100.00)

        # Verify relationship
        user_orders = self.db.get_user_orders(user_id)
        assert len(user_orders) == 1
        assert user_orders[0]["id"] == order_id
```

## Integration Testing

### Multi-Service Testing

```python
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestMicroservicesIntegration:
    def setUp(self):
        self.user_service = UserService()
        self.order_service = OrderService()
        self.notification_service = NotificationService()

        # All services use same UUID configuration for users
        user_config = IDConfig(
            namespace=Namespace("test.example.com/users"),
            salt="integration-test-v1"
        )
        self.user_gen = UUIDGenerator(user_config)

    def test_cross_service_workflow(self):
        """Test workflow spanning multiple services"""
        user_email = "integration@test.com"
        user_id = self.user_gen.generate("user", email=user_email)

        # Step 1: Create user
        user = self.user_service.create_user(user_email, "Test User")
        assert user["id"] == user_id

        # Step 2: Create order (should reference same user ID)
        # Order service can regenerate user UUID from email
        order = self.order_service.create_order(user_email, ["item1", "item2"])
        assert order["user_id"] == user_id

        # Step 3: Send notification (should reference same user ID)
        # Notification service can also regenerate user UUID
        notification = self.notification_service.send_order_confirmation(
            user_email, order["id"]
        )
        assert notification["user_id"] == user_id

        # All services independently generated the same user ID from the email
        assert user["id"] == order["user_id"] == notification["user_id"]

        # Verify we can regenerate the same UUID
        regenerated_id = self.user_gen.generate("user", email=user_email)
        assert regenerated_id == user_id
```

### API Testing

```python
import requests
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestAPIEndpoints:
    def setUp(self):
        self.base_url = "http://localhost:8000/api"
        user_config = IDConfig(
            namespace=Namespace("test.example.com/users"),
            salt="api-test-v1"
        )
        self.user_gen = UUIDGenerator(user_config)

    def test_user_api_endpoints(self):
        """Test user API with predictable UUIDs"""
        user_email = "apitest@example.com"
        expected_user_id = self.user_gen.generate("user", email=user_email)

        # POST /users - Create user
        create_response = requests.post(
            f"{self.base_url}/users",
            json={"email": user_email, "name": "API Test User"}
        )
        assert create_response.status_code == 201
        created_user = create_response.json()
        assert created_user["id"] == expected_user_id

        # GET /users/{id} - Retrieve user
        get_response = requests.get(f"{self.base_url}/users/{expected_user_id}")
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        assert retrieved_user["id"] == expected_user_id
        assert retrieved_user["email"] == user_email

        # PUT /users/{id} - Update user
        update_response = requests.put(
            f"{self.base_url}/users/{expected_user_id}",
            json={"name": "Updated API User"}
        )
        assert update_response.status_code == 200

        # DELETE /users/{id} - Delete user
        delete_response = requests.delete(f"{self.base_url}/users/{expected_user_id}")
        assert delete_response.status_code == 204
```

## Property-Based Testing

### Hypothesis Integration

```python
from hypothesis import given, strategies as st
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestUUIDProperties:
    def setUp(self):
        config = IDConfig(namespace=Namespace("test.example.com"), salt="property-test-v1")
        self.generator = UUIDGenerator(config)

    @given(st.text(min_size=1))
    def test_uuid_type_property(self, input_text):
        """Property: All generated UUIDs are valid UUID objects"""
        uuid_result = self.generator.generate("entity", value=input_text)

        # Should be a UUID object
        assert isinstance(uuid_result, UUID)

        # Can convert to string
        uuid_str = str(uuid_result)
        assert len(uuid_str) == 36
        assert uuid_str.count("-") == 4

    @given(st.text(min_size=1))
    def test_determinism_property(self, input_text):
        """Property: Same input always produces same UUID"""
        uuid1 = self.generator.generate("entity", value=input_text)
        uuid2 = self.generator.generate("entity", value=input_text)

        assert uuid1 == uuid2
        assert isinstance(uuid1, UUID)

    @given(st.lists(st.text(min_size=1), min_size=2, unique=True))
    def test_uniqueness_property(self, input_list):
        """Property: Different inputs produce different UUIDs"""
        uuids = [
            self.generator.generate("entity", value=input_text)
            for input_text in input_list
        ]

        # All UUIDs should be unique
        assert len(set(uuids)) == len(uuids)
        assert all(isinstance(u, UUID) for u in uuids)
```

## Performance Testing

### Benchmark Testing

```python
import time
from uuid_forge import UUIDGenerator, IDConfig, Namespace

class TestPerformance:
    def setUp(self):
        config = IDConfig(namespace=Namespace("test.example.com"), salt="perf-test-v1")
        self.generator = UUIDGenerator(config)
        self.test_data = [f"user{i}@test.com" for i in range(1000)]

    def test_single_generation_performance(self):
        """Test single UUID generation performance"""
        start_time = time.time()

        uuid_result = self.generator.generate("user", email="performance@test.com")

        end_time = time.time()
        generation_time = end_time - start_time

        # Should generate UUID very quickly
        assert generation_time < 0.01  # Under 10ms
        assert isinstance(uuid_result, UUID)

    def test_batch_generation_performance(self):
        """Test batch UUID generation performance"""
        start_time = time.time()

        uuids = [
            self.generator.generate("user", email=email)
            for email in self.test_data
        ]

        end_time = time.time()
        total_time = end_time - start_time

        # Should generate 1000 UUIDs quickly
        assert total_time < 1.0  # Under 1 second
        assert len(uuids) == 1000
        assert len(set(uuids)) == 1000  # All unique (different emails)

    def test_memory_usage(self):
        """Test memory usage during generation"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Generate many UUIDs
        large_test_data = [f"user{i}@test.com" for i in range(10000)]
        uuids = [
            self.generator.generate("user", email=email)
            for email in large_test_data
        ]

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024
        assert len(uuids) == 10000
```

## Mock and Stub Testing

### Deterministic Mocking

```python
from unittest.mock import patch
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestWithMocking:
    def setUp(self):
        config = IDConfig(namespace=Namespace("test.example.com"), salt="mock-test-v1")
        self.test_generator = UUIDGenerator(config)

    @patch('external_service.get_user_id')
    def test_external_service_integration(self, mock_get_user_id):
        """Test integration with external service using predictable UUIDs"""
        test_email = "mocktest@example.com"
        expected_uuid = self.test_generator.generate("user", email=test_email)

        # Mock external service to return deterministic UUID
        mock_get_user_id.return_value = expected_uuid

        # Test our service
        result = our_service.process_user(test_email)

        # Verify mock was called correctly
        mock_get_user_id.assert_called_once_with(test_email)
        assert result["user_id"] == expected_uuid

    def test_time_dependent_operations(self):
        """Test operations that depend on time using fixed timestamps"""
        fixed_timestamp = "2024-01-15T10:00:00Z"

        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = fixed_timestamp

            # Generate UUID with deterministic timestamp
            uuid_result = self.test_generator.generate(
                "event",
                user_email="timetest@example.com",
                timestamp=fixed_timestamp
            )

            # UUID is deterministic because timestamp is fixed
            expected_uuid = self.test_generator.generate(
                "event",
                user_email="timetest@example.com",
                timestamp=fixed_timestamp
            )
            assert uuid_result == expected_uuid
```

## Test Environment Management

### Environment-Specific Testing

```python
import os
from uuid_forge import UUIDGenerator, IDConfig, Namespace
from uuid import UUID

class TestEnvironmentConfiguration:
    def test_development_environment(self):
        """Test development environment configuration"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["UUID_NAMESPACE_DOMAIN"] = "dev.example.com"

        config = IDConfig(
            namespace=Namespace(os.environ["UUID_NAMESPACE_DOMAIN"]),
            salt=f"{os.environ['ENVIRONMENT']}-v1"
        )
        generator = UUIDGenerator(config)

        dev_uuid = generator.generate("user", email="devtest@example.com")

        # Development environment generates consistent UUIDs
        assert isinstance(dev_uuid, UUID)

        # Can regenerate same UUID
        dev_uuid_2 = generator.generate("user", email="devtest@example.com")
        assert dev_uuid == dev_uuid_2

    def test_production_environment(self):
        """Test production environment configuration"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["UUID_NAMESPACE_DOMAIN"] = "prod.example.com"

        config = IDConfig(
            namespace=Namespace(os.environ["UUID_NAMESPACE_DOMAIN"]),
            salt=f"{os.environ['ENVIRONMENT']}-v1"
        )
        generator = UUIDGenerator(config)

        prod_uuid = generator.generate("user", email="prodtest@example.com")

        # Production environment uses different namespace
        # Different namespace/salt = different UUIDs even with same input
        assert isinstance(prod_uuid, UUID)

        # Verify it's different from dev (different namespace)
        dev_config = IDConfig(
            namespace=Namespace("dev.example.com"),
            salt="development-v1"
        )
        dev_generator = UUIDGenerator(dev_config)
        dev_uuid = dev_generator.generate("user", email="prodtest@example.com")
        assert prod_uuid != dev_uuid  # Different environments = different UUIDs

    def tearDown(self):
        """Clean up environment variables"""
        for var in ["ENVIRONMENT", "UUID_NAMESPACE_DOMAIN"]:
            if var in os.environ:
                del os.environ[var]
```

## Continuous Integration Testing

### CI/CD Pipeline Testing

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --dev

      - name: Run deterministic tests
        run: |
          # Run tests multiple times to verify determinism
          uv run pytest tests/test_deterministic.py
          uv run pytest tests/test_deterministic.py
          uv run pytest tests/test_deterministic.py

      - name: Run integration tests
        run: uv run pytest tests/test_integration.py

      - name: Run performance tests
        run: uv run pytest tests/test_performance.py
```

## Next Steps

- [Migration Use Case](migration.md) - Data migration with consistent UUIDs
- [Best Practices](../guide/best-practices.md) - Testing optimization strategies
- [Development Guide](../development/testing.md) - Development testing setup
