import pytest
from order_service.src.infrastructure.mapper import start_mappers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from order_service.src.infrastructure.config import settings
from alembic import command
from alembic.config import Config

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://"
    f"{settings.database_user}:"
    f"{settings.database_password}@"
    f"{settings.database_host}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)


@pytest.fixture()
def apply_migrations():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

    # clean start (IMPORTANT)
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session_factory(apply_migrations):
    connection = apply_migrations.connect()
    transaction = connection.begin()

    Session = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,  
    )

    yield Session

    transaction.rollback()
    connection.close()


@pytest.fixture
def session(apply_migrations):

    connection = apply_migrations.connect()

    transaction = connection.begin()

    Session = sessionmaker(bind=connection)

    session = Session()

    yield session

    session.close()

    transaction.rollback()

    connection.close()


@pytest.fixture(autouse=True)
def mappers():
    start_mappers()
    yield
    clear_mappers()
