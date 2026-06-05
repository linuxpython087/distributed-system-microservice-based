from order_service.src.domain.events import order_events


def send_email_order_created(event, uow):
    print(f"[EMAIL] Order created: {event.order_id}")


event_handlers = {
    order_events.OrderCreatedEvent: [send_email_order_created],
}
