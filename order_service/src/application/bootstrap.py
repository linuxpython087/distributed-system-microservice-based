from order_service.src.infrastructure.mapper import start_mappers

from order_service.src.application.services.message_bus import MessageBus


from order_service.src.application.services.events_handlers import (
    event_handlers,
)

from order_service.src.application.services.commands_handlers import commands_handlers

from order_service.src.application.services.unit_of_work import (
    SqlAlchemyOrderUnitOfWork,
    AbstractOrderUnitOfWork,
)


from order_service.src.infrastructure.database import SessionLocal
from order_service.src.infrastructure.database import get_db

def bootstrap(
    start_map=True,
    uow: AbstractOrderUnitOfWork = None,
):

    if start_map:
        start_mappers()

    if uow is None:
        uow = SqlAlchemyOrderUnitOfWork(SessionLocal)


    return MessageBus(
        uow=uow,
        command_handlers=commands_handlers,
        events_handlers=event_handlers,
    )
