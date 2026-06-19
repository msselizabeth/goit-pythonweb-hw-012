from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.schemas.users import UserCreate


class UserRepository:
    """Provides database access for user records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Find a user by their email address.

        :param email: Email address to search for.
        :return: The matching user, or None if not found.
        """

        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, data: UserCreate, hashed_pass: str) -> User:
        """
        Create a new user record.

        :param data: Registration data containing the user's email.
        :param hashed_pass: Already-hashed password to store.
        :return: The newly created user.
        """
        new_user = User(email=data.email, password=hashed_pass)
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user

    async def verify_user_email(self, email: str) -> None:
        """
        Mark a user's email as verified.

        :param email: Email address of the user to verify.
        """
        stmt = update(User).where(User.email == email).values(is_verified=True)
        await self.db.execute(stmt)
        await self.db.flush()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        :param email: Email of the user to update.
        :param url: New avatar URL.
        :return: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar_url = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
