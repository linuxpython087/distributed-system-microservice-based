from order_service.src.infrastructure.repositories import SqlAlchemyOrderRepository
from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus
import pytest


from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
)


@pytest.fixture
def create_and_add_item_to_order(session):
    repo = SqlAlchemyOrderRepository(session)

    order = Order(user_id=UserId.new())

    repo.add(order)

    session.commit()

    loaded = repo.get(order.id)
    loaded.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD"))

    session.commit()
    return loaded


def test_confirm_order_is_persisted(session):
    repo = SqlAlchemyOrderRepository(session)

    order = Order(user_id=UserId.new())

    repo.add(order)

    session.commit()

    order.confirm()

    session.commit()

    loaded = repo.get(order.id)
    print(loaded)
    assert loaded.status == OrderStatus.CONFIRMED
    print(loaded.items)


def test_add_item_to_order(session):
    repo = SqlAlchemyOrderRepository(session)

    order = Order(user_id=UserId.new())

    repo.add(order)

    session.commit()

    loaded = repo.get(order.id)
    loaded.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD"))
    # loaded.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(30, "USD"))

    session.commit()
    assert loaded.status == OrderStatus.PENDING

    loaded.confirm()
    session.commit()
    loaded = repo.get(order.id)
    assert loaded.status == OrderStatus.CONFIRMED

    assert loaded.total() == Money(amount=58, currency="USD")


def test_add_item_to_existing_order(session, create_and_add_item_to_order):

    assert create_and_add_item_to_order.status == OrderStatus.PENDING
    create_and_add_item_to_order.add_item(
        product_id=ProductId.new(), qty=2, unit_price=Money(30, "USD")
    )
    session.commit()

    assert create_and_add_item_to_order.total() == Money(amount=118, currency="USD")


def test_remove_item_to_existing_order(session, create_and_add_item_to_order):
    order = create_and_add_item_to_order

    item_id = next(iter(order.items.keys()))

    assert create_and_add_item_to_order.status == OrderStatus.PENDING
    create_and_add_item_to_order.remove_item(item_id)
    session.commit()

    repo = SqlAlchemyOrderRepository(session)
    loaded = repo.get(order.id)

    assert item_id not in loaded.items
    assert len(loaded.items) == 0

    assert loaded.total() == Money(amount=0, currency="USD")
