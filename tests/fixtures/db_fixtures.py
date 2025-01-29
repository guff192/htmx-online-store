from pytest import fixture

from db.session import get_db


@fixture(scope="function")
def db():
    db_session =  get_db()
    try:
        yield db_session
    finally:
        db_session.commit()
        db_session.close()

