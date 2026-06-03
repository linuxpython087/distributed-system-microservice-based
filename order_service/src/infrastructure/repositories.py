from sqlalchemy.orm import Session

from order_service.src.domain.value_objects.object_ids import OrderId
from order_service.src.infrastructure.orm import orders_table
from order_service.src.domain.aggregates.order import Order


class SqlAlchemyOrderRepository:

    def __init__(self, session: Session):
        self.session = session

    def add(self, order):
        self.session.add(order)

    def get(self, order_id: OrderId):
        return self.session.query(Order).filter(orders_table.c.id == order_id).first()

    def remove(self, order):
        querry = self.session.query(Order).filter(orders_table.c.id == order)

        querry.delete(synchronize_session=False)
