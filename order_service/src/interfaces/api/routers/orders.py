from fastapi import APIRouter
from fastapi import Depends, status

from order_service.src.interfaces.api.dependencies import get_bus

from order_service.src.interfaces.api.schemas.requests import (
    CreateOrderRequest,AddItemRequest
)

from order_service.src.interfaces.api.schemas.responses import (
    CreateOrderResponse,
)

from order_service.src.application.services import commands

router = APIRouter()
from order_service.src.domain.value_objects.object_ids import UserId, OrderId, OrderItemId

from order_service.src.domain.value_objects.object_ids import OrderId, ProductId
from order_service.src.domain.value_objects.money import Money
@router.post(
    "/",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    request: CreateOrderRequest,
    bus=Depends(get_bus),
):
    cmd = commands.CreateOrderCommand(
        user_id=UserId.from_string(request.user_id)
    )

    result = bus.handle(cmd)

    return CreateOrderResponse(
        order_id=result[0].value
    )


@router.post("/{order_id}/items")
def add_item(
    order_id: str,
    request: AddItemRequest,
    bus=Depends(get_bus),
):
    cmd = commands.AddItemCommand(
        order_id=OrderId.from_string(order_id),
        product_id=ProductId.from_string(request.product_id),
        qty=request.qty,
        unit_price=Money(request.unit_price, "USD"),
    )

    bus.handle(cmd)

    return {"message": "item added"}


@router.delete("/{order_id}/items/{item_id}")
def remove_item(
    order_id: str,
    item_id: str,
    bus=Depends(get_bus),
):
    cmd = commands.RemoveItemCommand(
        order_id=OrderId.from_string(order_id),
        item_id=OrderItemId.from_string(item_id),
    )

    bus.handle(cmd)

    return {"message": "item removed"}


@router.patch("/{order_id}/items/{item_id}/quantity")
def change_item_quantity(
    order_id: str,
    item_id: str,
    qty: int,
    bus=Depends(get_bus),
):
    cmd = commands.ChangeItemQuantityCommand(
        order_id=OrderId.from_string(order_id),
        item_id=OrderItemId.from_string(item_id),
        qty=qty,
    )

    bus.handle(cmd)

    return {"message": "quantity updated"}



@router.post("/{order_id}/confirm", status_code=status.HTTP_201_CREATED)
def confirm_order(
    order_id: str,
    bus=Depends(get_bus),
):
    cmd = commands.ConfirmOrderCommand(
        order_id=OrderId.from_string(order_id),
    )

    bus.handle(cmd)

    return {"message": "order confirmed"}


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: str,
    bus=Depends(get_bus),
):
    cmd = commands.CancelOrderCommand(
        order_id=OrderId.from_string(order_id),
    )

    bus.handle(cmd)

    return {"message": "order cancelled"}