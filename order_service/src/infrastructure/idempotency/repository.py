from sqlalchemy import select, insert, update, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from order_service.src.infrastructure.orm import idempotency_table
import uuid


from order_service.src.domain.value_objects.object_ids import IdempotencyId
class IdempotencyRepository:

    def __init__(self, session: Session):
        self.session = session

    # =====================================================
    # 1. GET BY KEY
    # =====================================================
    def get_by_key(self, key: str):
        query = select(idempotency_table).where(
            idempotency_table.c.key == key
        )
        result =  self.session.execute(query)
        return result.mappings().first()

    # =====================================================
    # 2. SAFE GET OR CREATE (VERY IMPORTANT IN DISTRIBUTED SYSTEMS)
    # =====================================================
    def create(
        self,
        key: str,
        user_id: str,
        request_path: str,
        params: dict
    ):
        """
        Prevent race conditions when multiple requests arrive
        at the same time (retry / double submit).
        """

        stmt = pg_insert(idempotency_table).values(
             id=IdempotencyId.new(),
            key=key,
            user_id=user_id,
            request_path=request_path,
            request_params=params,
            status="processing",
            retry_count=0,
            created_at=func.now()
        ).on_conflict_do_nothing(
            index_elements=["key"]
        )

        self.session.execute(stmt)
        self.session.commit()

        return  self.get_by_key(key)

    # =====================================================
    # 3. MARK AS PROCESSING (LOCK ACQUIRE)
    # =====================================================
    def mark_processing(self, key: str):
        query = (
            update(idempotency_table)
            .where(idempotency_table.c.key == key)
            .values(
                status="processing",
                locked_at=func.now(),
                retry_count=idempotency_table.c.retry_count + 1
            )
        )
        self.session.execute(query)
        self.session.commit()

    # =====================================================
    # 4. MARK COMPLETED (SUCCESS STATE)
    # =====================================================
    def mark_completed(
        self,
        key: str,
        response_code: int,
        response_body: dict,
        order_id: str
    ):
        query = (
            update(idempotency_table)
            .where(idempotency_table.c.key == key)
            .values(
                status="completed",
                response_code=response_code,
                response_body=response_body,
                order_id=order_id,
                locked_at=None,
  
            )
        )
        self.session.execute(query)
        self.session.commit()

    # =====================================================
    # 5. MARK FAILED (ERROR STATE)
    # =====================================================
    def mark_failed(
        self,
        key: str,
        error_message: str
    ):
        query = (
            update(idempotency_table)
            .where(idempotency_table.c.key == key)
            .values(
                status="failed",
                error_message=error_message,
                locked_at=None,
              
            )
        )
        self.session.execute(query)
        self.session.commit()

    # =====================================================
    # 6. GET COMPLETED RESULT (FOR REPLAY SAFETY)
    # =====================================================
    def get_completed_result(self, key: str):
        query = select(
            idempotency_table.c.status,
            idempotency_table.c.response_code,
            idempotency_table.c.response_body,
            idempotency_table.c.order_id,
        ).where(
            idempotency_table.c.key == key
        )

        result =  self.session.execute(query)
        return result.mappings().first()

    # =====================================================
    # 7. CHECK IF IN PROGRESS
    # =====================================================
    def is_processing(self, key: str) -> bool:
        query = select(idempotency_table.c.status).where(
            idempotency_table.c.key == key
        )
        result =  self.session.execute(query)
        row = result.first()

        if not row:
            return False

        return row[0] == "processing"

    # =====================================================
    # 8. RECOVERY POINT UPDATE (ADVANCED WORKFLOW SUPPORT)
    # =====================================================
    def set_recovery_point(self, key: str, step: str):
        query = (
            update(idempotency_table)
            .where(idempotency_table.c.key == key)
            .values(
                recovery_point=step,
              
            )
        )
        self.session.execute(query)

    # =====================================================
    # 9. CLEANUP EXPIRED KEYS (OPTIONAL MAINTENANCE)
    # =====================================================
    def delete_expired(self):
        query = (
            update(idempotency_table)
            .where(idempotency_table.c.expires_at < func.now())
            .values(status="expired")
        )
        self.session.execute(query)
        self.session.commit()