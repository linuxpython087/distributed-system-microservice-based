

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

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
    version:int
    item_count:int
    total_amount: int
    currency: str
    items: List[OrderItemView]
    created_at: datetime
    last_update: datetime
