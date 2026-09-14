import pytest
from app.models.college import College
from app.models.company import Company
from app.models.role import Role
from tests.helpers import register, make_admin, auth_headers


@pytest.fixture(autouse=True)
def seed(db_session):
    db_session.add(College(name="ABC University", city="Meerut", state="UP"))
    company = Company(name="XYZ Technologies")
    db_session.add(company)
    db_session.flush()
    db_session.add(Role(company_id=company.id, title="Software Developer"))
    db_session.commit()


# --- college routes ---

def test_list_colleges_public(client, db_session):
    resp = client.get("/api/colleges")
    assert resp.status_code == 200
    assert resp.json()[0]["name"] == "ABC University"


def test_create_college_requires_admin(client, db_session):
    token = register(client, role="alumni")
    resp = client.post("/api/colleges", json={"name": "New College"}, headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_can_create_college(client, db_session):
    admin_tok = make_admin(db_session, client)
    resp = client.post("/api/colleges", json={"name": "New College", "city": "Pune", "state": "MH"}, headers=auth_headers(admin_tok))
    assert resp.status_code == 201
    assert resp.json()["name"] == "New College"


def test_create_college_missing_name_rejected(client, db_session):
    admin_tok = make_admin(db_session, client)
    resp = client.post("/api/colleges", json={"city": "Pune"}, headers=auth_headers(admin_tok))
    assert resp.status_code == 400


def test_duplicate_college_name_rejected(client, db_session):
    admin_tok = make_admin(db_session, client)
    resp = client.post("/api/colleges", json={"name": "ABC University"}, headers=auth_headers(admin_tok))
    assert resp.status_code == 409


# --- validation hardening ---

def test_absurd_placement_year_rejected(client, db_session):
    token = register(client, role="alumni")
    resp = client.post("/api/experiences", json={
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 99999, "rounds": [],
    }, headers=auth_headers(token))
    assert resp.status_code == 400


def test_zero_placement_year_rejected(client, db_session):
    token = register(client, role="alumni")
    resp = client.post("/api/experiences", json={
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 0, "rounds": [],
    }, headers=auth_headers(token))
    assert resp.status_code == 400


def test_negative_round_number_rejected(client, db_session):
    token = register(client, role="alumni")
    resp = client.post("/api/experiences", json={
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": [{"round_number": -1, "round_type": "Aptitude", "questions": []}],
    }, headers=auth_headers(token))
    assert resp.status_code == 400


def test_registration_absurd_graduation_year_rejected(client, db_session):
    resp = client.post("/api/auth/register", json={
        "name": "Test User", "email": "weird@example.com", "password": "secret123",
        "role": "student", "college_id": 1, "graduation_year": 1500,
    })
    assert resp.status_code == 400


def test_frequent_topics_limit_is_clamped(client, db_session):
    admin_tok = make_admin(db_session, client)
    alumni_tok = register(client, role="alumni")
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": [{"round_number": 1, "round_type": "Technical", "difficulty": "medium",
                    "questions": [{"question_text": "Q1", "category": "DBMS", "topic": "SQL", "difficulty": "medium"}]}],
    }
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok)).json()["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))

    resp_huge = client.get("/api/questions/frequent?limit=100000")
    assert resp_huge.status_code == 200
    assert len(resp_huge.json()) <= 50

    resp_negative = client.get("/api/questions/frequent?limit=-5")
    assert resp_negative.status_code == 200
