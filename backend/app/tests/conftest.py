import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""Pytest configuration and fixtures for API integration tests"""

# Ensure the backend root is on sys.path so 'app' package is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)           # .../backend/app
BACKEND_ROOT = os.path.dirname(APP_DIR)          # .../backend
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.main import app
from app.db.session import engine as app_engine, get_db
from app.db.base import Base

# Dependency override for DB: use the existing engine but wrap each test in a transaction

@pytest.fixture(scope="session")
def _engine():
    # Use the same engine configured by the app (assumes a test DB or isolated schema)
    return app_engine


@pytest.fixture()
def db_session(_engine):
    connection = _engine.connect()
    trans = connection.begin()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# Fake QueryEngine to avoid external calls during tests
class _FakeQueryEngine:
    async def process_query(self, query: str, fund_id=None, conversation_history=None):
        return {
            "answer": f"Echo: {query}",
            "sources": [],
            "metrics": {"tokens": 10},
            "processing_time": 0.01,
        }


def _get_fake_query_engine_service():
    return _FakeQueryEngine()


@pytest.fixture()
def client_with_fake_query(client):
    # Late import to avoid circulars
    from app.services.query_engine import get_query_engine_service

    app.dependency_overrides[get_query_engine_service] = _get_fake_query_engine_service
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_query_engine_service, None)
