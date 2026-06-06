from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Contact
from schemas import ContactModel

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session
    
    async def get_contacts(self, skip: int = 0, limit: int = 10):
        # Queries the database with pagination
        stmt = select(Contact).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_contact_by_id(self, id: int):
        stmt = select(Contact).where(Contact.id==id)
        result = await self.db.execute(stmt)
        return result.scalars().first()


    async def create_contact(self, body: ContactModel):
        new_contact = Contact(**body.model_dump())
        self.db.add(new_contact)
        await self.db.refresh(new_contact)
        return new_contact
    
    async def update_contact(self, id:int, body: ContactModel):
        contact = await self.get_contact_by_id(id)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.refresh(contact)
            return contact

    async def delete_contact(self, id:int):
        contact = await self.get_contact_by_id(id)
        if contact:
            await self.db.delete(contact)
    
    