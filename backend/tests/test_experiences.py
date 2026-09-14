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


def sample_payload(**overrides):
    payload = {
        "company_id": 1,
        "role_id": 1,
        "college_id": 1,
        "branch": "CSE",
        "graduation_year": 2026,
        "placement_year": 2026,
        "package": "12 LPA",
        "overall_experience": "Great process overall.",
        "preparation_tips": "Focus on DSA and SQL.",
        "additional_advice": "Stay calm.",
        "selected": True,
        "rounds": [
            {
                "round_number": 1,
                "round_type": "Aptitude",
                "description": "Basic quant and logical reasoning",
                "difficulty": "medium",
                "questions": [
                    {"question_text": "Quant problem on time and work", "category": "Aptitude", "topic": "Quant", "difficulty": "medium"}
                ],
            },
            {
                "round_number": 2,
                "round_type": "Technical",
                "description": "DSA and SQL",
                "difficulty": "hard",
                "questions": [
                    {"question_text": "Reverse a linked list", "category": "DSA", "topic": "Linked List", "difficulty": "hard"},
                    {"question_text": "Write an SQL JOIN query", "category": "DBMS", "topic": "SQL", "difficulty": "medium"},
                ],
            },
        ],
    }
    payload.update(overrides)
    return payload


def test_alumni_can_submit_experience(client, db_session):
    token = register(client, role="alumni")
    resp = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert len(data["rounds"]) == 2
    assert len(data["rounds"][1]["questions"]) == 2


def test_student_cannot_submit_experience(client, db_session):
    token = register(client, role="student", email="student@example.com")
    resp = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token))
    assert resp.status_code == 403


def test_role_must_belong_to_company(client, db_session):
    token = register(client, role="alumni")
    resp = client.post("/api/experiences", json=sample_payload(company_id=999), headers=auth_headers(token))
    assert resp.status_code == 400


def test_pending_experience_hidden_from_public_list(client, db_session):
    token = register(client, role="alumni")
    client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token))

    resp = client.get("/api/experiences")
    assert resp.status_code == 200
    assert resp.json() == []


def test_pending_experience_visible_to_owner(client, db_session):
    token = register(client, role="alumni")
    client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token))

    resp = client.get("/api/experiences", headers=auth_headers(token))
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"


def test_pending_experience_hidden_from_other_users(client, db_session):
    token = register(client, role="alumni", email="alumni1@example.com")
    client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token))

    other_token = register(client, role="student", email="student@example.com")
    resp = client.get("/api/experiences", headers=auth_headers(other_token))
    assert resp.json() == []


def test_admin_can_approve_and_it_becomes_public(client, db_session):
    token = register(client, role="alumni")
    exp_id = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token)).json()["id"]

    admin_token = make_admin(db_session, client)
    resp = client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"

    resp2 = client.get("/api/experiences")
    assert len(resp2.json()) == 1


def test_company_experience_count_reflects_approved_only(client, db_session):
    token = register(client, role="alumni")
    exp_id = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token)).json()["id"]

    resp = client.get("/api/companies/1")
    assert resp.json()["experience_count"] == 0

    admin_token = make_admin(db_session, client)
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_token))

    resp2 = client.get("/api/companies/1")
    assert resp2.json()["experience_count"] == 1


def test_owner_can_edit_own_experience_and_it_resets_to_pending(client, db_session):
    token = register(client, role="alumni")
    exp_id = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token)).json()["id"]

    admin_token = make_admin(db_session, client)
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_token))

    resp = client.put(f"/api/experiences/{exp_id}", json=sample_payload(package="15 LPA"), headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["package"] == "15 LPA"
    assert data["status"] == "pending"


def test_other_alumni_cannot_edit_someone_elses_experience(client, db_session):
    token1 = register(client, role="alumni", email="alumni1@example.com")
    exp_id = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token1)).json()["id"]

    token2 = register(client, role="alumni", email="alumni2@example.com")
    resp = client.put(f"/api/experiences/{exp_id}", json=sample_payload(), headers=auth_headers(token2))
    assert resp.status_code == 403


def test_owner_can_delete_own_experience(client, db_session):
    token = register(client, role="alumni")
    exp_id = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token)).json()["id"]

    resp = client.delete(f"/api/experiences/{exp_id}", headers=auth_headers(token))
    assert resp.status_code == 200

    resp2 = client.get(f"/api/experiences/{exp_id}", headers=auth_headers(token))
    assert resp2.status_code == 404


def test_my_experiences_endpoint(client, db_session):
    token = register(client, role="alumni")
    client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token))
    client.post("/api/experiences", json=sample_payload(placement_year=2025), headers=auth_headers(token))

    resp = client.get("/api/experiences/mine", headers=auth_headers(token))
    assert len(resp.json()) == 2


def test_experience_detail_includes_nested_rounds_and_questions(client, db_session):
    token = register(client, role="alumni")
    exp_id = client.post("/api/experiences", json=sample_payload(), headers=auth_headers(token)).json()["id"]

    resp = client.get(f"/api/experiences/{exp_id}", headers=auth_headers(token))
    data = resp.json()
    assert data["rounds"][0]["round_type"] == "Aptitude"
    assert data["rounds"][1]["questions"][0]["question_text"] == "Reverse a linked list"
