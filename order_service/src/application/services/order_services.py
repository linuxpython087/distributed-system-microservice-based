
from order_service.src.application.services.unit_of_work import SqlAlchemyOrderUnitOfWork, AbstractOrderUnitOfWork
from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus



from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
    OrderId
)

def create_order(
    user_id: UserId,
    uow: AbstractOrderUnitOfWork
) -> OrderId:

    with uow:

        order = Order(user_id=user_id)

        uow.orders.add(order)

        uow.commit()

        return order.id
    

def confirm_order(
    order_id: OrderId,
    uow: AbstractOrderUnitOfWork
):

    with uow:

        order = uow.orders.get(order_id)

        if order is None:
            raise

        order.confirm()

        uow.commit()



def add_item_to_order(
    order_id: OrderId,
    product_id: ProductId,
    qty: int,
    unit_price: Money,
    uow: AbstractOrderUnitOfWork
):

    with uow:

        order = uow.orders.get(order_id)

        if order is None:
            raise 

        order.add_item(
            product_id,
            qty,
            unit_price
        )

        uow.commit()