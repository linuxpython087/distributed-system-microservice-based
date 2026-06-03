from enum import Enum


class OrderStatus(Enum):

    PENDING = "PENDING"

    CONFIRMED = "CONFIRMED"

    RESERVED = "RESERVED"

    SHIPPED = "SHIPPED"

    DELIVERED = "DELIVERED"

    CANCELLED = "CANCELLED"
