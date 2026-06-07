from typing import Union

from order_service.src.application.services import commands
from order_service.src.domain.events import order_events

from order_service.src.application.services.unit_of_work import (
    AbstractOrderUnitOfWork,
)

Message = Union[commands.Command, order_events.Event]



# =========================
# MESSAGE BUS
# =========================


class MessageBus:
    def __init__(self, uow: AbstractOrderUnitOfWork, command_handlers, events_handlers):
        self.uow = uow
        self.command_handlers = command_handlers
        self.events_handlers = events_handlers

        self.results = []
        self.collected_events = []

    def handle(self, message):

        queue = [message]

        while queue:

            message = queue.pop(0)

            if message.__class__.__name__.endswith("Command"):

                result = self._handle_command(message, queue)
                self.results.append(result)

            else:
                self._handle_event(message, queue)

        return self.results

    def _handle_command(self, command, queue):
        handler = self.command_handlers[type(command)]

        result = handler.handle(command, self.uow)

        new_events = list(self.uow.collect_new_events())

        queue.extend(new_events)
        self.collected_events.extend(new_events)

        return result

    def _handle_event(self, event, queue):
        # placeholder : à brancher sur event handlers plus tard
        self.collected_events.append(event)
