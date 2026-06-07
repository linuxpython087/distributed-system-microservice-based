
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
            version=row.get("version", None),
            item_count=row["item_count"],
            created_at=row.get("created_at", None),
            last_update=row.get("updated_at", None),
            total_amount=row["total_amount"],
            currency=row["currency"],
            items=items,
            
        )