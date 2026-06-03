from order_service.src.domain.value_objects.object_ids import OrderId


class FakeOrderRepository:

    def __init__(self):
        self.orders = {}

    def add(self, order):
        self.orders[order.id] = order

    def get(self, order_id: OrderId):
        return self.orders.get(order_id)

    def remove(self, order):
        self.orders.pop(order.id, None)
