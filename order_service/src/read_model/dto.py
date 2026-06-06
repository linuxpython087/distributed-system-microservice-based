

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class OrderItemView:
    item_id: str
    product_id: str
    quantity: int
    unit_price: float
    currency: str
    subtotal: float



@dataclass
class OrderView:
    order_id: str
    user_id: str
    status: str
    total_amount: int
    currency: str
    items: List[OrderItemView]