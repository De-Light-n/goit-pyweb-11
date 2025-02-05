from unittest import mock
from unittest.mock import AsyncMock, MagicMock
from urllib import response

import pytest

from src.entity.models import User
from tests.conftest import TestingSessionLocal, test_user, test_user_not_confirmed

user_data = {"username": "testuser", "email": "testuser@gmail.com", "password": "12345678"}

def test_signup(client, monkeypatch, mock_rate_limiter):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert mock_send_email.called
    
def test_signup_with_existing_user(client, monkeypatch, mock_rate_limiter):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=test_user)
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Account already exists"
    assert not mock_send_email.called
    
def test_login(client, monkeypatch, mock_rate_limiter):
    response = client.post("api/auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    
def test_login_with_invalid_password(client, monkeypatch, mock_rate_limiter):
    response = client.post("api/auth/login", data={"username": test_user["email"], "password": "invalid"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"
    
def test_login_with_invalid_email(client, monkeypatch, mock_rate_limiter):
    response = client.post("api/auth/login", data={"username": "invalid", "password": "invalid"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"
    
def test_login_with_not_confirmed(client, monkeypatch, mock_rate_limiter):
    response = client.post("api/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_confirmed_email(client, mock_rate_limiter, get_token):
    response = client.get(f"/api/auth/confirmed_email/{get_token}")
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Your email is already confirmed"}

def test_confirmed_email_with_invalid_token(client, mock_rate_limiter):
    response = client.get("/api/auth/confirmed_email/invalid")
    assert response.status_code == 422, response.text
    assert response.json() == {"detail": "Invalid token for email verification"}
    
def test_request_email(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/request_email", json={"email": test_user_not_confirmed["email"]})
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Check your email for confirmation."}
    assert mock_send_email.called
    
def test_request_email_confirmed(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/request_email", json={"email": test_user["email"]})
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Your email is already confirmed"}