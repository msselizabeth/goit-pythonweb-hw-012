from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_connection import get_db
from app.repository.contacts import ContactRepository
from app.services.contacts import ContactService
from app.schemas.contacts import ContactModel, ContactResponse
from app.db.models import User
from app.services.auth import get_current_user

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
    current_user: User = Depends(get_current_user)
):
    """
    List the current user's contacts, with optional filtering and pagination.

    :param first_name: Filter by exact first name match.
    :param last_name: Filter by exact last name match.
    :param email: Filter by exact email match.
    :param skip: Number of records to skip.
    :param limit: Maximum number of records to return.
    :param service: Contact service for the lookup.
    :param current_user: The authenticated user.
    :return: A list of matching contacts.
    """
    return await service.get_contacts(first_name, last_name, email, skip, limit, current_user)


@router.get("/birthdays", response_model=list[ContactResponse])
async def get_birthdays(
    service: ContactService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    """
    List the current user's contacts with birthdays in the next 7 days.

    :param service: Contact service for the lookup.
    :param current_user: The authenticated user.
    :return: A list of contacts with upcoming birthdays.
    """
    return await service.get_b_days(current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    service: ContactService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a single contact by ID.

    :param contact_id: ID of the contact to retrieve.
    :param service: Contact service for the lookup.
    :param current_user: The authenticated user who owns the contact.
    :return: The matching contact.
    :raises HTTPException: If no contact with this ID exists for the user.
    """
    return await service.get_contact(contact_id, current_user)


@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    body: ContactModel,
    service: ContactService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new contact for the current user.

    :param body: Contact data to create.
    :param service: Contact service for the creation logic.
    :param current_user: The authenticated user who will own the contact.
    :return: The newly created contact.
    :raises HTTPException: If a contact with this email already exists.
    """
    return await service.create_contact(body, current_user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    service: ContactService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing contact.

    :param contact_id: ID of the contact to update.
    :param body: Updated contact data.
    :param service: Contact service for the update logic.
    :param current_user: The authenticated user who owns the contact.
    :return: The updated contact.
    :raises HTTPException: If the contact doesn't exist.
    """
    return await service.update_contact(contact_id, body, current_user)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    service: ContactService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a contact.

    :param contact_id: ID of the contact to delete.
    :param service: Contact service for the deletion logic.
    :param current_user: The authenticated user who owns the contact.
    :raises HTTPException: If no contact with this ID exists for the user.
    """
    await service.delete_contact(contact_id, current_user)
