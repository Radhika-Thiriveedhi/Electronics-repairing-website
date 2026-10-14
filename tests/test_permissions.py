import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_unauthenticated_dashboard_redirects(client):
    res = client.get("/customer/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.location

def test_unauthorized_role_access(client):
    # Login as Customer
    client.post("/login", data={"email": "customer@fixloop.org", "password": "password123"})
    # Try accessing owner dashboard
    res = client.get("/owner/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.location
