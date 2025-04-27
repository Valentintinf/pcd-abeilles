import pytest
from fastapi import FastAPI
import httpx
import uvicorn


BASE_URL = "http://localhost:8001"

app = FastAPI()

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

@pytest.fixture
def test_user():
    return {
        "username": "pytest_user",
        "email": "pytest_user@example.com",
        "password": "pytestpassword"
    }

def test_register_user(client, test_user):
    # Essayer de s'enregistrer
    response = client.post("/users/register", json=test_user)
    # On accepte que l'utilisateur existe déjà (code 400) ou succès (code 200)
    assert response.status_code in (200, 400)

def test_login_user(client, test_user):
    # Essayer de se connecter
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 200
    user_info = response.json().get("user")
    assert user_info is not None
    assert user_info["username"] == test_user["username"]
    assert user_info["email"] == test_user["email"]

def test_login_user_wrong_password(client, test_user):
    # Essayer de se connecter avec un mauvais mot de passe
    bad_login_data = {
        "username": test_user["username"],
        "password": "wrongpassword"
    }
    response = client.post("/users/login", json=bad_login_data)
    assert response.status_code == 401

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)