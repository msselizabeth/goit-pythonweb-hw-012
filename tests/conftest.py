import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.models import Base
from app.db.db_connection import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """
    Create a fresh in-memory SQLite engine and tables for each test,
    then tear everything down afterward. Creating the engine here (not at
    module level) ties it to the current test's event loop, avoiding
    'attached to a different loop' errors.
    """
    engine_test = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    test_session_local = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with test_session_local() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db] = override_get_db

    # make the session factory available to other fixtures/tests via app state
    app.state.test_session_local = test_session_local

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()

    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def client():
    """HTTP client for sending test requests to the API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, monkeypatch):
    """
    Create a verified user and return Authorization headers with a valid access token.
    Use this fixture in any test that needs an already-logged-in user.
    """

    async def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.api.auth.send_verification_email", fake_send_email)

    email = "fixtureuser@example.com"
    password = "TestPass123!"

    await client.post("/api/auth/signup", json={"email": email, "password": password})

    from app.repository.users import UserRepository

    # use the same session factory the app is using for this test
    test_session_local = app.state.test_session_local
    async with test_session_local() as session:
        repo = UserRepository(session)
        await repo.verify_user_email(email)
        await session.commit()

    response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

import app.services.cache as cache_module


@pytest_asyncio.fixture(autouse=True)
async def reset_redis_client():
    """
    Reset the cached Redis client before each test so a new connection
    is created in the current test's event loop, avoiding stale connections
    tied to a closed loop from a previous test.
    """
    cache_module.redis_client = None
    yield
    if cache_module.redis_client is not None:
        await cache_module.redis_client.close()
        cache_module.redis_client = None