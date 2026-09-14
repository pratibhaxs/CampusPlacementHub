import pytest
from app.models.college import College


@pytest.fixture(autouse=True)
def seed(db_session):
    db_session.add(College(name="ABC University", city="Meerut", state="UP"))
    db_session.commit()


def register_user(client, **overrides):
    payload = {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "password": "secret123",
        "role": "student",
        "college_id": 1,
    }
    payload.update(overrides)
    return client.post("/api/auth/register", json=payload)


def test_register_success(client):
    resp = register_user(client)
    assert resp.status_code == 201
    assert "token" in resp.json()


def test_register_duplicate_email_rejected(client):
    register_user(client)
    resp = register_user(client, name="Someone Else")
    assert resp.status_code == 409


def test_register_cannot_self_assign_admin_role(client):
    resp = register_user(client, role="admin", email="wannabe-admin@example.com")
    assert resp.status_code == 400


def test_login_success(client):
    register_user(client)
    resp = client.post("/api/auth/login", json={"email": "rahul@example.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_wrong_password(client):
    register_user(client)
    resp = client.post("/api/auth/login", json={"email": "rahul@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client):
    token = register_user(client).json()["token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "rahul@example.com"


def test_admin_only_route_blocked_for_student(client):
    token = register_user(client).json()["token"]
    resp = client.post("/api/colleges", json={"name": "New College"},
                        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
