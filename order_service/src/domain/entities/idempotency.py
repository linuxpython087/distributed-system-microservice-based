from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import IdempotencyId, OrderId, UserId


@dataclass
class IdempotencyRecord:

    id: IdempotencyId

    key: str

    user_id: UserId

    request_path: str

    request_params: dict

    status: str

    response_code: int | None = None

    response_body: dict | None = None

    recovery_point: str | None = None

    retry_count: int = 0

    order_id: OrderId | None = None