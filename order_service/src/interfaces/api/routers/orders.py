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

from order_service.src.domain.exceptions import (
    DomainException,
)

import structlog

logger = structlog.get_logger()


router = APIRouter()


@router.post(
    "/", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED
)
def create_order(
    request: CreateOrderRequest,
    bus=Depends(get_bus),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    try:

        # =========================================
        # 1. AUTO-GENERATE IF MISSING
        # =========================================
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())

        with bus.uow:

            service = IdempotencyService(bus.uow)

            cmd = commands.CreateOrderCommand(
                user_id=UserId.from_string(request.user_id)
            )

            def run():
                return bus.handle(cmd)

            logger.info(
                "create_order_started",
                user_id=str(cmd.user_id),
                idempotency_key=idempotency_key,
            )
            result = service.execute(
                key=idempotency_key,
                user_id=cmd.user_id,
                request_path="/orders",
                request_params=cmd.to_dict(),
                callback=run,
            )

            # result = bus.handle(cmd)
            logger.info(
                "order_created",
                order_id=str(result["result"][0]),
                user_id=str(cmd.user_id),
                idempotency_key=idempotency_key,
            )

            return CreateOrderResponse(
                order_id=result["result"][0],
                idempotency_key=idempotency_key,
            )
    except DomainException as d:
        logger.warning(
            "create_order_business_failed", error=str(d), user_id=request.user_id
        )
        raise
    except Exception as e:
        logger.exception("create_order_failed", error=str(e))
        raise


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
    try:
        cmd = commands.AddItemCommand(
            order_id=OrderId.from_string(order_id),
            product_id=ProductId.from_string(request.product_id),
            qty=request.qty,
            unit_price=Money(request.unit_price, "USD"),
        )

        logger.info(
            "add_item_started",
            order_id=order_id,
            product_id=request.product_id,
            qty=request.qty,
        )

        result = bus.handle(cmd)
        logger.info(
            "item_added",
            order_id=order_id,
            item_id=str(result[0]),
            product_id=request.product_id,
            qty=request.qty,
            unit_price=request.unit_price,
        )

        return AddItemResponse(item_id=str(result[0].value), message="Item Added")

    except DomainException as d:
        logger.warning("add_item_business_failed", error=str(d), order_id=order_id)
        raise
    except Exception as e:
        logger.exception("add_item_failed", error=str(e), order_id=order_id)
        raise


@router.delete(
    "/{order_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_item(
    order_id: str,
    item_id: str,
    bus=Depends(get_bus),
):
    try:
        cmd = commands.RemoveItemCommand(
            order_id=OrderId.from_string(order_id),
            item_id=OrderItemId.from_string(item_id),
        )

        logger.info("remove_item_started", order_id=order_id, item_id=item_id)

        bus.handle(cmd)
        logger.info("item_removed", order_id=order_id, item_id=item_id)

        return {"ùessage": "item removed"}

    except DomainException as d:
        logger.warning(
            "remove_item_business_failed",
            error=str(d),
            order_id=order_id,
            item_id=item_id,
        )
        raise
    except Exception as e:
        logger.exception(
            "remove_item_failed", order_id=order_id, error=str(e), item_id=item_id
        )
        raise


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
    try:
        cmd = commands.ChangeItemQuantityCommand(
            order_id=OrderId.from_string(order_id),
            item_id=OrderItemId.from_string(item_id),
            qty=request.qty,
        )
        logger.info(
            "change_quantity_started",
            order_id=order_id,
            item_id=item_id,
            new_quantity=request.qty,
        )

        bus.handle(cmd)
        logger.info(
            "quantity_changed", order_id=order_id, item_id=item_id, qty=request.qty
        )

        return ChangeQuantityResponse(message="quantity updated")
    except DomainException as d:
        logger.warning(
            "change_quantity_business_failed", error=str(d), order_id=order_id
        )
        raise
    except Exception as e:
        logger.exception("change_quantity_failed", error=str(e), order_id=order_id)
        raise


@router.post(
    "/{order_id}/confirm",
    status_code=status.HTTP_201_CREATED,
    response_model=ConfirmOrderResponse,
)
def confirm_order(
    order_id: str,
    bus=Depends(get_bus),
):
    try:

        cmd = commands.ConfirmOrderCommand(
            order_id=OrderId.from_string(order_id),
        )
        logger.info("confirm_order_started", order_id=order_id)

        bus.handle(cmd)
        logger.info("order_confirmed", order_id=order_id)

        return ConfirmOrderResponse(message="order confirmed")

    except DomainException as d:
        logger.warning("confirm_order_business_failed", error=str(d), order_id=order_id)
        raise
    except Exception as e:
        logger.exception("confirm_order_failed", error=str(e), order_id=order_id)
        raise


@router.post(
    "/{order_id}/cancel",
    status_code=status.HTTP_201_CREATED,
    response_model=CancelOrderResponse,
)
def cancel_order(
    order_id: str,
    bus=Depends(get_bus),
):
    try:
        cmd = commands.CancelOrderCommand(
            order_id=OrderId.from_string(order_id),
        )
        logger.info("cancel_order_started", order_id=order_id)

        bus.handle(cmd)
        logger.info("order_cancelled", order_id=order_id)

        return CancelOrderResponse(message=f"Order: {order_id} Cancelled")

    except DomainException as d:
        logger.warning("cancel_order_business_failed", error=str(d), order_id=order_id)
        raise

    except Exception as e:
        logger.exception("cancel_order_failed", error=str(e), order_id=order_id)
        raise
