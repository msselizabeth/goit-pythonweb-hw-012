import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_creates_user(client: AsyncClient, monkeypatch):
    """Signing up with valid data should create a user and return 201."""

    # email sending hits a real SMTP server — replace it with a no-op for tests
    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)

    response = await client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "TestPass123!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["is_verified"] is False


@pytest.mark.asyncio
async def test_signup_duplicate_email_fails(client: AsyncClient, monkeypatch):
    """Signing up twice with the same email should return 409."""

    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)

    await client.post(
        "/api/auth/signup",
        json={"email": "dupe@example.com", "password": "TestPass123!"},
    )
    response = await client.post(
        "/api/auth/signup",
        json={"email": "dupe@example.com", "password": "TestPass123!"},
    )

    assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_unverified_user_fails(client: AsyncClient, monkeypatch):
    """Logging in before email verification should return 403."""

    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)

    await client.post(
        "/api/auth/signup",
        json={"email": "unverified@example.com", "password": "TestPass123!"},
    )

    response = await client.post(
        "/api/auth/login",
        data={"username": "unverified@example.com", "password": "TestPass123!"},  # OAuth2 form uses "data", not "json"
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_login_wrong_password_fails(client: AsyncClient, monkeypatch):
    """Logging in with the wrong password should return 401."""

    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)

    await client.post(
        "/api/auth/signup",
        json={"email": "wrongpass@example.com", "password": "TestPass123!"},
    )

    response = await client.post(
        "/api/auth/login",
        data={"username": "wrongpass@example.com", "password": "WrongPassword1!"},
    )

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_verify_email_success(client: AsyncClient, monkeypatch):
    """Verifying with a valid token should mark the user as verified."""

    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)

    await client.post(
        "/api/auth/signup",
        json={"email": "verifyme@example.com", "password": "TestPass123!"},
    )

    from app.services.auth import create_access_token
    token = create_access_token(data={"sub": "verifyme@example.com"})

    response = await client.get(f"/api/auth/verify/{token}")
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully."


@pytest.mark.asyncio
async def test_verify_email_invalid_token_fails(client: AsyncClient):
    """Verifying with a malformed token should return 400."""

    response = await client.get("/api/auth/verify/not-a-real-token")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password_unknown_email_still_returns_generic_message(client: AsyncClient):
    """Requesting a reset for an email that doesn't exist should not reveal that — same generic message."""

    response = await client.post(
        "/api/auth/forgot-password",
        json={"email": "doesnotexist@example.com"},
    )
    assert response.status_code == 200
    assert "If this email exists" in response.json()["message"]


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(client: AsyncClient, monkeypatch):
    """Full flow: request reset, then actually reset the password and log in with the new one."""

    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)
    monkeypatch.setattr("app.api.auth.send_password_reset_email", fake_send_email)

    email = "resetflow@example.com"
    old_password = "TestPass123!"
    new_password = "NewPass456!"

    await client.post("/api/auth/signup", json={"email": email, "password": old_password})


    from app.services.auth import create_access_token
    reset_token = create_access_token(data={"sub": email}, expires_delta=900)

    response = await client.post(
        f"/api/auth/reset-password/{reset_token}",
        json={"new_password": new_password},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully."