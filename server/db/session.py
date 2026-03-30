from contextlib import contextmanager
from db.db_models import SessionLocal
from repositories.auth_repo import AuthRepository


@contextmanager
def get_repository():
    db = SessionLocal()
    try:
        yield AuthRepository(db)
    finally:
        db.close()
