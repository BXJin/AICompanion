from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import create_database_engine
from app.main import create_app
from app.models.base import Base
import app.models  # noqa: F401


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'test.db'}"
    return Settings(database_url=database_url)


@pytest.fixture
def client(test_settings: Settings) -> Generator[TestClient]:
    engine = create_database_engine(test_settings.database_url)
    Base.metadata.create_all(engine)
    with TestClient(create_app(test_settings)) as test_client:
        yield test_client
    Base.metadata.drop_all(engine)

