from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User
from app.schemas.users import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    # Find by email
    async def get_user_by_email(self, email: str) -> User | None:
        
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # New user
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        
        new_user = User(
            email=user_data.email,
            password=hashed_password 
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user