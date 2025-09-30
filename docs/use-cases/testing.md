# Testing with UUID-Forge

Learn how to leverage deterministic UUIDs for more effective testing strategies.

## Overview

Deterministic UUID generation provides significant advantages for testing by making UUIDs predictable and reproducible. This enables more reliable tests, easier debugging, and better test data management.

## Benefits for Testing

### Predictable Test Data

```python
from uuid_forge import UUIDGenerator

def test_user_creation():
    """Test with predictable UUIDs"""
    generator = UUIDGenerator(namespace="test-users")

    # Always generates the same UUID for same input
    user_id = generator.generate("test@example.com")

    # Test assertions can use exact UUID values
    assert user_id == "expected-uuid-value-here"
    assert len(user_id) == 36
```

### Reproducible Test Scenarios

```python
class TestOrderProcessing:
    def setUp(self):
        self.user_gen = UUIDGenerator(namespace="test-users")
        self.order_gen = UUIDGenerator(namespace="test-orders")

    def test_order_workflow(self):
        """Test complete order workflow with predictable UUIDs"""
        # Same UUIDs generated every test run
        user_id = self.user_gen.generate("customer@test.com")
        order_data = {
            "user_id": user_id,
            "items": ["product1", "product2"],
            "timestamp": "2024-01-15T10:00:00Z"
        }
        order_id = self.order_gen.generate(order_data)

        # Test can rely on specific UUID values
        assert order_id == self.expected_order_uuid
        assert user_id == self.expected_user_uuid
```

## Test Data Management

### Fixture-Based Testing

```python
import pytest
from uuid_forge import UUIDGenerator

@pytest.fixture
def test_generators():
    """Provide test UUID generators"""
    return {
        "users": UUIDGenerator(namespace="test-users"),
        "orders": UUIDGenerator(namespace="test-orders"),
        "products": UUIDGenerator(namespace="test-products")
    }

@pytest.fixture
def test_users(test_generators):
    """Generate test user data"""
    users = [
        {"email": "user1@test.com", "name": "User One"},
        {"email": "user2@test.com", "name": "User Two"},
        {"email": "user3@test.com", "name": "User Three"}
    ]

    for user in users:
        user["id"] = test_generators["users"].generate(user["email"])

    return users

def test_user_processing(test_users):
    """Test using predictable user data"""
    assert len(test_users) == 3
    assert all(user["id"] for user in test_users)

    # UUIDs are deterministic - same every test run
    expected_first_uuid = test_users[0]["id"]
    assert expected_first_uuid == "predictable-uuid-for-user1"
```

### Database Testing

```python
class TestDatabaseOperations:
    def setUp(self):
        self.user_gen = UUIDGenerator(namespace="db-test-users")
        self.setup_test_database()

    def test_user_crud_operations(self):
        """Test CRUD operations with deterministic UUIDs"""
        user_email = "dbtest@example.com"
        user_id = self.user_gen.generate(user_email)

        # Create
        self.db.create_user(user_id, user_email, "Test User")

        # Read
        stored_user = self.db.get_user(user_id)
        assert stored_user["id"] == user_id
        assert stored_user["email"] == user_email

        # Update
        self.db.update_user(user_id, {"name": "Updated Name"})
        updated_user = self.db.get_user(user_id)
        assert updated_user["name"] == "Updated Name"

        # Delete
        self.db.delete_user(user_id)
        assert self.db.get_user(user_id) is None

    def test_relationship_integrity(self):
        """Test foreign key relationships"""
        user_id = self.user_gen.generate("parent@test.com")
        order_gen = UUIDGenerator(namespace="db-test-orders")

        # Create parent record
        self.db.create_user(user_id, "parent@test.com", "Parent User")

        # Create child record with deterministic UUID
        order_data = {"user_id": user_id, "total": 100.00}
        order_id = order_gen.generate(order_data)
        self.db.create_order(order_id, user_id, 100.00)

        # Verify relationship
        user_orders = self.db.get_user_orders(user_id)
        assert len(user_orders) == 1
        assert user_orders[0]["id"] == order_id
```

## Integration Testing

### Multi-Service Testing

```python
class TestMicroservicesIntegration:
    def setUp(self):
        self.user_service = UserService()
        self.order_service = OrderService()
        self.notification_service = NotificationService()

        # All services use same UUID generators
        self.user_gen = UUIDGenerator(namespace="integration-users")

    def test_cross_service_workflow(self):
        """Test workflow spanning multiple services"""
        user_email = "integration@test.com"
        user_id = self.user_gen.generate(user_email)

        # Step 1: Create user
        user = self.user_service.create_user(user_email, "Test User")
        assert user["id"] == user_id

        # Step 2: Create order (should reference same user ID)
        order = self.order_service.create_order(user_email, ["item1", "item2"])
        assert order["user_id"] == user_id

        # Step 3: Send notification (should reference same user ID)
        notification = self.notification_service.send_order_confirmation(user_email, order["id"])
        assert notification["user_id"] == user_id

        # All services generated same user ID independently
        assert user["id"] == order["user_id"] == notification["user_id"]
```

### API Testing

```python
import requests
from uuid_forge import UUIDGenerator

class TestAPIEndpoints:
    def setUp(self):
        self.base_url = "http://localhost:8000/api"
        self.user_gen = UUIDGenerator(namespace="api-test-users")

    def test_user_api_endpoints(self):
        """Test user API with predictable UUIDs"""
        user_email = "apitest@example.com"
        expected_user_id = self.user_gen.generate(user_email)

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
from uuid_forge import UUIDGenerator

class TestUUIDProperties:
    def setUp(self):
        self.generator = UUIDGenerator(namespace="property-tests")

    @given(st.text(min_size=1))
    def test_uuid_format_property(self, input_text):
        """Property: All generated UUIDs have valid format"""
        uuid_result = self.generator.generate(input_text)

        # UUID format properties
        assert len(uuid_result) == 36
        assert uuid_result.count("-") == 4
        assert all(c in "0123456789abcdef-" for c in uuid_result.lower())

    @given(st.text(min_size=1))
    def test_determinism_property(self, input_text):
        """Property: Same input always produces same UUID"""
        uuid1 = self.generator.generate(input_text)
        uuid2 = self.generator.generate(input_text)

        assert uuid1 == uuid2

    @given(st.lists(st.text(min_size=1), min_size=2, unique=True))
    def test_uniqueness_property(self, input_list):
        """Property: Different inputs produce different UUIDs"""
        uuids = [self.generator.generate(input_text) for input_text in input_list]

        # All UUIDs should be unique
        assert len(set(uuids)) == len(uuids)
```

## Performance Testing

### Benchmark Testing

```python
import time
from uuid_forge import UUIDGenerator

class TestPerformance:
    def setUp(self):
        self.generator = UUIDGenerator(namespace="perf-tests")
        self.test_data = [f"user{i}@test.com" for i in range(1000)]

    def test_single_generation_performance(self):
        """Test single UUID generation performance"""
        start_time = time.time()

        uuid_result = self.generator.generate("performance@test.com")

        end_time = time.time()
        generation_time = end_time - start_time

        # Should generate UUID in under 1ms
        assert generation_time < 0.001
        assert len(uuid_result) == 36

    def test_batch_generation_performance(self):
        """Test batch UUID generation performance"""
        start_time = time.time()

        uuids = [self.generator.generate(email) for email in self.test_data]

        end_time = time.time()
        total_time = end_time - start_time

        # Should generate 1000 UUIDs in under 100ms
        assert total_time < 0.1
        assert len(uuids) == 1000
        assert len(set(uuids)) == 1000  # All unique

    def test_memory_usage(self):
        """Test memory usage during generation"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Generate many UUIDs
        large_test_data = [f"user{i}@test.com" for i in range(10000)]
        uuids = [self.generator.generate(email) for email in large_test_data]

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
from uuid_forge import UUIDGenerator

class TestWithMocking:
    def setUp(self):
        self.test_generator = UUIDGenerator(namespace="mock-tests")

    @patch('external_service.get_user_id')
    def test_external_service_integration(self, mock_get_user_id):
        """Test integration with external service using predictable UUIDs"""
        test_email = "mocktest@example.com"
        expected_uuid = self.test_generator.generate(test_email)

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

            # Generate UUID with time component
            time_data = {
                "user": "timetest@example.com",
                "timestamp": fixed_timestamp
            }
            uuid_result = self.test_generator.generate(time_data)

            # UUID is deterministic because timestamp is fixed
            assert uuid_result == self.test_generator.generate(time_data)
```

## Test Environment Management

### Environment-Specific Testing

```python
import os
from uuid_forge import UUIDGenerator

class TestEnvironmentConfiguration:
    def test_development_environment(self):
        """Test development environment configuration"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["UUID_NAMESPACE"] = "dev-test"

        generator = UUIDGenerator(namespace=os.environ["UUID_NAMESPACE"])
        uuid_result = generator.generate("devtest@example.com")

        # Development environment generates consistent test UUIDs
        assert uuid_result.startswith("dev-specific-pattern")

    def test_production_environment(self):
        """Test production environment configuration"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["UUID_NAMESPACE"] = "prod"

        generator = UUIDGenerator(namespace=os.environ["UUID_NAMESPACE"])
        uuid_result = generator.generate("prodtest@example.com")

        # Production environment uses different namespace
        assert uuid_result != "dev-specific-pattern"

    def tearDown(self):
        """Clean up environment variables"""
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "UUID_NAMESPACE" in os.environ:
            del os.environ["UUID_NAMESPACE"]
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
          python-version: '3.11'

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
