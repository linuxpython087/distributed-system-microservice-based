from order_service.src.infrastructure.orm import order_read_model_table


class OrderProjector:

    def __init__(self, session):
        self.session = session

    def project(self, order):
        """
        order = aggregate domain (WRITE MODEL)
        """

        items = []

        for item in order.items.values():
            subtotal = item.subtotal()

            items.append({
                "id": str(item.id),
                "product_id": str(item.product_id),
                "quantity": item.quantity,
                "unit_price": item.unit_price.amount,
                "subtotal": subtotal.amount,
                "currency": subtotal.currency,
                
            })

        total = order.total()
        

        row = {
            "order_id": order.id,
            "user_id": order.user_id,
            "status": order.status.value,
            "total_amount": total.amount,
            "currency": total.currency,
            "items": items,
            "version": order.version,
        }

        # UPSERT (très important)
        existing = self.session.execute(
            order_read_model_table.select().where(
                order_read_model_table.c.order_id == order.id
            )
        ).first()

        if existing:
            self.session.execute(
                order_read_model_table.update()
                .where(order_read_model_table.c.order_id == order.id)
                .values(**row)
            )
        else:
            self.session.execute(
                order_read_model_table.insert().values(**row)
            )

        self.session.commit()