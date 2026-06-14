from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.repository.contacts import ContactRepository
from app.schemas.contacts import ContactModel
from app.db.models import User


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_contacts(
        self,
        current_user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        skip: int = 0,
        limit: int = 10,
    ):
        contacts = await self.repository.get_contacts(
            first_name, last_name, email, skip, limit, current_user.id
        )
        if len(contacts) == 0:
            return []
        return contacts

    async def get_contact(self, id: int, current_user: User):
        contact = await self.repository.get_contact_by_id(id, current_user.id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

    async def create_contact(self, body: ContactModel, current_user: User):
        try:
            return await self.repository.create_contact(body, current_user.id)
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Contact with this email already exists"
            )
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def update_contact(self, id: int, body: ContactModel, current_user: User):
        try:
            contact = await self.repository.update_contact(id, body, current_user.id)
            if contact is None:
                raise HTTPException(status_code=404, detail="Contact not found")
            return contact
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def delete_contact(self, id: int, current_user: User):
        contact = await self.repository.delete_contact(id, current_user.id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

    async def get_b_days(self, current_user: User):
        return await self.repository.get_birthdays(current_user.id)
