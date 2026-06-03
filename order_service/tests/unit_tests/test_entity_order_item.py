import pytest

from order_service.src.domain.entities.order_item import OrderItem
from order_service.src.domain.exceptions import InvalidQuantity
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.value_objects.object_ids import ProductId


def test_create_order_item():
    item = OrderItem(product_id=ProductId.new(), qty=2, unit_price=Money(10, "USD"))

    assert isinstance(item.product_id, ProductId)
    assert item.unit_price.amount == 10


@pytest.fixture
def create_item():
    return OrderItem(product_id=ProductId.new(), qty=2, unit_price=Money(10, "USD"))


def test_order_item_subtotal():
    item = OrderItem(product_id=ProductId.new(), qty=3, unit_price=Money(10, "USD"))

    subtotal = item.subtotal()

    assert subtotal.amount == 30
    assert subtotal.currency == "USD"


@pytest.mark.parametrize(
    "qty",
    [0, -5],
)
def test_create_order_item_with_invalid_quantity(qty):
    with pytest.raises(InvalidQuantity, match="Quantity must be greater than zero"):
        OrderItem(product_id=ProductId.new(), qty=qty, unit_price=Money(10, "USD"))


def test_change_item_quantity(create_item):
    item = create_item
    item.change_quantity(20)

    assert item.quantity == 20


@pytest.mark.parametrize("qty", [0, -1, -10])
def test_change_item_quantity_with_invalid_quantity(create_item, qty):
    with pytest.raises(InvalidQuantity, match="Quantity must be greater than zero"):
        create_item.change_quantity(qty)
