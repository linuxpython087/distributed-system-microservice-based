from order_service.src.application.services.message_bus import MessageBus
import pytest

from order_service.src.application.services.unit_of_work import (
    SqlAlchemyOrderUnitOfWork,
)

from order_service.src.domain.value_objects.money import Money


from order_service.src.domain.value_objects.object_ids import ProductId, UserId

from order_service.src.application.services import commands

from order_service.src.application.services.commands_handlers import (
    command_handlers,
    event_handlers,
)


@pytest.fixture
def uow(session_factory):
    uow = SqlAlchemyOrderUnitOfWork(session_factory)
    return uow


@pytest.fixture
def bus(uow):

    return MessageBus(
        uow=uow,
        event_handlers=event_handlers,
        command_handlers=command_handlers,
    )


def test_create_order_bus(bus):
    cmd = commands.CreateOrderCommand(user_id=UserId.new())

    bus.handle(cmd)

    # vérifier que l'order a été persisté
    with bus.uow:
        orders = list(bus.uow.orders.list())

    assert len(orders) == 1


def test_add_items_to_order(bus):
    cmd = commands.CreateOrderCommand(user_id=UserId.new())

    bus.handle(cmd)
    result = bus.results[0]
    add_cmd = commands.AddItemCommand(
        result, product_id=ProductId.new(), qty=3, unit_price=Money(20, "USD")
    )
    bus.handle(add_cmd)
    with bus.uow:
        loaded = bus.uow.orders.get(result)

    assert loaded is not None
    assert len(loaded.items) == 1


def test_remove_item(bus):
    # 1. create order
    create_cmd = commands.CreateOrderCommand(user_id=UserId.new())
    bus.handle(create_cmd)
    order_id = bus.results[-1]

    # 2. add item
    add_cmd = commands.AddItemCommand(
        order_id=order_id,
        product_id=ProductId.new(),
        qty=2,
        unit_price=Money(10, "USD"),
    )
    bus.handle(add_cmd)

    with bus.uow:
        order = bus.uow.orders.get(order_id)
        item_id = next(iter(order.items.keys()))

    # 3. remove item
    remove_cmd = commands.RemoveItemCommand(order_id=order_id, item_id=item_id)

    bus.handle(remove_cmd)

    with bus.uow:
        order = bus.uow.orders.get(order_id)

    assert len(order.items) == 0


def test_change_quantity(bus):
    bus.handle(commands.CreateOrderCommand(user_id=UserId.new()))
    order_id = bus.results[-1]

    bus.handle(
        commands.AddItemCommand(
            order_id=order_id,
            product_id=ProductId.new(),
            qty=2,
            unit_price=Money(10, "USD"),
        )
    )

    with bus.uow:
        order = bus.uow.orders.get(order_id)
        item_id = next(iter(order.items.keys()))

    bus.handle(
        commands.ChangeItemQuantityCommand(order_id=order_id, item_id=item_id, qty=10)
    )

    with bus.uow:
        order = bus.uow.orders.get(order_id)

    assert order.items[item_id].quantity == 10


def test_confirm_order(bus):
    bus.handle(commands.CreateOrderCommand(user_id=UserId.new()))
    order_id = bus.results[-1]
    bus.handle(
        commands.AddItemCommand(
            order_id=order_id,
            product_id=ProductId.new(),
            qty=2,
            unit_price=Money(10, "USD"),
        )
    )

    bus.handle(commands.ConfirmOrderCommand(order_id=order_id))

    with bus.uow:
        order = bus.uow.orders.get(order_id)

    assert order.status.value == "CONFIRMED"


def test_cancel_order(bus):
    bus.handle(commands.CreateOrderCommand(user_id=UserId.new()))
    order_id = bus.results[-1]

    bus.handle(commands.CancelOrderCommand(order_id=order_id))

    with bus.uow:
        order = bus.uow.orders.get(order_id)

    assert order.status.value == "CANCELLED"
