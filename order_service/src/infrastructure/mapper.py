from sqlalchemy.orm import registry, relationship

from order_service.src.infrastructure.orm import orders_table, order_items_table, outbox_messages_table
from sqlalchemy.orm import composite
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.entities.order_item import OrderItem
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy import event
from order_service.src.domain.entities.outbox_message import OutboxMessage

# -------------------------
# DOMAIN IMPORTS (for mapping layer)
# -------------------------


mapper_registry = registry()

_mappers_started = False


def start_mappers():
    global _mappers_started

    if _mappers_started:
        return

    _mappers_started = True

    mapper_registry.map_imperatively(
        OrderItem,
        order_items_table,
        properties={
            "_quantity": order_items_table.c.quantity,
            "unit_price": composite(
                Money,
                order_items_table.c.unit_price_amount,
                order_items_table.c.unit_price_currency,
            ),
        },
    )

    mapper_registry.map_imperatively(
        Order,
        orders_table,
        properties={
            "items": relationship(
                OrderItem,
                cascade="all, delete-orphan",
                primaryjoin=orders_table.c.id == order_items_table.c.order_id,
                foreign_keys=[order_items_table.c.order_id],
                backref="order",
                lazy="joined",
                collection_class=attribute_mapped_collection("id"),
            )
        },
        version_id_col=orders_table.c.version,
        version_id_generator=False,
    )

    mapper_registry.map_imperatively(
        OutboxMessage, outbox_messages_table
    )

    @event.listens_for(Order, "load")
    def receive_load(order, context):
        order.events = []
