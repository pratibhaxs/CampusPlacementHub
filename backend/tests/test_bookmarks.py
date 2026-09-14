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
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": [{"round_number": 1, "round_type": "Technical", "difficulty": "medium",
                    "questions": [{"question_text": "Reverse a linked list", "category": "DSA", "topic": "Linked List", "difficulty": "hard"}]}],
    }
    resp = client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok)).json()
    exp_id = resp["id"]
    question_id = resp["rounds"][0]["questions"][0]["id"]
    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))
    return exp_id, question_id


def test_student_can_bookmark_company(client, db_session):
    token = register(client)
    resp = client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["preview"]["title"] == "XYZ Technologies"


def test_alumni_cannot_bookmark(client, db_session):
    token = register(client, role="alumni", email="alumni2@example.com")
    resp = client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token))
    assert resp.status_code == 403


def test_bookmark_experience_and_question(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id, question_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    resp1 = client.post("/api/bookmarks", json={"target_type": "experience", "target_id": exp_id}, headers=auth_headers(student_tok))
    assert resp1.status_code == 201
    assert "XYZ Technologies" in resp1.json()["preview"]["title"]

    resp2 = client.post("/api/bookmarks", json={"target_type": "question", "target_id": question_id}, headers=auth_headers(student_tok))
    assert resp2.status_code == 201
    assert resp2.json()["preview"]["title"] == "Reverse a linked list"


def test_cannot_bookmark_pending_experience(client, db_session):
    alumni_tok = register(client, role="alumni", email="alumni3@example.com")
    payload = {
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": [], "overall_experience": "test",
    }
    exp_id = client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok)).json()["id"]

    student_tok = register(client)
    resp = client.post("/api/bookmarks", json={"target_type": "experience", "target_id": exp_id}, headers=auth_headers(student_tok))
    assert resp.status_code == 404


def test_duplicate_bookmark_rejected(client, db_session):
    token = register(client)
    client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token))
    resp = client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token))
    assert resp.status_code == 409


def test_invalid_target_type_rejected(client, db_session):
    token = register(client)
    resp = client.post("/api/bookmarks", json={"target_type": "banana", "target_id": 1}, headers=auth_headers(token))
    assert resp.status_code == 400


def test_bookmark_nonexistent_company_rejected(client, db_session):
    token = register(client)
    resp = client.post("/api/bookmarks", json={"target_type": "company", "target_id": 999}, headers=auth_headers(token))
    assert resp.status_code == 404


def test_list_bookmarks_filtered_by_type(client, db_session):
    token = register(client)
    client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token))

    resp = client.get("/api/bookmarks?target_type=company", headers=auth_headers(token))
    assert len(resp.json()) == 1

    resp2 = client.get("/api/bookmarks?target_type=question", headers=auth_headers(token))
    assert len(resp2.json()) == 0


def test_student_can_delete_own_bookmark(client, db_session):
    token = register(client)
    bookmark_id = client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token)).json()["id"]

    resp = client.delete(f"/api/bookmarks/{bookmark_id}", headers=auth_headers(token))
    assert resp.status_code == 200

    resp2 = client.get("/api/bookmarks", headers=auth_headers(token))
    assert resp2.json() == []


def test_student_cannot_delete_another_students_bookmark(client, db_session):
    token1 = register(client, email="student1@example.com")
    bookmark_id = client.post("/api/bookmarks", json={"target_type": "company", "target_id": 1}, headers=auth_headers(token1)).json()["id"]

    token2 = register(client, email="student2@example.com")
    resp = client.delete(f"/api/bookmarks/{bookmark_id}", headers=auth_headers(token2))
    assert resp.status_code == 404
