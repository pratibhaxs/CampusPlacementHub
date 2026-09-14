import pytest
from app.models.college import College
from app.models.company import Company
from app.models.role import Role
from tests.helpers import register, make_admin, auth_headers


@pytest.fixture(autouse=True)
def seed(db_session):
    db_session.add(College(name="ABC University", city="Meerut", state="UP"))
    db_session.add(College(name="XYZ Institute", city="Delhi", state="DL"))
    company = Company(name="XYZ Technologies")
    db_session.add(company)
    db_session.flush()
    db_session.add(Role(company_id=company.id, title="Software Developer"))
    db_session.add(Role(company_id=company.id, title="Data Analyst"))
    db_session.commit()


def submit_and_approve(client, admin_tok, **overrides):
    email_suffix = overrides.pop("_email_suffix", "1")
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "branch": "CSE",
        "graduation_year": 2026, "placement_year": 2026, "package": "10 LPA",
        "overall_experience": "Good", "preparation_tips": "Practice",
        "additional_advice": "Relax", "selected": True,
        "rounds": [
            {"round_number": 1, "round_type": "Aptitude", "description": "Quant", "difficulty": "medium",
             "questions": [{"question_text": "Q1", "category": "Aptitude", "topic": "Quant", "difficulty": "medium"}]},
            {"round_number": 2, "round_type": "Technical", "description": "SQL", "difficulty": "hard",
             "questions": [{"question_text": "SQL join query", "category": "DBMS", "topic": "SQL JOIN", "difficulty": "medium"}]},
        ],
    }
    payload.update(overrides)
    alumni_tok = register(client, role="alumni", email=f"alumni{email_suffix}@example.com", college_id=payload["college_id"])
    resp = client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok))
    exp_id = resp.json()["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))
    return exp_id


def test_filter_by_college(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, college_id=1, _email_suffix="1")
    submit_and_approve(client, admin_tok, college_id=2, _email_suffix="2")

    resp = client.get("/api/experiences?college_id=1")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["college_id"] == 1


def test_filter_by_role(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, role_id=1, _email_suffix="1")
    submit_and_approve(client, admin_tok, role_id=2, _email_suffix="2")

    resp = client.get("/api/experiences?role_id=2")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["role_title"] == "Data Analyst"


def test_filter_by_year(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, placement_year=2025, _email_suffix="1")
    submit_and_approve(client, admin_tok, placement_year=2026, _email_suffix="2")

    resp = client.get("/api/experiences?year=2025")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["placement_year"] == 2025


def test_filter_by_branch_partial_match(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, branch="Computer Science", _email_suffix="1")
    submit_and_approve(client, admin_tok, branch="Mechanical", _email_suffix="2")

    resp = client.get("/api/experiences?branch=computer")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["branch"] == "Computer Science"


def test_filter_by_round_difficulty_no_duplicate_rows(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, _email_suffix="1")

    resp = client.get("/api/experiences?difficulty=hard")
    assert len(resp.json()) == 1


def test_filter_by_round_type(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, _email_suffix="1")

    resp = client.get("/api/experiences?round_type=technical")
    assert len(resp.json()) == 1

    resp2 = client.get("/api/experiences?round_type=hr")
    assert len(resp2.json()) == 0


def test_filter_by_topic(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, _email_suffix="1")

    resp = client.get("/api/experiences?topic=sql")
    assert len(resp.json()) == 1

    resp2 = client.get("/api/experiences?topic=nonexistent")
    assert len(resp2.json()) == 0


def test_combined_filters(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, college_id=1, placement_year=2026, _email_suffix="1")
    submit_and_approve(client, admin_tok, college_id=1, placement_year=2025, _email_suffix="2")
    submit_and_approve(client, admin_tok, college_id=2, placement_year=2026, _email_suffix="3")

    resp = client.get("/api/experiences?college_id=1&year=2026")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["college_id"] == 1
    assert data[0]["placement_year"] == 2026


def test_topic_and_difficulty_combined_does_not_500(client, db_session):
    """Regression test carried over from the Flask version — combining topic
    and difficulty filters previously caused a duplicate JOIN bug there."""
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, _email_suffix="1")

    resp = client.get("/api/experiences?topic=sql&difficulty=hard")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp2 = client.get("/api/experiences?topic=sql&difficulty=easy")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


def test_topic_round_type_and_difficulty_all_combined(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, _email_suffix="1")

    resp = client.get("/api/experiences?topic=sql&round_type=technical&difficulty=hard")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
