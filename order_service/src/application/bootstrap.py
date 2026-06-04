import inspect
from functools import partial

from order_service.src.infrastructure.mapper import start_mappers

from order_service.src.application.services.message_bus import MessageBus

from order_service.src.application.services import (
    handlers,
    commands,
)

from order_service.src.application.services.commands_handlers import (
    event_handlers,
)

from order_service.src.application.services.unit_of_work import (
    SqlAlchemyOrderUnitOfWork,
)

from order_service.src.infrastructure.database import SessionLocal


def inject_dependencies(handler, dependencies):

    params = inspect.signature(handler).parameters

    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }

    return partial(handler, **deps)


def bootstrap(
    start_map=True,
    uow=None,
):

    if start_map:
        start_mappers()

    if uow is None:
        uow = SqlAlchemyOrderUnitOfWork(SessionLocal)

    dependencies = {
        "uow": uow,
    }
    injected_command_handlers = {
        commands.CreateOrderCommand: inject_dependencies(
            handlers.create_order,
            dependencies,
        ),
        commands.AddItemCommand: inject_dependencies(
            handlers.add_item_to_order,
            dependencies,
        ),
        commands.RemoveItemCommand: inject_dependencies(
            handlers.remove_item_from_order,
            dependencies,
        ),
        commands.ChangeItemQuantityCommand: inject_dependencies(
            handlers.change_item_quantity,
            dependencies,
        ),
        commands.ConfirmOrderCommand: inject_dependencies(
            handlers.confirm_order,
            dependencies,
        ),
        commands.CancelOrderCommand: inject_dependencies(
            handlers.cancel_order,
            dependencies,
        ),
    }

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in handlers_list
        ]
        for event_type, handlers_list in event_handlers.items()
    }

    return MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )
