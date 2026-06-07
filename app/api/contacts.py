from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_connection import get_db
from app.repository import ContactRepository
from app.service import ContactService
from app.schemas import ContactModel, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


def get_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    repository = ContactRepository(db)
    return ContactService(repository)


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    skip: int = 0,
    limit: int = 10,
    service: ContactService = Depends(get_service),
):
    return await service.get_contacts(first_name, last_name, email, skip, limit)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    service: ContactService = Depends(get_service),
):
    return await service.get_contact(contact_id)


@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    body: ContactModel,
    service: ContactService = Depends(get_service),
):
    return await service.create_contact(body)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    service: ContactService = Depends(get_service),
):
    return await service.update_contact(contact_id, body)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    service: ContactService = Depends(get_service),
):
    await service.delete_contact(contact_id)
