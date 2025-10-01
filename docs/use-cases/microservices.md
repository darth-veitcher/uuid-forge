# Microservices Architecture

Learn how to use UUID-Forge effectively in microservices architectures for consistent entity identification across services.

## Overview

In microservices architectures, UUID-Forge solves the critical problem of consistent entity identification across distributed services. By generating deterministic UUIDs, different services can independently create the same UUID for the same entity, eliminating the need for centralized ID generation or complex coordination.

## Key Benefits

- **Service Independence**: Services can generate UUIDs without inter-service communication
- **Data Consistency**: Same entity gets same UUID across all services
- **Event Sourcing**: Consistent UUIDs for event correlation
- **Testing**: Predictable UUIDs simplify integration testing

## Service Design Patterns

### 1. Namespace-per-Service Pattern

Each service uses its own namespace for entity isolation:

```python
# User Service
from uuid_forge import UUIDGenerator
# Service-specific namespace
USER_SERVICE_NS = Namespace("user-service.mycompany.com")
user_forge = UUIDGenerator(namespace=USER_SERVICE_NS)

class UserService:
    def create_user(self, email, name):
        user_id = user_forge.generate({
            "email": email.lower().strip(),
            "type": "user"
        })
        return {"id": user_id, "email": email, "name": name}
```

```python
# Order Service
ORDER_SERVICE_NS = Namespace("order-service.mycompany.com")
order_forge = UUIDGenerator(namespace=ORDER_SERVICE_NS)

class OrderService:
    def create_order(self, user_email, items):
        # Generate consistent user reference
        user_id = user_forge.generate({
            "email": user_email.lower().strip(),
            "type": "user"
        })

        # Generate order ID
        order_id = order_forge.generate({
            "user_id": user_id,
            "items": sorted(items),
            "type": "order"
        })

        return {"id": order_id, "user_id": user_id, "items": items}
```

### 2. Entity-Type-Based Namespaces

Create namespaces based on entity types:

```python
# Root namespace for the organization
ROOT_NS = Namespace("mycompany.com")

# Entity-specific namespaces
USERS_NS = uuid.uuid5(ROOT_NS, "users")
ORDERS_NS = uuid.uuid5(ROOT_NS, "orders")
PRODUCTS_NS = uuid.uuid5(ROOT_NS, "products")

# Shared forge instances
user_forge = UUIDGenerator(namespace=USERS_NS)
order_forge = UUIDGenerator(namespace=ORDERS_NS)
product_forge = UUIDGenerator(namespace=PRODUCTS_NS)

# Any service can generate consistent entity UUIDs
def get_user_uuid(email):
    return user_forge.generate(email.lower().strip())

def get_product_uuid(sku):
    return product_forge.generate(sku.upper().strip())
```

## Service Integration Examples

### User Management Service

```python
class UserManagementService:
    def __init__(self):
        self.user_forge = UUIDGenerator(namespace=USERS_NS)

    def register_user(self, email, profile_data):
        user_id = self.user_forge.generate(email)

        user = {
            "id": user_id,
            "email": email,
            "profile": profile_data,
            "created_at": datetime.utcnow()
        }

        # Store in database
        self.db.users.insert(user)

        # Publish event
        self.event_bus.publish("user.registered", {
            "user_id": user_id,
            "email": email
        })

        return user

    def get_user_id(self, email):
        """Other services can call this to get consistent user ID"""
        return self.user_forge.generate(email)
```

### Order Processing Service

```python
class OrderProcessingService:
    def __init__(self):
        self.user_forge = UUIDGenerator(namespace=USERS_NS)
        self.order_forge = UUIDGenerator(namespace=ORDERS_NS)
        self.product_forge = UUIDGenerator(namespace=PRODUCTS_NS)

    def create_order(self, user_email, product_skus, quantities):
        # Generate consistent IDs
        user_id = self.user_forge.generate(user_email)

        order_items = []
        for sku, qty in zip(product_skus, quantities):
            product_id = self.product_forge.generate(sku)
            order_items.append({
                "product_id": product_id,
                "sku": sku,
                "quantity": qty
            })

        # Generate order ID from user and items
        order_data = {
            "user_id": user_id,
            "items": sorted(order_items, key=lambda x: x["sku"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        order_id = self.order_forge.generate(order_data)

        order = {
            "id": order_id,
            "user_id": user_id,
            "items": order_items,
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        # Store order
        self.db.orders.insert(order)

        # Publish event
        self.event_bus.publish("order.created", {
            "order_id": order_id,
            "user_id": user_id
        })

        return order
```

### Notification Service

```python
class NotificationService:
    def __init__(self):
        self.user_forge = UUIDGenerator(namespace=USERS_NS)
        self.notification_forge = UUIDGenerator(namespace=NOTIFICATIONS_NS)

    def handle_order_created(self, event_data):
        user_id = event_data["user_id"]
        order_id = event_data["order_id"]

        # Generate notification ID
        notification_id = self.notification_forge.generate({
            "user_id": user_id,
            "type": "order_confirmation",
            "reference_id": order_id
        })

        notification = {
            "id": notification_id,
            "user_id": user_id,
            "type": "order_confirmation",
            "message": f"Your order {order_id} has been created",
            "created_at": datetime.utcnow()
        }

        self.send_notification(notification)
```

## Event-Driven Architecture

### Event Correlation

Use deterministic UUIDs for event correlation:

```python
class EventService:
    def __init__(self):
        self.event_forge = UUIDGenerator(namespace="events")

    def create_correlation_id(self, user_id, action, timestamp):
        """Create deterministic correlation ID for event tracing"""
        return self.event_forge.generate({
            "user_id": user_id,
            "action": action,
            "timestamp": timestamp.isoformat()
        })

    def publish_correlated_events(self, user_id, action):
        timestamp = datetime.utcnow()
        correlation_id = self.create_correlation_id(user_id, action, timestamp)

        events = [
            {"type": "action.started", "correlation_id": correlation_id},
            {"type": "action.processed", "correlation_id": correlation_id},
            {"type": "action.completed", "correlation_id": correlation_id}
        ]

        for event in events:
            self.event_bus.publish(event["type"], event)
```

### Saga Pattern Implementation

```python
class SagaOrchestrator:
    def __init__(self):
        self.saga_forge = UUIDGenerator(namespace="sagas")
        self.user_forge = UUIDGenerator(namespace=USERS_NS)
        self.order_forge = UUIDGenerator(namespace=ORDERS_NS)

    def start_order_saga(self, user_email, order_data):
        user_id = self.user_forge.generate(user_email)
        order_id = self.order_forge.generate(order_data)

        # Generate deterministic saga ID
        saga_id = self.saga_forge.generate({
            "type": "order_processing",
            "user_id": user_id,
            "order_id": order_id
        })

        saga_state = {
            "saga_id": saga_id,
            "user_id": user_id,
            "order_id": order_id,
            "steps": ["validate_user", "reserve_inventory", "process_payment"],
            "current_step": 0,
            "status": "started"
        }

        self.execute_saga_step(saga_state)
        return saga_id
```

## API Gateway Integration

### Request Tracing

```python
class APIGateway:
    def __init__(self):
        self.trace_forge = UUIDGenerator(namespace="traces")

    def create_trace_id(self, request):
        """Create deterministic trace ID for request tracking"""
        trace_data = {
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get("User-Agent", ""),
            "timestamp": datetime.utcnow().replace(microsecond=0).isoformat()
        }
        return self.trace_forge.generate(trace_data)

    def process_request(self, request):
        trace_id = self.create_trace_id(request)
        request.headers["X-Trace-ID"] = trace_id
        return self.forward_to_service(request)
```

## Database Consistency

### Cross-Service Queries

```python
class ReportingService:
    def __init__(self):
        self.user_forge = UUIDGenerator(namespace=USERS_NS)
        self.order_forge = UUIDGenerator(namespace=ORDERS_NS)

    def generate_user_order_report(self, user_email):
        user_id = self.user_forge.generate(user_email)

        # Query user data from user service database
        user_data = self.user_db.find_one({"id": user_id})

        # Query order data from order service database
        orders = self.order_db.find({"user_id": user_id})

        return {
            "user": user_data,
            "orders": list(orders),
            "generated_at": datetime.utcnow()
        }
```

## Testing Strategies

### Integration Testing

```python
class IntegrationTestSuite:
    def setUp(self):
        self.user_service = UserManagementService()
        self.order_service = OrderProcessingService()
        self.notification_service = NotificationService()

    def test_cross_service_uuid_consistency(self):
        """Test that all services generate same UUID for same entity"""
        email = "test@example.com"

        # Generate user ID from different services
        user_id_1 = self.user_service.get_user_id(email)
        user_id_2 = self.order_service.user_forge.generate(email)
        user_id_3 = self.notification_service.user_forge.generate(email)

        # All should be identical
        assert user_id_1 == user_id_2 == user_id_3

    def test_end_to_end_workflow(self):
        """Test complete workflow with consistent UUIDs"""
        email = "customer@example.com"

        # Register user
        user = self.user_service.register_user(email, {"name": "Test User"})

        # Create order
        order = self.order_service.create_order(email, ["SKU001"], [1])

        # Verify same user ID is used
        assert user["id"] == order["user_id"]
```

## Monitoring and Observability

### UUID Tracking

```python
import logging

class UUIDTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_forge = UUIDGenerator(namespace=USERS_NS)

    def track_uuid_usage(self, service_name, entity_type, input_data, uuid_result):
        """Track UUID generation for debugging and monitoring"""
        self.logger.info({
            "event": "uuid_generated",
            "service": service_name,
            "entity_type": entity_type,
            "uuid": uuid_result,
            "input_hash": hash(str(input_data))  # Don't log sensitive data
        })

    def validate_uuid_consistency(self, expected_uuid, input_data):
        """Validate that UUID generation is still consistent"""
        generated_uuid = self.user_forge.generate(input_data)
        if generated_uuid != expected_uuid:
            self.logger.error({
                "event": "uuid_inconsistency_detected",
                "expected": expected_uuid,
                "generated": generated_uuid,
                "input_hash": hash(str(input_data))
            })
            return False
        return True
```

## Next Steps

- [Multi-Storage Use Case](multi-storage.md) - Learn about UUID consistency across storage systems
- [Testing Use Case](testing.md) - Advanced testing strategies with deterministic UUIDs
- [Migration Use Case](migration.md) - Data migration patterns with UUID-Forge
