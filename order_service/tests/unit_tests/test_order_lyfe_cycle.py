from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.value_objects.object_ids import UserId, ProductId
from order_service.src.domain.order_status import OrderStatus

from order_service.src.domain.exceptions import InvalidOrderState
import pytest
from order_service.src.domain.events.order_events import (
    OrderCreatedEvent,
    OrderItemAddedEvent,
    OrderItemRemovedEvent,
    OrderItemQuantityChangedEvent,
    OrderConfirmedEvent,
)


def test_order_lifecycle():

    #  user creates order
    user_id = UserId.new()
    order = Order(user_id=user_id)

    assert isinstance(order.events[0], OrderCreatedEvent)
    assert order.status == OrderStatus.PENDING

    #  user adds item
    product_id = ProductId.new()

    order.add_item(product_id=product_id, qty=2, unit_price=Money(10, "USD"))

    assert isinstance(order.events[-1], OrderItemAddedEvent)
    assert len(order.items) == 1

    item_id = next(iter(order.items.keys()))

    # user changes quantity
    order.change_item_quantity(item_id, 5)

    assert isinstance(order.events[-1], OrderItemQuantityChangedEvent)
    assert order.items[item_id].quantity == 5

    #  user removes item
    order.remove_item(item_id)

    assert isinstance(order.events[-1], OrderItemRemovedEvent)
    assert len(order.items) == 0

    # add again to confirm order
    order.add_item(product_id=product_id, qty=3, unit_price=Money(10, "USD"))

    # confirm order (checkout)
    order.confirm()

    assert order.status == OrderStatus.CONFIRMED
    assert isinstance(order.events[-1], OrderConfirmedEvent)

    # total check
    assert order.total().amount == 30
    assert order.total().currency == "USD"


def test_user_cannot_modify_order_after_confirmation():

    order = Order(user_id=UserId.new())

    product_id = ProductId.new()

    # valid in PENDING
    order.add_item(product_id, 2, Money(10, "USD"))
    order.confirm()

    # after CONFIRMED → no modification allowed
    with pytest.raises(InvalidOrderState):
        order.add_item(ProductId.new(), 1, Money(5, "USD"))

    with pytest.raises(InvalidOrderState):
        item_id = next(iter(order.items.keys()))
        order.change_item_quantity(item_id, 10)

    with pytest.raises(InvalidOrderState):
        order.remove_item(item_id)


def test_user_cannot_modify_cancelled_order():

    order = Order(user_id=UserId.new())

    product_id = ProductId.new()

    order.add_item(product_id, 2, Money(10, "USD"))
    order.cancel()

    #  cancelled = frozen state
    with pytest.raises(InvalidOrderState):
        order.add_item(ProductId.new(), 1, Money(5, "USD"))

    with pytest.raises(InvalidOrderState):
        item_id = next(iter(order.items.keys()))
        order.change_item_quantity(item_id, 10)

    with pytest.raises(InvalidOrderState):
        order.remove_item(item_id)


def test_version_increments_when_item_added():
    order = Order(user_id=UserId.new())

    assert order.version == 0

    order.add_item(ProductId.new(), 2, Money(10, "USD"))

    assert order.version == 1


def test_version_increments_when_quantity_changes():
    order = Order(user_id=UserId.new())

    order.add_item(ProductId.new(), 2, Money(10, "USD"))

    item_id = next(iter(order.items.keys()))

    assert order.version == 1

    order.change_item_quantity(item_id, 5)

    assert order.version == 2


def test_version_increments_when_order_confirmed():
    order = Order(user_id=UserId.new())

    assert order.version == 0

    order.confirm()

    assert order.version == 1
