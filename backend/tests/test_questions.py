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
    company2 = Company(name="Acme Corp")
    db_session.add(company2)
    db_session.flush()
    db_session.add(Role(company_id=company2.id, title="Backend Engineer"))
    db_session.commit()


def submit_and_approve(client, admin_tok, email, company_id, rounds):
    token = register(client, role="alumni", email=email)
    payload = {
        "company_id": company_id, "role_id": 1 if company_id == 1 else 2, "college_id": 1,
        "branch": "CSE", "graduation_year": 2026, "placement_year": 2026,
        "overall_experience": "Good", "rounds": rounds, "selected": True,
    }
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(token)).json()["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))
    return exp_id


def rounds_with_topics(*topics):
    return [{
        "round_number": 1, "round_type": "Technical", "difficulty": "medium",
        "questions": [{"question_text": f"Question about {t}", "category": "DBMS", "topic": t, "difficulty": "medium"} for t in topics],
    }]


def test_frequent_topics_counts_correctly(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("SQL JOIN", "OOP"))
    submit_and_approve(client, admin_tok, "a2@example.com", 1, rounds_with_topics("SQL JOIN", "OOP"))
    submit_and_approve(client, admin_tok, "a3@example.com", 1, rounds_with_topics("SQL JOIN", "Python"))

    resp = client.get("/api/questions/frequent")
    data = resp.json()
    counts = {row["topic"]: row["count"] for row in data}
    assert counts["SQL JOIN"] == 3
    assert counts["OOP"] == 2
    assert counts["Python"] == 1
    assert data[0]["topic"] == "SQL JOIN"


def test_frequent_topics_is_case_insensitive(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("sql join"))
    submit_and_approve(client, admin_tok, "a2@example.com", 1, rounds_with_topics("SQL JOIN"))
    submit_and_approve(client, admin_tok, "a3@example.com", 1, rounds_with_topics("Sql Join"))

    resp = client.get("/api/questions/frequent")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["count"] == 3


def test_frequent_topics_scoped_by_company(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("SQL JOIN"))
    submit_and_approve(client, admin_tok, "a2@example.com", 2, rounds_with_topics("SQL JOIN"))
    submit_and_approve(client, admin_tok, "a3@example.com", 2, rounds_with_topics("SQL JOIN"))

    resp_company1 = client.get("/api/questions/frequent?company_id=1")
    assert resp_company1.json()[0]["count"] == 1

    resp_company2 = client.get("/api/questions/frequent?company_id=2")
    assert resp_company2.json()[0]["count"] == 2


def test_pending_experiences_excluded_from_frequency(client, db_session):
    token = register(client, role="alumni", email="a1@example.com")
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": rounds_with_topics("SQL JOIN"),
    }
    client.post("/api/experiences", json=payload, headers=auth_headers(token))

    resp = client.get("/api/questions/frequent")
    assert resp.json() == []


def test_frequent_topics_respects_limit(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("A", "B", "C"))

    resp = client.get("/api/questions/frequent?limit=2")
    assert len(resp.json()) == 2


def test_list_questions_includes_report_count(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("SQL JOIN"))
    submit_and_approve(client, admin_tok, "a2@example.com", 1, rounds_with_topics("SQL JOIN"))

    resp = client.get("/api/questions")
    data = resp.json()
    assert len(data) == 2
    assert all(q["report_count"] == 2 for q in data)


def test_list_questions_filter_by_category(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("SQL JOIN"))

    resp = client.get("/api/questions?category=DBMS")
    assert len(resp.json()) == 1

    resp2 = client.get("/api/questions?category=HR")
    assert len(resp2.json()) == 0


def test_list_questions_filter_by_company(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", 1, rounds_with_topics("SQL JOIN"))
    submit_and_approve(client, admin_tok, "a2@example.com", 2, rounds_with_topics("OOP"))

    resp = client.get("/api/questions?company_id=1")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["company_name"] == "XYZ Technologies"


def test_list_questions_excludes_pending(client, db_session):
    token = register(client, role="alumni", email="a1@example.com")
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": rounds_with_topics("SQL JOIN"),
    }
    client.post("/api/experiences", json=payload, headers=auth_headers(token))

    resp = client.get("/api/questions")
    assert resp.json() == []
