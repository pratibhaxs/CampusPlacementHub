import pytest
from app.models.college import College
from tests.helpers import register, make_admin, auth_headers


@pytest.fixture(autouse=True)
def seed(db_session):
    db_session.add(College(name="ABC University", city="Meerut", state="UP"))
    db_session.commit()


def test_list_companies_empty(client):
    resp = client.get("/api/companies")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_company_requires_admin(client, db_session):
    token = register(client)
    resp = client.post("/api/companies", json={"name": "XYZ Technologies"}, headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_can_create_company(client, db_session):
    admin_token = make_admin(db_session, client)
    resp = client.post("/api/companies", json={"name": "XYZ Technologies", "description": "A tech company"},
                        headers=auth_headers(admin_token))
    assert resp.status_code == 201
    assert resp.json()["name"] == "XYZ Technologies"


def test_duplicate_company_name_rejected(client, db_session):
    admin_token = make_admin(db_session, client)
    headers = auth_headers(admin_token)
    client.post("/api/companies", json={"name": "XYZ Technologies"}, headers=headers)
    resp = client.post("/api/companies", json={"name": "XYZ Technologies"}, headers=headers)
    assert resp.status_code == 409


def test_company_search(client, db_session):
    admin_token = make_admin(db_session, client)
    headers = auth_headers(admin_token)
    client.post("/api/companies", json={"name": "XYZ Technologies"}, headers=headers)
    client.post("/api/companies", json={"name": "Acme Corp"}, headers=headers)

    resp = client.get("/api/companies?q=xyz")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "XYZ Technologies"


def test_company_detail_includes_roles(client, db_session):
    admin_token = make_admin(db_session, client)
    headers = auth_headers(admin_token)
    company_id = client.post("/api/companies", json={"name": "XYZ Technologies"}, headers=headers).json()["id"]
    client.post(f"/api/companies/{company_id}/roles", json={"title": "Software Developer"}, headers=headers)

    resp = client.get(f"/api/companies/{company_id}")
    data = resp.json()
    assert data["name"] == "XYZ Technologies"
    assert len(data["roles"]) == 1
    assert data["roles"][0]["title"] == "Software Developer"


def test_adding_role_requires_admin(client, db_session):
    admin_token = make_admin(db_session, client)
    company_id = client.post("/api/companies", json={"name": "XYZ Technologies"},
                              headers=auth_headers(admin_token)).json()["id"]

    student_token = register(client, role="student", email="student@example.com")
    resp = client.post(f"/api/companies/{company_id}/roles", json={"title": "Hacker"},
                        headers=auth_headers(student_token))
    assert resp.status_code == 403


def test_delete_company_cascades_roles(client, db_session):
    admin_token = make_admin(db_session, client)
    headers = auth_headers(admin_token)
    company_id = client.post("/api/companies", json={"name": "XYZ Technologies"}, headers=headers).json()["id"]
    client.post(f"/api/companies/{company_id}/roles", json={"title": "Software Developer"}, headers=headers)

    resp = client.delete(f"/api/companies/{company_id}", headers=headers)
    assert resp.status_code == 200

    resp2 = client.get(f"/api/companies/{company_id}")
    assert resp2.status_code == 404
