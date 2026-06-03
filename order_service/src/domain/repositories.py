from typing import Protocol

from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.object_ids import OrderId


class OrderRepository(Protocol):

    def add(self, order: Order) -> None: ...

    def get(self, order_id: OrderId) -> Order | None: ...

    def remove(self, order: Order) -> None: ...
