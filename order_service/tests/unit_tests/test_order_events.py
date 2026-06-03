from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.object_ids import (
    UserId,
    ProductId,
)
from order_service.src.domain.events.order_events import (
    OrderCreatedEvent,
    OrderConfirmedEvent,
    OrderItemAddedEvent,
    OrderCancelledEvent,
    OrderItemQuantityChangedEvent,
    OrderItemRemovedEvent,
)
from order_service.src.domain.value_objects.money import Money


def test_order_created_event_is_recorded():
    user_id = UserId.new()

    order = Order(user_id=user_id)

    assert len(order.events) == 1

    event = order.events[0]

    assert isinstance(event, OrderCreatedEvent)
    assert event.order_id == order.id
    assert event.user_id == user_id


def test_order_confirmed_event_is_recorded():
    user_id = UserId.new()

    order = Order(user_id=user_id)

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(10, "USD"))

    order.confirm()

    assert isinstance(order.events[-1], OrderConfirmedEvent)
    assert len(order.events) == 3


def test_order_add_item_event_is_recorded():
    user_id = UserId.new()

    order = Order(user_id=user_id)

    product_id = ProductId.new()

    order.add_item(product_id=product_id, qty=2, unit_price=Money(10, "USD"))

    assert isinstance(order.events[-1], OrderItemAddedEvent)

    event = order.events[-1]

    assert event.order_id == order.id
    assert event.product_id == product_id
    assert event.quantity == 2


def test_order_cancle_order_event_is_recorded():
    user_id = UserId.new()

    order = Order(user_id=user_id)

    product_id = ProductId.new()

    order.add_item(product_id=product_id, qty=2, unit_price=Money(10, "USD"))

    order.cancel()

    assert isinstance(order.events[-1], OrderCancelledEvent)

    event = order.events[-1]

    assert event.order_id == order.id


def test_order_remove_item_event_is_recorded():
    user_id = UserId.new()

    order = Order(user_id=user_id)

    product_id = ProductId.new()

    order.add_item(product_id=product_id, qty=2, unit_price=Money(10, "USD"))

    assert isinstance(order.events[-1], OrderItemAddedEvent)
    item_id = next(iter(order.items.keys()))

    order.remove_item(item_id=item_id)

    event = order.events[-1]

    assert isinstance(event, OrderItemRemovedEvent)


def test_order_change_quantity_item_event_is_recorded():
    user_id = UserId.new()

    order = Order(user_id=user_id)

    product_id = ProductId.new()

    order.add_item(product_id=product_id, qty=2, unit_price=Money(10, "USD"))

    order.add_item(product_id=product_id, qty=2, unit_price=Money(10, "USD"))

    assert isinstance(order.events[-1], OrderItemAddedEvent)
    item_id = next(iter(order.items.keys()))

    order.change_item_quantity(item_id=item_id, qty=20)

    event = order.events[-1]

    assert isinstance(event, OrderItemQuantityChangedEvent)

    print(order.to_dict())
