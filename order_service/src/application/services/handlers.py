from order_service.src.application.services.unit_of_work import (
    AbstractOrderUnitOfWork,
)
from order_service.src.domain.aggregates.order import Order


from order_service.src.application.services import commands
from order_service.src.domain.value_objects.object_ids import OrderId


def create_order(
    cmd: commands.CreateOrderCommand, uow: AbstractOrderUnitOfWork
) -> OrderId:

    with uow:

        order = Order(user_id=cmd.user_id)

        uow.orders.add(order)

        uow.commit()

        return order.id


def add_item_to_order(cmd: commands.AddItemCommand, uow: AbstractOrderUnitOfWork):

    with uow:

        order = uow.orders.get(cmd.order_id)

        if order is None:
            raise

        order.add_item(cmd.product_id, cmd.qty, cmd.unit_price)

        uow.commit()


def remove_item_from_order(
    cmd: commands.RemoveItemCommand, uow: AbstractOrderUnitOfWork
):
    with uow:

        order = uow.orders.get(cmd.order_id)

        if order is None:
            raise Exception("Order not found")

        order.remove_item(cmd.item_id)

        uow.commit()


def change_item_quantity(
    cmd: commands.ChangeItemQuantityCommand, uow: AbstractOrderUnitOfWork
):
    with uow:

        order = uow.orders.get(cmd.order_id)

        if order is None:
            raise Exception("Order not found")

        order.change_item_quantity(cmd.item_id, cmd.qty)

        uow.commit()


def confirm_order(cmd: commands.ConfirmOrderCommand, uow: AbstractOrderUnitOfWork):

    with uow:

        order = uow.orders.get(cmd.order_id)

        if order is None:
            raise

        order.confirm()

        uow.commit()


def cancel_order(cmd: commands.CancelOrderCommand, uow: AbstractOrderUnitOfWork):
    with uow:

        order = uow.orders.get(cmd.order_id)

        if order is None:
            raise Exception("Order not found")

        order.cancel()

        uow.commit()
