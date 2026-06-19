import pytest
from datetime import date

from app.main import app
from app.repository.contacts import ContactRepository
from app.repository.users import UserRepository
from app.schemas.contacts import ContactModel
from app.services.auth import hash_helper


@pytest.mark.asyncio
async def test_repository_update_contact_not_found(client):
    """Updating a contact that doesn't exist should return None."""

    test_session_local = app.state.test_session_local
    async with test_session_local() as session:
        repo = ContactRepository(session)

        result = await repo.update_contact(
            id=999,
            body=ContactModel(
                first_name="Ghost",
                last_name="User",
                email="ghost@example.com",
                phone="0991234567",
                birthday=date(1990, 1, 1),
                additional_data=None,
            ),
            user_id=1,
        )

        assert result is None


@pytest.mark.asyncio
async def test_repository_delete_contact_not_found(client):
    """Deleting a contact that doesn't exist should return None."""

    test_session_local = app.state.test_session_local
    async with test_session_local() as session:
        repo = ContactRepository(session)
        result = await repo.delete_contact(id=999, user_id=1)
        assert result is None


@pytest.mark.asyncio
async def test_repository_create_and_update_contact(client):
    """Creating a contact, then updating it, should persist the new values."""

    test_session_local = app.state.test_session_local
    async with test_session_local() as session:
        user_repo = UserRepository(session)
        hashed = hash_helper.get_password_hash("TestPass123!")
        user = await user_repo.create_user(
            data=type("obj", (), {"email": "repo_owner@example.com"})(),
            hashed_pass=hashed,
        )
        await session.commit()

        contact_repo = ContactRepository(session)
        created = await contact_repo.create_contact(
            body=ContactModel(
                first_name="Original",
                last_name="Name",
                email="original@example.com",
                phone="0991234567",
                birthday=date(1990, 1, 1),
                additional_data=None,
            ),
            user_id=user.id,
        )
        await session.commit()

        updated = await contact_repo.update_contact(
            id=created.id,
            body=ContactModel(
                first_name="Updated",
                last_name="Name",
                email="original@example.com",
                phone="0991234567",
                birthday=date(1990, 1, 1),
                additional_data="now has a note",
            ),
            user_id=user.id,
        )

        assert updated.first_name == "Updated"
        assert updated.additional_data == "now has a note"