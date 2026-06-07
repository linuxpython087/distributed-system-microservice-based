from sqlalchemy import Table, Column, String, Integer, ForeignKey, DateTime, MetaData
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text

from sqlalchemy.types import TypeDecorator
from order_service.src.domain.order_status import OrderStatus
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


from order_service.src.domain.value_objects.object_ids import (
    OrderId,
    UserId,
    ProductId,
    OrderItemId,
    IdempotencyId
)


class BaseUUIDType(TypeDecorator):
    impl = PG_UUID(as_uuid=True)
    cache_ok = True

    vo_class = None  # override

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value  # VO -> UUID

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.vo_class(value)  # UUID -> VO


class OrderIdType(BaseUUIDType):
    vo_class = OrderId
    cache_ok = True


class UserIdType(BaseUUIDType):
    vo_class = UserId
    cache_ok = True


class IdempotencyIdType(BaseUUIDType):
    vo_class = IdempotencyId
    cache_ok = True

class ProductIdType(BaseUUIDType):
    vo_class = ProductId
    cache_ok = True


class OrderItemIdType(BaseUUIDType):
    vo_class = OrderItemId


class OrderStatusType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value  # Enum -> str

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return OrderStatus(value)  # str -> Enum


# -------------------------
# Registry
# -------------------------

metadata = MetaData()


# =========================================================
# ORDERS TABLE
# =========================================================
orders_table = Table(
    "orders",
    metadata,
    Column("id", OrderIdType(), primary_key=True),
    Column("user_id", UserIdType(), nullable=False),
    Column("status", OrderStatusType(), nullable=False),
    # Optimistic locking
    Column("version", Integer, nullable=False, default=0, server_default="0"),
    # Audit (optional but useful)
    Column("created_at", DateTime(timezone=True), server_default=text("now()")),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

# =========================================================
# ORDER ITEMS TABLE
# =========================================================
order_items_table = Table(
    "order_items",
    metadata,
    Column("id", OrderItemIdType(), primary_key=True),
    Column("order_id", OrderIdType(), ForeignKey("orders.id"), nullable=False),
    Column("product_id", ProductIdType(), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price_amount", Integer, nullable=False),
    Column("unit_price_currency", String, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=text("now()")),
)

# =========================================================
# IDEMPOTENCY KEYS TABLE
# =========================================================
idempotency_table = Table(
    "idempotency_keys",
    metadata,
    Column("id", IdempotencyIdType(), primary_key=True),
    # Unique request identifier
    Column("key", String, unique=True, nullable=False),
    # Who triggered request
    Column("user_id", UserIdType(), nullable=False),
    # What operation
    Column("request_path", String, nullable=False),
    # Payload snapshot
    Column("request_params", JSONB, nullable=True),
    # Result cache
    Column("response_code", Integer, nullable=True),
    Column("response_body", JSONB, nullable=True),
    # Distributed execution control
    Column("status", String, nullable=False, default="processing"),
    # processing | completed | failed
    # Recovery mechanism (workflow resume point)
    Column("recovery_point", String, nullable=True),
    # Concurrency protection (distributed lock)
    Column("locked_at", DateTime(timezone=True), nullable=True),
    # Retry tracking
    Column("retry_count", Integer, nullable=False, server_default="0"),
    # Debugging / observability
    Column("error_message", String, nullable=True),
    # Lifecycle
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("expires_at", DateTime(timezone=True), nullable=True),
    # Link to business entity
    Column("order_id", OrderIdType(), ForeignKey("orders.id"), nullable=True),
)





order_read_model_table = Table(
    "order_read_model",
    metadata,

    Column("order_id", OrderIdType(), primary_key=True),
    Column("user_id", UserIdType(), nullable=False),

    Column("status", String, nullable=False),
    Column("item_count", Integer, nullable=False, default=0),

    Column("total_amount", Integer, nullable=False, default=0, server_default=")"),
    Column("currency", String, nullable=False, default="USD"),

    # snapshot complet des items
    Column("items", JSONB, nullable=False),

    Column("version", Integer, nullable=False, default=0),

    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)