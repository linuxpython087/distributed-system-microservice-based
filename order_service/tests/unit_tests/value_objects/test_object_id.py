import pytest
import uuid

from order_service.src.domain.value_objects.object_ids import (
    UserId,
    ProductId,
    OrderId,
    OrderItemId,
)


@pytest.mark.parametrize("cls", [UserId, ProductId, OrderId, OrderItemId])
def test_all_ids_creation(cls):
    obj = cls.new()

    assert isinstance(obj, cls)
    assert isinstance(obj.value, uuid.UUID)


def test_user_id_creation():
    uid = UserId.new()

    assert isinstance(uid, UserId)
    assert isinstance(uid.value, uuid.UUID)




@pytest.mark.parametrize("cls", [UserId, ProductId, OrderId, OrderItemId])
def test_from_string(cls):
    raw = "12345678-1234-5678-1234-567812345678"

    obj = cls.from_string(raw)

    assert obj.value == uuid.UUID(raw)



def test_str_representation():
    uid = UserId.from_string("12345678-1234-5678-1234-567812345678")

    assert str(uid) == "12345678-1234-5678-1234-567812345678"

def test_id_types_are_not_interchangeable():
    user = UserId.new()
    # print(user.value)
    # print(str(user))
    product = ProductId.new()

    assert type(user) is not type(product)
    assert user != product