from order_service.src.domain.order_status import OrderStatus

ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: [
        OrderStatus.CONFIRMED,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.CONFIRMED: [
        OrderStatus.RESERVED,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.RESERVED: [
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.SHIPPED: [
        OrderStatus.DELIVERED,
    ],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}
