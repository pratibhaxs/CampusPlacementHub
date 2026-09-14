from app.models.user import User
from app.security import hash_password


def register(client, role="student", email="user@example.com", college_id=1):
    resp = client.post("/api/auth/register", json={
        "name": "Test User", "email": email, "password": "secret123",
        "role": role, "college_id": college_id,
    })
    return resp.json()["token"]


def make_admin(db_session, client, email="admin@example.com"):
    """Seeds an admin directly (equivalent to the old 'register then promote
    in MySQL' flow from the README, but faster for tests)."""
    admin = User(name="Admin", email=email, role="admin", college_id=1)
    admin.password_hash = hash_password("secret123")
    db_session.add(admin)
    db_session.commit()
    resp = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    return resp.json()["token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
