import pytest
from app.models.college import College
from app.models.company import Company
from app.models.role import Role
from tests.helpers import register, make_admin, auth_headers


@pytest.fixture(autouse=True)
def seed(db_session):
    db_session.add(College(name="ABC University", city="Meerut", state="UP"))
    company1 = Company(name="XYZ Technologies")
    company2 = Company(name="Acme Corp")
    db_session.add_all([company1, company2])
    db_session.flush()
    db_session.add(Role(company_id=company1.id, title="Software Developer"))
    db_session.add(Role(company_id=company2.id, title="Backend Engineer"))
    db_session.commit()


def test_student_cannot_access_admin_statistics(client, db_session):
    token = register(client, role="student", email="student@example.com")
    resp = client.get("/api/admin/statistics", headers=auth_headers(token))
    assert resp.status_code == 403


def test_statistics_counts(client, db_session):
    admin_tok = make_admin(db_session, client)
    register(client, role="student", email="s1@example.com")
    register(client, role="student", email="s2@example.com")
    alumni_tok = register(client, role="alumni", email="a1@example.com")

    exp_id = client.post("/api/experiences", json={
        "company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026,
        "rounds": [{"round_number": 1, "round_type": "Aptitude", "difficulty": "medium",
                    "questions": [{"question_text": "Q1", "category": "Aptitude", "topic": "Quant", "difficulty": "medium"}]}],
    }, headers=auth_headers(alumni_tok)).json()["id"]

    resp_before = client.get("/api/admin/statistics", headers=auth_headers(admin_tok))
    data_before = resp_before.json()
    assert data_before["total_students"] == 2
    assert data_before["total_alumni"] == 1
    assert data_before["total_companies"] == 2
    assert data_before["total_experiences"] == 0
    assert data_before["pending_experiences"] == 1

    client.put(f"/api/experiences/{exp_id}/status", json={"status": "approved"}, headers=auth_headers(admin_tok))

    resp_after = client.get("/api/admin/statistics", headers=auth_headers(admin_tok))
    data_after = resp_after.json()
    assert data_after["total_experiences"] == 1
    assert data_after["pending_experiences"] == 0
    assert data_after["most_discussed_companies"][0]["company"] == "XYZ Technologies"
    assert data_after["most_discussed_companies"][0]["count"] == 1
    assert data_after["most_frequent_topics"][0]["topic"] == "Quant"
