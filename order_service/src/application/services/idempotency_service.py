from typing import Callable, Any

from order_service.src.application.services.unit_of_work import (
    AbstractOrderUnitOfWork,
)


class IdempotencyService:

    def __init__(self, uow: AbstractOrderUnitOfWork):
        self.uow = uow

    def execute(
        self,
        *,
        key: str,
        user_id,
        request_path: str,
        request_params: dict,
        callback: Callable[[], Any],
    ):

        existing = self.uow.idempotency.get_by_key(key)

        # ==========================================
        # COMPLETED
        # ==========================================

        if existing and existing["status"] == "completed":

            return existing["response_body"]

        # ==========================================
        # PROCESSING
        # ==========================================

        if existing and existing["status"] == "processing":

            raise RuntimeError(f"Request with key '{key}' is already processing")

        # ==========================================
        # CREATE RECORD
        # ==========================================

        self.uow.idempotency.create(
            key=key,
            user_id=user_id,
            request_path=request_path,
            params=request_params,
        )

        try:

            result = callback()

            # ======================================
            # SERIALIZE RESPONSE
            # ======================================

            response_body = self._serialize_result(result)

            order_id = self._extract_order_id(result)

            self.uow.idempotency.mark_completed(
                key=key,
                response_code=201,
                response_body=response_body,
                order_id=order_id,
            )

            self.uow.commit()

            return response_body

        except Exception as exc:

            self.uow.idempotency.mark_failed(
                key=key,
                error_message=str(exc),
            )

            self.uow.commit()

            raise

    # ==========================================
    # HELPERS
    # ==========================================

    def _serialize_result(self, result):

        if result is None:
            return {}

        if isinstance(result, list):

            serialized = []

            for item in result:

                if hasattr(item, "value"):
                    serialized.append(str(item.value))

                else:
                    serialized.append(str(item))

            return {"result": serialized}

        if hasattr(result, "value"):

            return {"result": str(result.value)}

        return {"result": str(result)}

    def _extract_order_id(self, result):

        if isinstance(result, list):

            if not result:
                return None

            first = result[0]

            if hasattr(first, "value"):
                return first

            return None

        if hasattr(result, "value"):
            return result

        return None
