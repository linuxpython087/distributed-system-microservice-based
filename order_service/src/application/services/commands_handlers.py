from order_service.src.application.services.handlers import (
    CreateOrderHandler,
    AddItemToOrderHandler,
    ChangeItemQuantityHandler,
    ConfirmOrderHandler,
    CancelOrderHandler,
    RemoveItemFromOrderHandler,
)
from order_service.src.application.services import (
    commands,
)

commands_handlers = {
    commands.CreateOrderCommand: CreateOrderHandler(),
    commands.AddItemCommand: AddItemToOrderHandler(),
    commands.RemoveItemCommand: RemoveItemFromOrderHandler(),
    commands.ChangeItemQuantityCommand: ChangeItemQuantityHandler(),
    commands.ConfirmOrderCommand: ConfirmOrderHandler(),
    commands.CancelOrderCommand: CancelOrderHandler(),
}
