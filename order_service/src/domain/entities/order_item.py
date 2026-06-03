from order_service.src.domain.exceptions import InvalidQuantity
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.value_objects.object_ids import OrderItemId, ProductId


class OrderItem:

    def __init__(
        self,
        product_id: ProductId,
        qty: int,
        unit_price: Money,
        item_id: OrderItemId = None,
    ):
        self.id = item_id or OrderItemId.new()

        self.product_id = product_id

        self._validate_quantity(qty)
        self._quantity = qty

        self.unit_price = unit_price

    @property
    def quantity(self):
        return self._quantity

    def _validate_quantity(self, qty):
        if qty <= 0:
            raise InvalidQuantity("Quantity must be greater than zero")

    def change_quantity(self, qty):
        self._validate_quantity(qty)
        self._quantity = qty

    def subtotal(self) -> Money:
        return self.unit_price.multiply(self._quantity)
