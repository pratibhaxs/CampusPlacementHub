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


def submit_and_approve(client, admin_tok, email, rounds):
    token = register(client, role="alumni", email=email)
    payload = {"company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026, "rounds": rounds}
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(token)).json()["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))
    return exp_id


def test_stats_with_no_experiences(client, db_session):
    resp = client.get("/api/companies/1/stats")
    data = resp.json()
    assert data["total_experiences"] == 0
    assert data["average_rounds"] == 0
    assert data["most_common_first_round"] is None
    assert data["topic_percentages"] == []


def test_average_rounds_calculation(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", [
        {"round_number": 1, "round_type": "Aptitude", "difficulty": "medium", "questions": []},
        {"round_number": 2, "round_type": "Technical", "difficulty": "hard", "questions": []},
    ])
    submit_and_approve(client, admin_tok, "a2@example.com", [
        {"round_number": 1, "round_type": "Aptitude", "difficulty": "medium", "questions": []},
        {"round_number": 2, "round_type": "Coding", "difficulty": "medium", "questions": []},
        {"round_number": 3, "round_type": "Technical", "difficulty": "hard", "questions": []},
        {"round_number": 4, "round_type": "HR", "difficulty": "easy", "questions": []},
    ])

    resp = client.get("/api/companies/1/stats")
    data = resp.json()
    assert data["total_experiences"] == 2
    assert data["average_rounds"] == 3.0


def test_most_common_first_round(client, db_session):
    admin_tok = make_admin(db_session, client)
    for i in range(3):
        submit_and_approve(client, admin_tok, f"a{i}@example.com", [
            {"round_number": 1, "round_type": "Aptitude", "difficulty": "medium", "questions": []},
        ])
    submit_and_approve(client, admin_tok, "a4@example.com", [
        {"round_number": 1, "round_type": "Coding", "difficulty": "medium", "questions": []},
    ])

    resp = client.get("/api/companies/1/stats")
    assert resp.json()["most_common_first_round"] == "Aptitude"


def test_topic_percentages_deduped_per_experience(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", [
        {"round_number": 1, "round_type": "Technical", "difficulty": "medium", "questions": [
            {"question_text": "Q1", "category": "DBMS", "topic": "SQL", "difficulty": "medium"},
            {"question_text": "Q2", "category": "DBMS", "topic": "SQL", "difficulty": "medium"},
        ]},
    ])
    submit_and_approve(client, admin_tok, "a2@example.com", [
        {"round_number": 1, "round_type": "Technical", "difficulty": "medium", "questions": [
            {"question_text": "Q1", "category": "DBMS", "topic": "SQL", "difficulty": "medium"},
        ]},
    ])
    submit_and_approve(client, admin_tok, "a3@example.com", [
        {"round_number": 1, "round_type": "HR", "difficulty": "easy", "questions": [
            {"question_text": "Tell me about yourself", "category": "HR", "topic": "Introduction", "difficulty": "easy"},
        ]},
    ])

    resp = client.get("/api/companies/1/stats")
    data = resp.json()
    sql_entry = next(t for t in data["topic_percentages"] if t["topic"] == "SQL")
    assert sql_entry["percentage"] == 67


def test_average_difficulty(client, db_session):
    admin_tok = make_admin(db_session, client)
    submit_and_approve(client, admin_tok, "a1@example.com", [
        {"round_number": 1, "round_type": "Aptitude", "difficulty": "medium", "questions": []},
        {"round_number": 2, "round_type": "Technical", "difficulty": "hard", "questions": []},
        {"round_number": 3, "round_type": "HR", "difficulty": "easy", "questions": []},
    ])

    resp = client.get("/api/companies/1/stats")
    assert resp.json()["average_difficulty"] == "medium"


def test_stats_only_counts_approved_experiences(client, db_session):
    token = register(client, role="alumni", email="a1@example.com")
    payload = {"company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
               "rounds": [{"round_number": 1, "round_type": "Aptitude", "difficulty": "medium", "questions": []}]}
    client.post("/api/experiences", json=payload, headers=auth_headers(token))

    resp = client.get("/api/companies/1/stats")
    assert resp.json()["total_experiences"] == 0
