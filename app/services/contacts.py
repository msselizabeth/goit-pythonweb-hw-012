from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.repository.contacts import ContactRepository
from app.schemas.contacts import ContactModel
from app.db.models import User


class ContactService:
    """Handles contact CRUD operations and birthday lookups for a user."""

    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_contacts(
        self,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        skip: int,
        limit: int,
        current_user: User,
    ):
        """
        Retrieve a paginated, optionally filtered list of the user's contacts.

        :param first_name: Filter by first name (partial match).
        :param last_name: Filter by last name (partial match).
        :param email: Filter by email (partial match).
        :param skip: Number of records to skip (for pagination).
        :param limit: Maximum number of records to return.
        :param current_user: The authenticated user whose contacts are returned.
        :return: A list of matching contacts.
        """

        contacts = await self.repository.get_contacts(
            current_user.id, first_name, last_name, email, skip, limit
        )
        if len(contacts) == 0:
            return []
        return contacts

    async def get_contact(self, id: int, current_user: User):
        """
        Retrieve a single contact by ID.

        :param id: ID of the contact to retrieve.
        :param current_user: The authenticated user who owns the contact.
        :return: The matching contact.
        :raises HTTPException: If no contact with this ID exists for the user.
        """
        contact = await self.repository.get_contact_by_id(id, current_user.id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

    async def create_contact(self, body: ContactModel, current_user: User):
        """
        Create a new contact for the current user.

        :param body: Contact data to create.
        :param current_user: The authenticated user who will own the contact.
        :return: The newly created contact.
        :raises HTTPException: If a contact with this email already exists, or on a database error.
        """
        try:
            return await self.repository.create_contact(body, current_user.id)
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Contact with this email already exists"
            )
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def update_contact(self, id: int, body: ContactModel, current_user: User):
        """
        Update an existing contact.

        :param id: ID of the contact to update.
        :param body: Updated contact data.
        :param current_user: The authenticated user who owns the contact.
        :return: The updated contact.
        :raises HTTPException: If the contact doesn't exist, or on a database error.
        """
        try:
            contact = await self.repository.update_contact(id, body, current_user.id)
            if contact is None:
                raise HTTPException(status_code=404, detail="Contact not found")
            return contact
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def delete_contact(self, id: int, current_user: User):
        """
        Delete a contact.

        :param id: ID of the contact to delete.
        :param current_user: The authenticated user who owns the contact.
        :return: The deleted contact.
        :raises HTTPException: If no contact with this ID exists for the user.
        """
        contact = await self.repository.delete_contact(id, current_user.id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

    async def get_b_days(self, current_user: User):
        """
        Retrieve contacts whose birthday falls within the upcoming period.

        :param current_user: The authenticated user whose contacts are checked.
        :return: A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_birthdays(current_user.id)
