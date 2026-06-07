from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Contact
from app.schemas import ContactModel


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        skip: int = 0,
        limit: int = 10,
    ):

        filters = []
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

    async def get_contact_by_id(self, id: int):
        stmt = select(Contact).where(Contact.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_contact(self, body: ContactModel):
        new_contact = Contact(**body.model_dump())
        self.db.add(new_contact)
        await self.db.flush()
        await self.db.refresh(new_contact)
        return new_contact

    async def update_contact(self, id: int, body: ContactModel):
        contact = await self.get_contact_by_id(id)
        if contact is None:
            return None
        for key, value in body.model_dump().items():
            setattr(contact, key, value)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def delete_contact(self, id: int):
        contact = await self.get_contact_by_id(id)
        if contact is None:
            return None
        await self.db.delete(contact)
        return contact
