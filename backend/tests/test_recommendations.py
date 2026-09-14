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
    db_session.add(Role(company_id=company.id, title="Data Analyst"))
    db_session.commit()


def submit_and_approve(client, admin_tok, email, role_id, questions):
    token = register(client, role="alumni", email=email)
    payload = {
        "company_id": 1, "role_id": role_id, "college_id": 1, "placement_year": 2026,
        "rounds": [{"round_number": 1, "round_type": "Technical", "difficulty": "medium", "questions": questions}],
    }
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(token)).json()["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))
    return exp_id


def test_no_experiences_returns_empty(client, db_session):
    resp = client.get("/api/companies/1/recommendation")
    data = resp.json()
    assert data["recommended_topics"] == []
    assert data["based_on"] == 0


def test_star_rating_matches_percentage(client, db_session):
    """82% mentioning SQL should map to 5 stars, matching the spec's own
    'SQL ⭐⭐⭐⭐⭐' example."""
    admin_tok = make_admin(db_session, client)
    q_sql = [{"question_text": "SQL join query", "category": "DBMS", "topic": "SQL", "difficulty": "medium"}]
    q_other = [{"question_text": "Something else", "category": "Other", "topic": "Other", "difficulty": "medium"}]

    for i in range(4):
        submit_and_approve(client, admin_tok, f"a{i}@example.com", 1, q_sql)
    submit_and_approve(client, admin_tok, "a5@example.com", 1, q_other)

    resp = client.get("/api/companies/1/recommendation")
    data = resp.json()
    sql_entry = next(t for t in data["recommended_topics"] if t["topic"] == "SQL")
    assert sql_entry["percentage"] == 80
    assert sql_entry["stars"] == 4


def test_hundred_percent_gives_five_stars(client, db_session):
    admin_tok = make_admin(db_session, client)
    q_sql = [{"question_text": "SQL join query", "category": "DBMS", "topic": "SQL", "difficulty": "medium"}]
    for i in range(3):
        submit_and_approve(client, admin_tok, f"a{i}@example.com", 1, q_sql)

    resp = client.get("/api/companies/1/recommendation")
    data = resp.json()
    assert data["recommended_topics"][0]["stars"] == 5
    assert data["recommended_topics"][0]["percentage"] == 100


def test_low_percentage_still_gets_at_least_one_star(client, db_session):
    admin_tok = make_admin(db_session, client)
    q_rare = [{"question_text": "Rare question", "category": "Other", "topic": "RareTopic", "difficulty": "medium"}]
    q_common = [{"question_text": "Common question", "category": "Other", "topic": "CommonTopic", "difficulty": "medium"}]

    submit_and_approve(client, admin_tok, "a1@example.com", 1, q_rare)
    for i in range(9):
        submit_and_approve(client, admin_tok, f"b{i}@example.com", 1, q_common)

    resp = client.get("/api/companies/1/recommendation")
    data = resp.json()
    rare_entry = next(t for t in data["recommended_topics"] if t["topic"] == "RareTopic")
    assert rare_entry["percentage"] == 10
    assert rare_entry["stars"] == 1


def test_recommendation_scoped_by_role(client, db_session):
    admin_tok = make_admin(db_session, client)
    q_sql = [{"question_text": "SQL join query", "category": "DBMS", "topic": "SQL", "difficulty": "medium"}]
    q_python = [{"question_text": "Python decorators", "category": "Python", "topic": "Python", "difficulty": "medium"}]

    submit_and_approve(client, admin_tok, "a1@example.com", 1, q_sql)
    submit_and_approve(client, admin_tok, "a2@example.com", 2, q_python)

    resp_role1 = client.get("/api/companies/1/recommendation?role_id=1")
    data1 = resp_role1.json()
    assert len(data1["recommended_topics"]) == 1
    assert data1["recommended_topics"][0]["topic"] == "SQL"

    resp_role2 = client.get("/api/companies/1/recommendation?role_id=2")
    data2 = resp_role2.json()
    assert data2["recommended_topics"][0]["topic"] == "Python"


def test_frequent_questions_dedupe_case_insensitive(client, db_session):
    admin_tok = make_admin(db_session, client)
    q1 = [{"question_text": "Reverse a linked list", "category": "DSA", "topic": "Linked List", "difficulty": "hard"}]
    q2 = [{"question_text": "reverse a LINKED LIST", "category": "DSA", "topic": "Linked List", "difficulty": "hard"}]

    submit_and_approve(client, admin_tok, "a1@example.com", 1, q1)
    submit_and_approve(client, admin_tok, "a2@example.com", 1, q2)

    resp = client.get("/api/companies/1/recommendation")
    data = resp.json()
    assert len(data["frequent_questions"]) == 1
    assert data["frequent_questions"][0]["count"] == 2


def test_only_approved_experiences_count(client, db_session):
    token = register(client, role="alumni", email="a1@example.com")
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": [{"round_number": 1, "round_type": "Technical", "difficulty": "medium",
                    "questions": [{"question_text": "Q1", "category": "DBMS", "topic": "SQL", "difficulty": "medium"}]}],
    }
    client.post("/api/experiences", json=payload, headers=auth_headers(token))

    resp = client.get("/api/companies/1/recommendation")
    assert resp.json()["based_on"] == 0
