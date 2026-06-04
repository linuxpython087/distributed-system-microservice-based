from order_service.src.application.services.unit_of_work import FakeUnitOfWork
from order_service.src.domain.aggregates.order import Order

from order_service.src.domain.value_objects.object_ids import (
    UserId,
)


def test_create_order():
    user_id = UserId.new()
    order = Order(user_id=user_id)

    uow = FakeUnitOfWork()

    with uow:
        uow.orders.add(order)
        uow.commit()

    loaded = uow.orders.get(order.id)

    assert loaded is not None
