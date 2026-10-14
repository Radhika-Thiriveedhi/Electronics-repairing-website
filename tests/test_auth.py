import pytest
from app import create_app
from app.services.auth_service import User, register_user

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

def test_user_authentication(client):
    user = User.get_by_email("customer@fixloop.org")
    assert user is not None
    assert user.role == "customer"
    assert user.check_password("password123") is True

import time

def test_user_registration(client):
    unique_email = f"test_user_{int(time.time() * 1000)}@fixloop.org"
    new_user, msg = register_user(
        email=unique_email,
        password="secretpassword",
        name="Test User",
        role="customer"
    )
    assert new_user is not None
    assert new_user.name == "Test User"

def test_duplicate_registration_fails(client):
    user, msg = register_user(
        email="customer@fixloop.org",
        password="password123",
        name="Aarav Sharma",
        role="customer"
    )
    assert user is None
    assert "already registered" in msg.lower()
