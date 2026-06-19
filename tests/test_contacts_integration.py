import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_contact(client: AsyncClient, auth_headers):
    """Creating a contact, then listing contacts, should return it."""

    create_response = await client.post(
        "/api/contacts/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "0991234567",
            "birthday": "1990-06-08",
            "additional_data": None,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = await client.get("/api/contacts/", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@pytest.mark.asyncio
async def test_get_nonexistent_contact_returns_404(client: AsyncClient, auth_headers):
    """Fetching a contact that doesn't exist should return 404."""

    response = await client.get("/api/contacts/999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact(client: AsyncClient, auth_headers):
    """Deleting an existing contact should return 204 and remove it."""

    create_response = await client.post(
        "/api/contacts/",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "0991234568",
            "birthday": "1992-01-01",
            "additional_data": None,
        },
        headers=auth_headers,
    )
    contact_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/contacts/{contact_id}", headers=auth_headers)
    assert get_response.status_code == 404