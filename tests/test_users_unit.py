import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.users import UserService
from app.db.models import User


@pytest.mark.asyncio
async def test_register_user_already_exists_raises_409():
    """If a user with this email already exists, registration should raise 409."""

    mock_repo = AsyncMock()
    mock_repo.get_user_by_email.return_value = User(id=1, email="taken@example.com")

    service = UserService(mock_repo)

    fake_data = type("obj", (), {"email": "taken@example.com", "password": "whatever"})()

    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(fake_data)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_auth_user_not_found_raises_401():
    """Authenticating an email that doesn't exist should raise 401."""

    mock_repo = AsyncMock()
    mock_repo.get_user_by_email.return_value = None

    service = UserService(mock_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.auth_user(email="nobody@example.com", password="whatever")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_auth_user_wrong_password_raises_401():
    """Authenticating with a correct email but wrong password should raise 401."""

    from app.services.auth import hash_helper

    existing_user = User(
        id=1,
        email="user@example.com",
        password=hash_helper.get_password_hash("correctpassword"),
    )

    mock_repo = AsyncMock()
    mock_repo.get_user_by_email.return_value = existing_user

    service = UserService(mock_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.auth_user(email="user@example.com", password="wrongpassword")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_update_avatar_url_calls_repository():
    """Updating the avatar should delegate to the repository with the right arguments."""

    mock_repo = AsyncMock()
    mock_repo.update_avatar_url.return_value = User(id=1, email="user@example.com", avatar_url="http://new-url")

    service = UserService(mock_repo)
    result = await service.update_avatar_url(email="user@example.com", url="http://new-url")

    mock_repo.update_avatar_url.assert_called_once_with("user@example.com", "http://new-url")
    assert result.avatar_url == "http://new-url"