
from abc import abstractmethod, ABC
from order_service.src.domain.repositories import OrderRepository
from order_service.src.infrastructure.repositories import SqlAlchemyOrderRepository
from order_service.src.infrastructure.database import SessionLocal

from order_service.src.infrastructure.fake_repository import FakeOrderRepository
from sqlalchemy import event

class AbstractOrderUnitOfWork(ABC):

    orders: OrderRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
    

    # def collect_new_events(self):

    #     for product in self.products.seen:

    #         while product.events:

    #             yield product.events.pop(0)


class FakeUnitOfWork(AbstractOrderUnitOfWork):

    def __init__(self):
        self.orders = FakeOrderRepository()
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

class SqlAlchemyOrderUnitOfWork(AbstractOrderUnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.orders = SqlAlchemyOrderRepository(self.session)
        return self   

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc:
                self.rollback()
            else:
                self.commit()
        finally:
            self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

