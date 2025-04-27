import requests
import base64

DB_API_URL = "http://localhost:8001"

def get_validated_image(image_id):
    try:
        response = requests.get(f"{DB_API_URL}/images/{image_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_pending_image(image_id):
    try:
        response = requests.get(f"{DB_API_URL}/images/pending/{image_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def list_validated_images():
    try:
        response = requests.get(f"{DB_API_URL}/images/", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

def list_pending_images():
    try:
        response = requests.get(f"{DB_API_URL}/images/pending/", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

def delete_validated_image(image_id):
    try:
        response = requests.delete(f"{DB_API_URL}/images/{image_id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def delete_pending_image(image_id):
    try:
        response = requests.delete(f"{DB_API_URL}/images/pending/{image_id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def update_pending_image(image_id, update_fields):
    try:
        response = requests.patch(f"{DB_API_URL}/images/pending/{image_id}", json=update_fields, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def login_user_api(username, password):
    try:
        response = requests.post(f"{DB_API_URL}/users/login", json={
            "username": username,
            "password": password
        }, timeout=5)
        response.raise_for_status()
        return response.json().get("user")
    except requests.RequestException:
        return None


def register_user_api(username, email, password):
    try:
        response = requests.post(f"{DB_API_URL}/users/register", json={
            "username": username,
            "email": email,
            "password": password
        }, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False
