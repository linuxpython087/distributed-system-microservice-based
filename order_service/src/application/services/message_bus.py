from typing import Union

from order_service.src.application.services import commands
from order_service.src.domain.events import order_events

from order_service.src.application.services.unit_of_work import (
    AbstractOrderUnitOfWork,
)

Message = Union[commands.Command, order_events.Event]


class MessageBus:
    def __init__(self, uow: AbstractOrderUnitOfWork, event_handlers, command_handlers):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.results = []
        self.collected_events = []

    def handle(self, message):
        queue = [message]

        while queue:
            message = queue.pop(0)

            if isinstance(message, commands.Command):
                result = self._handle_command(message, queue)
                self.results.append(result)
            else:
                self._handle_event(message, queue)

    def _handle_command(self, command, queue):
        handler = self.command_handlers.get(type(command))

        if not handler:
            raise Exception(f"No handler for command {type(command)}")

        result = handler(command, self.uow)

        new_events = list(self.uow.collect_new_events())

        queue.extend(self.uow.collect_new_events())

        self.collected_events.extend(new_events)
        return result

    def _handle_event(self, event, queue):
        handlers = self.event_handlers.get(type(event), [])

        for handler in handlers:
            handler(event, self.uow)

        new_events = list(self.uow.collect_new_events())

        queue.extend(new_events)
        self.collected_events.extend(new_events)
