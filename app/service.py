from app.repository import ContactRepository
from app.schemas import ContactModel
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_contacts(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        skip: int = 0,
        limit: int = 10,
    ):
        contacts = await self.repository.get_contacts(
            first_name, last_name, email, skip, limit
        )
        if len(contacts) == 0:
            return []
        return contacts

    async def get_contact(self, id: int):
        contact = await self.repository.get_contact_by_id(id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

    async def create_contact(self, body: ContactModel):
        try:
            return await self.repository.create_contact(body)
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Contact with this email already exists"
            )
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def update_contact(self, id: int, body: ContactModel):
        try:
            contact = await self.repository.update_contact(id, body)
            if contact is None:
                raise HTTPException(status_code=404, detail="Contact not found")
            return contact
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def delete_contact(self, id: int):
        contact = await self.repository.delete_contact(id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    
    async def get_b_days(self):
        return await self.repository.get_birthdays()
