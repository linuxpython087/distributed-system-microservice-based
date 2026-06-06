# # read_model/repository.py

# from sqlalchemy import select
# from order_service.src.infrastructure.orm import orders_table, order_items_table
# from .dto import OrderView, OrderItemView

# from order_service.src.domain.value_objects.object_ids import OrderId, OrderItemId
# class OrderReadRepository:

#     def __init__(self, session):
#         self.session = session

#     def get_order(self, order_id: str) -> OrderView:
#         order_id = OrderId.from_string(order_id)
#         order = self.session.execute(
#             select(orders_table).where(orders_table.c.id == order_id)
#         ).first()

#         items = self.session.execute(
#             select(order_items_table).where(order_items_table.c.order_id == order_id)
#         ).all()

#         total = 0
#         item_views = []

#         for i in items:
#             price = i.unit_price_amount * i.quantity
#             total += price

#             item_views.append(
#                 OrderItemView(
#                     product_id=str(i.product_id),
#                     quantity=i.quantity,
#                     unit_price=i.unit_price_amount,
#                 )
#             )

#         return OrderView(
#             order_id=str(order.id),
#             user_id=str(order.user_id),
#             status=order.status,
#             total=total,
#             items=item_views,
#         )




from sqlalchemy import select
from order_service.src.infrastructure.orm import order_read_model_table
from order_service.src.read_model.dto import OrderView, OrderItemView

from order_service.src.domain.value_objects.object_ids import OrderId
class OrderReadRepository:

    def __init__(self, session):
        self.session = session

    def get_order(self, order_id: str) -> OrderView:
        order_id = OrderId.from_string(order_id)

        row = self.session.execute(
            select(order_read_model_table)
            .where(order_read_model_table.c.order_id == order_id)
        ).mappings().first()

        if not row:
            return None

        items = [
            OrderItemView(
                item_id=i.get("id", None),
                product_id=i["product_id"],
                quantity=i["quantity"],
                unit_price=i["unit_price"],
                currency=i["currency"],
                subtotal=i["subtotal"]
                
            )
            for i in row["items"]
        ]

        return OrderView(
            order_id=row["order_id"],
            user_id=row["user_id"],
            status=row["status"],
            total_amount=row["total_amount"],
            currency=row["currency"],
            items=items
        )