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


def submit_and_approve_experience(client, admin_tok):
    alumni_tok = register(client, role="alumni", email="alumni@example.com")
    payload = {"company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026, "rounds": []}
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok)).json()["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))
    return exp_id


def test_student_can_mark_helpful(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    resp = client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(student_tok))
    assert resp.status_code == 200
    data = resp.json()
    assert data["helpful_count"] == 1
    assert data["user_has_voted_helpful"] is True


def test_toggling_helpful_again_removes_vote(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(student_tok))
    resp = client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(student_tok))
    data = resp.json()
    assert data["helpful_count"] == 0
    assert data["user_has_voted_helpful"] is False


def test_multiple_students_votes_accumulate(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    tok1 = register(client, email="s1@example.com")
    tok2 = register(client, email="s2@example.com")

    client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(tok1))
    resp = client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(tok2))
    assert resp.json()["helpful_count"] == 2


def test_alumni_cannot_vote_helpful(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    alumni_tok = register(client, role="alumni", email="alumni2@example.com")

    resp = client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(alumni_tok))
    assert resp.status_code == 403


def test_experience_list_includes_helpful_count(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)
    client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(student_tok))

    resp = client.get("/api/experiences", headers=auth_headers(student_tok))
    data = resp.json()
    assert data[0]["helpful_count"] == 1
    assert data[0]["user_has_voted_helpful"] is True


def test_cannot_vote_on_pending_experience(client, db_session):
    alumni_tok = register(client, role="alumni", email="alumni3@example.com")
    payload = {"company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026, "rounds": []}
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok)).json()["id"]

    student_tok = register(client)
    resp = client.post(f"/api/experiences/{exp_id}/helpful", headers=auth_headers(student_tok))
    assert resp.status_code == 404
