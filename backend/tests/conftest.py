import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def db_session(app):
    """A session bound to the exact same in-memory DB the app's requests use
    (StaticPool keeps them on one shared connection) — for seeding fixture
    data before making requests through the client."""
    session = app.state.SessionLocal()
    try:
        yield session
    finally:
        session.close()
