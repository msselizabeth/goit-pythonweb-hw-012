from sqlalchemy import select, and_, extract, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Contact
from app.schemas.contacts import ContactModel
from datetime import date, timedelta


class ContactRepository:
    """Provides database access for contact records, scoped to a specific user."""

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        skip: int = 0,
        limit: int = 10,
    ):
        """
        Retrieve a paginated, optionally filtered list of a user's contacts.

        :param user_id: ID of the contacts' owner.
        :param first_name: Filter by exact first name match.
        :param last_name: Filter by exact last name match.
        :param email: Filter by exact email match.
        :param skip: Number of records to skip (for pagination).
        :param limit: Maximum number of records to return.
        :return: A list of matching contacts.
        """
        # Added user_id to the base filters list
        filters = [Contact.user_id == user_id]

        if first_name:
            filters.append(Contact.first_name == first_name)
        if last_name:
            filters.append(Contact.last_name == last_name)
        if email:
            filters.append(Contact.email == email)

        # Check if any of queries exists
        if filters:
            stmt = select(Contact).where(and_(*filters))
        else:
            stmt = select(Contact)

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, id: int, user_id: int):
        """
        Find a single contact by ID, scoped to its owner.

        :param id: ID of the contact to retrieve.
        :param user_id: ID of the contact's owner.
        :return: The matching contact, or None if not found.
        """
        # Added Contact.user_id == user_id to the condition
        stmt = select(Contact).where(and_(Contact.id == id, Contact.user_id == user_id))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_contact(self, body: ContactModel, user_id: int):
        """
        Create a new contact for a user.

        :param body: Contact data to create.
        :param user_id: ID of the user who will own the contact.
        :return: The newly created contact.
        """

        # Added user_id parameter when creating the model instance
        new_contact = Contact(**body.model_dump(), user_id=user_id)
        self.db.add(new_contact)
        await self.db.flush()
        await self.db.refresh(new_contact)
        return new_contact

    async def update_contact(self, id: int, body: ContactModel, user_id: int):
        """
        Update an existing contact's fields.

        :param id: ID of the contact to update.
        :param body: Updated contact data.
        :param user_id: ID of the contact's owner.
        :return: The updated contact, or None if not found.
        """

        contact = await self.get_contact_by_id(id, user_id)
        if contact is None:
            return None
        for key, value in body.model_dump().items():
            setattr(contact, key, value)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def delete_contact(self, id: int, user_id: int):
        """
        Delete a contact.

        :param id: ID of the contact to delete.
        :param user_id: ID of the contact's owner.
        :return: The deleted contact, or None if not found.
        """
        contact = await self.get_contact_by_id(id, user_id)
        if contact is None:
            return None
        await self.db.delete(contact)
        return contact

    async def get_birthdays(self, user_id: int):
        """
        Retrieve a user's contacts with birthdays in the next 7 days.

        Handles the month-boundary case (e.g. late December into January)
        by splitting the date range across two month conditions.

        :param user_id: ID of the contacts' owner.
        :return: A list of contacts with upcoming birthdays.
        """
        today = date.today()
        end_date = today + timedelta(days=7)
        if today.month == end_date.month:
            stmt = select(Contact).where(
                and_(
                    Contact.user_id == user_id,  # Added user_id filter
                    extract("day", Contact.birthday) >= today.day,
                    extract("day", Contact.birthday) <= end_date.day,
                    extract("month", Contact.birthday) == end_date.month,
                )
            )
        else:
            stmt = select(Contact).where(
                and_(
                    Contact.user_id == user_id,  # Added user_id filter
                    or_(
                        and_(
                            extract("day", Contact.birthday) >= today.day,
                            extract("month", Contact.birthday) == today.month,
                        ),
                        and_(
                            extract("day", Contact.birthday) <= end_date.day,
                            extract("month", Contact.birthday) == end_date.month,
                        ),
                    ),
                )
            )
        result = await self.db.execute(stmt)
        return result.scalars().all()
