from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import Settings


settings = Settings()

engine = create_engine(settings.db_url)

Base = declarative_base()
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def db_dependency():
    try:
        db = Session()
        yield db
    except Exception as e:
        print(f'Error establishing db session: {e}')
    else:
        db.close()


def get_db():
    db = Session()
    return db


def init_db():
    Base.metadata.create_all(engine, checkfirst=True)

