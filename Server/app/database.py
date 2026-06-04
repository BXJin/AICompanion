from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


@lru_cache
def create_database_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


@lru_cache
def create_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(bind=create_database_engine(database_url), autoflush=False, autocommit=False, future=True)


def create_session(settings: Settings) -> Session:
    return create_session_factory(settings.database_url)()


def session_scope(settings: Settings) -> Generator[Session]:
    session = create_session(settings)
    try:
        yield session
    finally:
        session.close()

