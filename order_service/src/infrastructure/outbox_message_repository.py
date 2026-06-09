
from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.value_objects.object_ids import OutboxId
from sqlalchemy.orm import Session


from order_service.src.infrastructure.orm import orders_table, order_items_table, outbox_messages_table
class SqlalchemyOutboxMessageRepository:

    def __init__(self, session:Session):
        self.session = session

    def add(self, message: OutboxMessage):
        self.session.add(message)
        

    def get_outbox_message(self, id:OutboxId) -> OutboxMessage:
        outbox = self.session.query(OutboxMessage).filter(outbox_messages_table.c.id == id).first()
        return outbox