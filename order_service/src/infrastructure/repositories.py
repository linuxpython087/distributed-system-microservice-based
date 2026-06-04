from sqlalchemy.orm import Session

from order_service.src.domain.value_objects.object_ids import OrderId
from order_service.src.infrastructure.orm import orders_table
from order_service.src.domain.aggregates.order import Order


class SqlAlchemyOrderRepository:

    def __init__(self, session: Session):
        self.session = session
        self.seen = set()

    def add(self, order):
        self.session.add(order)

    def get(self, order_id: OrderId):
        order = self.session.query(Order).filter(orders_table.c.id == order_id).first()
        if order:
            self.seen.add(order)

        return order

    def remove(self, order):
        querry = self.session.query(Order).filter(orders_table.c.id == order)

        querry.delete(synchronize_session=False)

    def list(self):
        return self.session.query(Order).all()
