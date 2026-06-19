import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.contacts import ContactService
from app.db.models import User


@pytest.fixture
def fake_user():
    """A minimal fake user object — service methods only need .id from it."""
    user = User(id=1, email="test@example.com")
    return user


@pytest.mark.asyncio
async def test_get_contact_not_found_raises_404(fake_user):
    """If the repository finds nothing, the service should raise 404."""

    mock_repo = AsyncMock()
    mock_repo.get_contact_by_id.return_value = None

    service = ContactService(mock_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_contact(id=999, current_user=fake_user)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_contact_not_found_raises_404(fake_user):
    """Updating a contact that doesn't exist should raise 404."""

    mock_repo = AsyncMock()
    mock_repo.update_contact.return_value = None

    service = ContactService(mock_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.update_contact(id=999, body={}, current_user=fake_user)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact_not_found_raises_404(fake_user):
    """Deleting a contact that doesn't exist should raise 404."""

    mock_repo = AsyncMock()
    mock_repo.delete_contact.return_value = None

    service = ContactService(mock_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_contact(id=999, current_user=fake_user)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_contacts_empty_list(fake_user):
    """If the repository returns no contacts, the service should return an empty list."""

    mock_repo = AsyncMock()
    mock_repo.get_contacts.return_value = []

    service = ContactService(mock_repo)
    result = await service.get_contacts(
        first_name=None, last_name=None, email=None, skip=0, limit=10, current_user=fake_user
    )

    assert result == []