from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import Settings


settings = Settings()

engine = create_engine(url=settings.db_url)

Base = declarative_base()
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def db_dependency():
    try:
        db = Session()
    except Exception as e:
        logger.error(f'Error establishing db session:')
        raise e
    try:
        yield db
    finally:
        db.close()



def get_db():
    db = next(db_dependency())
    return db


def init_db():
    Base.metadata.create_all(engine, checkfirst=True)

