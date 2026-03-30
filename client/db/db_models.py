from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from core import settings
from typing import Generator
from sqlalchemy.orm import Session
engine = create_engine(
    settings.db_url,
    echo=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Synchronous database session generator.
    Use it with 'with' or as a dependency in FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
