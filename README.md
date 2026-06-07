# Contacts API

REST API for managing contacts built with FastAPI, SQLAlchemy, and PostgreSQL.

## Requirements

- Docker & Docker Compose
- Poetry (for local development)

## Quick Start

### 1. Configure

```
# .env

POSTGRES_USER=admin
POSTGRES_PASSWORD=admin1234
POSTGRES_DB=contacts_db
PGADMIN_DEFAULT_EMAIL=admin@gmail.com
PGADMIN_DEFAULT_PASSWORD=admin1234
DATABASE_URL=postgresql+asyncpg://admin:admin1234@db:5432/contacts_db
```

### 2. Start containers

docker compose up -d --build

### 3. Run migrations

docker compose exec app alembic upgrade head

### 4. Seed test data

docker compose exec app python seed.py

### 5. Open API docs

http://localhost:8001/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/contacts/ | Get all contacts (supports ?first_name, ?last_name, ?email) |
| GET | /api/contacts/{id} | Get contact by id |
| POST | /api/contacts/ | Create contact |
| PUT | /api/contacts/{id} | Update contact |
| PATCH | /api/contacts/{id} | Partial update |
| DELETE | /api/contacts/{id} | Delete contact |
| GET | /api/contacts/birthdays | Contacts with birthdays in next 7 days |

## Services

| Service | URL |
|---------|-----|
| API | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |
| pgAdmin | http://localhost:5050 |