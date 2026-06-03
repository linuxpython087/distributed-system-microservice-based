from order_service.src.application.services.unit_of_work import SqlAlchemyOrderUnitOfWork
from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus
import pytest


from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,OrderId
)

def test_create_order(session_factory):
    user_id = UserId.new()
    order = Order(user_id=user_id)

    uow = SqlAlchemyOrderUnitOfWork(session_factory)

    with uow:
        uow.orders.add(order)
        uow.commit()

    with uow:
        loaded = uow.orders.get(order.id)

    assert loaded is not None


def test_add_item_to_order(session_factory):
    user_id = UserId.new()
    order = Order(user_id=user_id)

    uow = SqlAlchemyOrderUnitOfWork(session_factory)

    with uow:
        uow.orders.add(order)
        uow.commit()

        loaded = uow.orders.get(order.id)
        loaded.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD"))
        uow.commit()
        loaded = uow.orders.get(order.id)
    


    assert loaded.items is not None



def test_uow_rolls_back_uncommitted_work(
    session_factory
):

    order_id = OrderId.new()

    try:

        with SqlAlchemyOrderUnitOfWork(
            session_factory
        ) as uow:

            order = Order(
                user_id=UserId.new(),
                order_id=order_id
            )

            uow.orders.add(order)

            raise Exception()

    except Exception:
        pass

    with SqlAlchemyOrderUnitOfWork(
        session_factory
    ) as uow:

        loaded = uow.orders.get(order_id)

        assert loaded is None