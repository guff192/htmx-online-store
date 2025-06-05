from pytest import fixture
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from db.session import Base, get_db


settings = Settings()


@fixture(scope="session")
def engine() -> Engine:
    return create_engine(url=settings.db_url)


@fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@fixture(scope="function")
def db_session(engine: Engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

