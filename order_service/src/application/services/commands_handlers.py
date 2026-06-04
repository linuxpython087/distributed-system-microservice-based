from order_service.src.application.services import commands
from order_service.src.domain.events import order_events

from order_service.src.application.services import handlers


def send_email_order_created(event, uow):
    print(f"[EMAIL] Order created: {event.order_id}")


event_handlers = {
    order_events.OrderCreatedEvent: [send_email_order_created],
}


command_handlers = {
    commands.CreateOrderCommand: handlers.create_order,
    commands.AddItemCommand: handlers.add_item_to_order,
    commands.RemoveItemCommand: handlers.remove_item_from_order,
    commands.ChangeItemQuantityCommand: handlers.change_item_quantity,
    commands.ConfirmOrderCommand: handlers.confirm_order,
    commands.CancelOrderCommand: handlers.cancel_order,
}
