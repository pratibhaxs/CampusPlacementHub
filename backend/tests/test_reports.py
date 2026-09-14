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


def test_student_can_report_experience(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    resp = client.post("/api/reports", json={"experience_id": exp_id, "reason": "fake"}, headers=auth_headers(student_tok))
    assert resp.status_code == 201
    assert resp.json()["status"] == "open"


def test_alumni_cannot_report(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    alumni_tok = register(client, role="alumni", email="alumni2@example.com")

    resp = client.post("/api/reports", json={"experience_id": exp_id, "reason": "spam"}, headers=auth_headers(alumni_tok))
    assert resp.status_code == 403


def test_invalid_reason_rejected(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    resp = client.post("/api/reports", json={"experience_id": exp_id, "reason": "because I said so"}, headers=auth_headers(student_tok))
    assert resp.status_code == 400


def test_duplicate_open_report_same_reason_rejected(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    client.post("/api/reports", json={"experience_id": exp_id, "reason": "fake"}, headers=auth_headers(student_tok))
    resp = client.post("/api/reports", json={"experience_id": exp_id, "reason": "fake"}, headers=auth_headers(student_tok))
    assert resp.status_code == 409


def test_different_reason_allowed(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)

    client.post("/api/reports", json={"experience_id": exp_id, "reason": "fake"}, headers=auth_headers(student_tok))
    resp = client.post("/api/reports", json={"experience_id": exp_id, "reason": "spam"}, headers=auth_headers(student_tok))
    assert resp.status_code == 201


def test_student_cannot_list_reports(client, db_session):
    student_tok = register(client)
    resp = client.get("/api/reports", headers=auth_headers(student_tok))
    assert resp.status_code == 403


def test_admin_can_list_and_resolve_reports(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)
    report_id = client.post("/api/reports", json={"experience_id": exp_id, "reason": "fake"}, headers=auth_headers(student_tok)).json()["id"]

    resp = client.get("/api/reports", headers=auth_headers(admin_tok))
    data = resp.json()
    assert len(data) == 1
    assert data[0]["reporter_name"] == "Test User"
    assert "XYZ Technologies" in data[0]["experience_title"]

    resolve_resp = client.put(f"/api/reports/{report_id}", json={"status": "reviewed"}, headers=auth_headers(admin_tok))
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "reviewed"


def test_reports_filtered_by_status(client, db_session):
    admin_tok = make_admin(db_session, client)
    exp_id = submit_and_approve_experience(client, admin_tok)
    student_tok = register(client)
    report_id = client.post("/api/reports", json={"experience_id": exp_id, "reason": "fake"}, headers=auth_headers(student_tok)).json()["id"]
    client.put(f"/api/reports/{report_id}", json={"status": "reviewed"}, headers=auth_headers(admin_tok))

    resp_open = client.get("/api/reports?status=open", headers=auth_headers(admin_tok))
    assert resp_open.json() == []

    resp_reviewed = client.get("/api/reports?status=reviewed", headers=auth_headers(admin_tok))
    assert len(resp_reviewed.json()) == 1


def test_admin_can_filter_experiences_by_pending_status(client, db_session):
    admin_tok = make_admin(db_session, client)
    alumni_tok = register(client, role="alumni", email="alumni3@example.com")
    payload = {"company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026, "rounds": []}
    client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok))

    resp = client.get("/api/experiences?status=pending", headers=auth_headers(admin_tok))
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"


def test_non_admin_status_filter_is_ignored_not_a_bypass(client, db_session):
    """A student passing ?status=pending shouldn't be able to see other
    people's pending (unapproved) experiences."""
    alumni_tok = register(client, role="alumni", email="alumni4@example.com")
    payload = {"company_id": 1, "role_id": 1, "college_id": 1, "placement_year": 2026, "rounds": []}
    client.post("/api/experiences", json=payload, headers=auth_headers(alumni_tok))

    student_tok = register(client)
    resp = client.get("/api/experiences?status=pending", headers=auth_headers(student_tok))
    assert resp.json() == []
