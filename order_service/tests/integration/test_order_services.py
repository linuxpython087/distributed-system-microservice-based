from order_service.src.application.services.unit_of_work import (
    SqlAlchemyOrderUnitOfWork,
)
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus
import pytest


from order_service.src.domain.value_objects.object_ids import ProductId, UserId
from order_service.src.application.services.order_services import (
    create_order,
    remove_item_from_order,
    add_item_to_order,
    change_item_quantity,
    cancel_order,
    confirm_order,
)
from order_service.src.application.services import commands


@pytest.fixture
def uow(session_factory):
    uow = SqlAlchemyOrderUnitOfWork(session_factory)
    return uow


def test_create_order(uow):
    user_id = UserId.new()
    cmd = commands.CreateOrderCommand(user_id=user_id)
    order = create_order(cmd, uow)

    with uow:
        loaded = uow.orders.get(order)

    assert loaded is not None


def test_add_item_to_order(uow):
    user_id = UserId.new()
    cmd = commands.CreateOrderCommand(user_id=user_id)
    order_id = create_order(cmd, uow)
    add_item_to_order(
        commands.AddItemCommand(
            order_id, product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD")
        ),
        uow,
    )

    with uow:

        order = uow.orders.get(order_id)

    assert order is not None


def test_remove_item_from_order(uow):

    user_id = UserId.new()

    order_id = create_order(commands.CreateOrderCommand(user_id), uow)

    add_item_to_order(
        commands.AddItemCommand(
            order_id=order_id,
            product_id=ProductId.new(),
            qty=2,
            unit_price=Money(29, "USD"),
        ),
        uow,
    )

    with uow:
        order = uow.orders.get(order_id)

        item_id = next(iter(order.items.keys()))

    remove_item_from_order(
        commands.RemoveItemCommand(
            order_id=order_id,
            item_id=item_id,
        ),
        uow,
    )

    with uow:
        order = uow.orders.get(order_id)

    assert len(order.items) == 0


def test_change_item_quantity(uow):

    user_id = UserId.new()

    order_id = create_order(commands.CreateOrderCommand(user_id), uow)

    add_item_to_order(
        commands.AddItemCommand(
            order_id=order_id,
            product_id=ProductId.new(),
            qty=2,
            unit_price=Money(29, "USD"),
        ),
        uow,
    )

    with uow:
        order = uow.orders.get(order_id)

        item_id = next(iter(order.items.keys()))

    change_item_quantity(
        commands.ChangeItemQuantityCommand(
            order_id=order_id,
            item_id=item_id,
            qty=10,
        ),
        uow,
    )

    with uow:
        order = uow.orders.get(order_id)

        item = order.items[item_id]

    assert item.quantity == 10


def test_confirm_order(uow):

    order_id = create_order(commands.CreateOrderCommand(UserId.new()), uow)
    add_item_to_order(
        commands.AddItemCommand(
            order_id, product_id=ProductId.new(), qty=2, unit_price=Money(29, "USD")
        ),
        uow,
    )

    confirm_order(
        commands.ConfirmOrderCommand(order_id=order_id),
        uow,
    )

    with uow:
        order = uow.orders.get(order_id)

    assert order.status == OrderStatus.CONFIRMED


def test_cancel_order(uow):

    order_id = create_order(commands.CreateOrderCommand(UserId.new()), uow)

    cancel_order(
        commands.CancelOrderCommand(order_id=order_id),
        uow,
    )

    with uow:
        order = uow.orders.get(order_id)

    assert order.status == OrderStatus.CANCELLED
