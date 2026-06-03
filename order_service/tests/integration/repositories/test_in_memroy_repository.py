from order_service.src.infrastructure.fake_repository import FakeOrderRepository
from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus


from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
)


def test_add_order():
    repo = FakeOrderRepository()
    order = Order(user_id=UserId.new())

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD"))

    repo.add(order)

    retrieve_order = repo.get(order.id)
    assert order.id == retrieve_order.id
    assert len(repo.orders) == 1


def test_remove_order():
    repo = FakeOrderRepository()
    order = Order(user_id=UserId.new())

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD"))

    repo.add(order)

    repo.remove(order)

    assert len(repo.orders) == 0


def test_confirm_order():
    repo = FakeOrderRepository()

    order = Order(user_id=UserId.new())

    repo.add(order)

    order.confirm()

    loaded = repo.get(order.id)

    assert loaded.status == OrderStatus.CONFIRMED
