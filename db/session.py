from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import Settings


settings = Settings()

engine = create_engine(settings.DB_URL)

Base = declarative_base()
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    try:
        db = Session()
        yield db
    except Exception as e:
        print(f'Error establishing db session: {e}')
    else:
        db.close()

def init_db():
    Base.metadata.create_all(engine, checkfirst=True)

