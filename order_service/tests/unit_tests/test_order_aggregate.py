from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus
import pytest


from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
)


def test_create_order():
    user_id = UserId.new()
    order = Order(user_id=user_id)

    assert order.user_id.value == user_id.value
    assert order.status == OrderStatus.PENDING
    assert len(order.items) == 0


def test_add_item():
    order = Order(user_id=UserId.new())

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD"))

    assert len(order.items) == 1

    item = next(iter(order.items.values()))

    assert item.product_id.value  # or compare ProductId
    assert item.subtotal().amount == 58


def test_remove_item():
    order = Order(user_id=UserId.new())

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(10, "USD"))

    item_id = next(iter(order.items.keys()))

    order.remove_item(item_id)

    assert len(order.items) == 0


def test_change_item_quantity():
    order = Order(user_id=UserId.new())

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(10, "USD"))

    item_id = next(iter(order.items.keys()))

    order.change_item_quantity(item_id, 5)

    item = order.items[item_id]

    assert item.quantity == 5
    assert item.subtotal().amount == 50


def test_get_total():
    order = Order(user_id=UserId.new())

    order.add_item(ProductId.new(), 2, Money(29, "USD"))

    total = order.total()

    assert total.amount == 58
    assert total.currency == "USD"


# def test_cannot_modify_cancelled_order():
#     order = Order(user_id=1)

#     order.cancel()

#     with pytest.raises(InvalidOrderState):
#         order.add_item(product_id=1, qty=2, unit_price=Money(10, "USD"))


# def test_get_total():
#     order = Order(user_id=1)
#     order.add_item(product_id=1, qty=2, unit_price=Money(29, "USD"))
#     total = order.total()
#     assert total.amount == 58


def test_currency_mismatch_on_add_item():
    order = Order(user_id=UserId.new())

    order.add_item(ProductId.new(), 2, Money(10, "EUR"))

    with pytest.raises(ValueError, match="Currency mismatch in order"):
        order.add_item(ProductId.new(), 1, Money(5, "USD"))
