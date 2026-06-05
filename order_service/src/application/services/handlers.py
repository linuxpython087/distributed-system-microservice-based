from typing import Protocol

from order_service.src.application.services.unit_of_work import (
    AbstractOrderUnitOfWork,
)
from order_service.src.domain.aggregates.order import Order
from order_service.src.application.services import commands

# =========================
# COMMAND HANDLER CONTRACT
# =========================


class CommandHandler(Protocol):
    def handle(self, command, uow: AbstractOrderUnitOfWork):
        pass


# =========================
# HANDLERS
# =========================


class CreateOrderHandler:
    def handle(self, cmd: commands.CreateOrderCommand, uow: AbstractOrderUnitOfWork):
        with uow:
            order = Order(user_id=cmd.user_id)
            uow.orders.add(order)
            uow.commit()
            return order.id


class AddItemToOrderHandler:
    def handle(self, cmd: commands.AddItemCommand, uow: AbstractOrderUnitOfWork):
        with uow:
            order = uow.orders.get(cmd.order_id)

            if order is None:
                raise Exception("Order not found")

            order.add_item(cmd.product_id, cmd.qty, cmd.unit_price)

            uow.commit()


class RemoveItemFromOrderHandler:
    def handle(self, cmd: commands.RemoveItemCommand, uow: AbstractOrderUnitOfWork):
        with uow:
            order = uow.orders.get(cmd.order_id)

            if order is None:
                raise Exception("Order not found")

            order.remove_item(cmd.item_id)

            uow.commit()


class ChangeItemQuantityHandler:
    def handle(
        self, cmd: commands.ChangeItemQuantityCommand, uow: AbstractOrderUnitOfWork
    ):
        with uow:
            order = uow.orders.get(cmd.order_id)

            if order is None:
                raise Exception("Order not found")

            order.change_item_quantity(cmd.item_id, cmd.qty)

            uow.commit()


class ConfirmOrderHandler:
    def handle(self, cmd: commands.ConfirmOrderCommand, uow: AbstractOrderUnitOfWork):
        with uow:
            order = uow.orders.get(cmd.order_id)

            if order is None:
                raise Exception("Order not found")

            order.confirm()

            uow.commit()


class CancelOrderHandler:
    def handle(self, cmd: commands.CancelOrderCommand, uow: AbstractOrderUnitOfWork):
        with uow:
            order = uow.orders.get(cmd.order_id)

            if order is None:
                raise Exception("Order not found")

            order.cancel()

            uow.commit()
