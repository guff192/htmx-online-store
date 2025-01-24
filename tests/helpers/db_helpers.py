from sqlalchemy.orm import Session


def add_all_to_db(db_session: Session, objects: list):
    db_session.add_all(objects)
    db_session.commit()

    db_session.flush(objects)


def add_to_db(db_session: Session, db_obj):
    db_session.add(db_obj)
    db_session.commit()

    db_session.flush((db_obj,))


