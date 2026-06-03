from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from order_service.src.infrastructure.config import settings

from collections.abc import Generator
from sqlalchemy.orm import Session

DATABASE_URL = (
    f"postgresql://"
    f"{settings.database_user}:"
    f"{settings.database_password}@"
    f"{settings.database_host}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)

engine = create_engine(
    DATABASE_URL,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
