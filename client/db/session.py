from contextlib import contextmanager
from db.db_models import SessionLocal
from repositories import TodoRepository


@contextmanager
def get_repository():
    db = SessionLocal()
    try:
        yield TodoRepository(db)
    finally:
        db.close()
