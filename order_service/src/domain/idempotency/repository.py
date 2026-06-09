# domain/idempotency/repository.py

from typing import Protocol


class AbstractIdempotencyRepository(Protocol):

    def acquire_lock(
        self,
        *,
        key: str,
        user_id,
        request_path: str,
        params: dict,
    ): ...

    def get_by_key(self, key: str): ...

    def mark_completed(
        self,
        *,
        key: str,
        response_code: int,
        response_body: dict,
        order_id,
    ): ...

    def mark_failed(
        self,
        *,
        key: str,
        error_message: str,
    ): ...

    def set_recovery_point(
        self,
        *,
        key: str,
        recovery_point: str,
    ): ...

    def get_completed_result(
        self,
        key: str,
    ): ...

    def cleanup_expired(self): ...
