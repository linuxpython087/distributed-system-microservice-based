from fastapi import APIRouter
from fastapi import Depends, status, Header

from order_service.src.interfaces.api.dependencies import get_bus

from order_service.src.interfaces.api.schemas.requests import (
    CreateOrderRequest,
    AddItemRequest,
    ChangeQuantityRequest,
)

from order_service.src.interfaces.api.schemas.responses import (
    CreateOrderResponse,
    AddItemResponse,
    CancelOrderResponse,
    ChangeQuantityResponse,
    ConfirmOrderResponse,
)

from order_service.src.application.services import commands


from order_service.src.domain.value_objects.object_ids import (
    UserId,
    OrderId,
    OrderItemId,
    ProductId,
)

from order_service.src.domain.value_objects.money import Money

from order_service.src.application.services.idempotency_service import (
    IdempotencyService,
)
import uuid

router = APIRouter()


@router.post(
    "/", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED
)
def create_order(
    request: CreateOrderRequest,
    bus=Depends(get_bus),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    # =========================================
    # 1. AUTO-GENERATE IF MISSING
    # =========================================
    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())

    with bus.uow:

        service = IdempotencyService(bus.uow)

        cmd = commands.CreateOrderCommand(user_id=UserId.from_string(request.user_id))

        def run():
            return bus.handle(cmd)

        result = service.execute(
            key=idempotency_key,
            user_id=cmd.user_id,
            request_path="/orders",
            request_params=cmd.to_dict(),
            callback=run,
        )

        # result = bus.handle(cmd)

        return CreateOrderResponse(
            order_id=result["result"][0],
            idempotency_key=idempotency_key,
        )


@router.post(
    "/{order_id}/items",
    response_model=AddItemResponse,
    status_code=status.HTTP_201_CREATED,
)
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

    result = bus.handle(cmd)

    return AddItemResponse(item_id=str(result[0].value), message="Item Added")


@router.delete(
    "/{order_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
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

    return {"ùessage": "item removed"}


@router.patch(
    "/{order_id}/items/{item_id}/quantity",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ChangeQuantityResponse,
)
def change_item_quantity(
    order_id: str,
    item_id: str,
    request: ChangeQuantityRequest,
    bus=Depends(get_bus),
):
    cmd = commands.ChangeItemQuantityCommand(
        order_id=OrderId.from_string(order_id),
        item_id=OrderItemId.from_string(item_id),
        qty=request.qty,
    )

    bus.handle(cmd)

    return ChangeQuantityResponse(message="quantity updated")


@router.post(
    "/{order_id}/confirm",
    status_code=status.HTTP_201_CREATED,
    response_model=ConfirmOrderResponse,
)
def confirm_order(
    order_id: str,
    bus=Depends(get_bus),
):
    cmd = commands.ConfirmOrderCommand(
        order_id=OrderId.from_string(order_id),
    )

    bus.handle(cmd)

    return ConfirmOrderResponse(message="order confirmed")


@router.post(
    "/{order_id}/cancel",
    status_code=status.HTTP_201_CREATED,
    response_model=CancelOrderResponse,
)
def cancel_order(
    order_id: str,
    bus=Depends(get_bus),
):
    cmd = commands.CancelOrderCommand(
        order_id=OrderId.from_string(order_id),
    )

    bus.handle(cmd)

    return CancelOrderResponse(message=f"Order: {order_id} Cancelled")
