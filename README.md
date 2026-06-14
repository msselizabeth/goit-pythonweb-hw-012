# Contacts API

REST API for managing contacts built with FastAPI, SQLAlchemy, and PostgreSQL.

## Requirements

- Docker & Docker Compose
- Poetry (for local development)

## Quick Start

### 1. Configure

```
# .env

# Database
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin1234
POSTGRES_DB=contacts_db
PGADMIN_DEFAULT_EMAIL=admin@gmail.com
PGADMIN_DEFAULT_PASSWORD=admin1234
DATABASE_URL=postgresql+asyncpg://admin:admin1234@db:5432/contacts_db

# Security
JWT_SECRET=your_super_secret_key_here
JWT_ALGORITHM=HS256

# Email Verification (FastAPI-Mail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_google_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Cloudinary (Avatar Uploads)
CLOUDINARY_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### 2. Start containers

docker compose up -d --build

### 3. Run migrations

docker compose exec app alembic upgrade head

### 4. Seed test data (Optional)

docker compose exec app python seed.py

### 5. Open API docs

http://localhost:8001/docs

## API Endpoints

### Auth
POST   /api/auth/signup
POST   /api/auth/login
GET    /api/auth/verify/{token}

### Users
GET    /api/users/me
PATCH  /api/users/avatar

### Contacts
GET    /api/contacts/
GET    /api/contacts/{id}
POST   /api/contacts/
PUT    /api/contacts/{id}
PATCH  /api/contacts/{id}
DELETE /api/contacts/{id}
GET    /api/contacts/birthdays

## Services

| Service | URL |
|---------|-----|
| API | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |
| pgAdmin | http://localhost:5050 |