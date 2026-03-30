from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from core import settings

engine = create_engine(
    settings.db_url,
    echo=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)


class Base(DeclarativeBase):
    pass
