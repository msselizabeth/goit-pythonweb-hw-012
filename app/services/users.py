from app.repository.users import UserRepository
from app.schemas.users import UserCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.auth import hash_helper, create_access_token


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def register_user(self, data: UserCreate):
        try:    
            # Chek if user exists
            user = await self.repository.get_user_by_email(data.email)
            if user:
                raise HTTPException(status_code=409, detail="User already exists.")
            
            hashed_pass = hash_helper.get_password_hash(data.password)
            new_user = await self.repository.create_user(data, hashed_pass)
            return new_user
        
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")

    async def auth_user(self, email: str, password: str):
        try:
            # Chek if user exists
            user = await self.repository.get_user_by_email(email)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials.")
            
            is_password_correct = hash_helper.verify_password(password, user.password)
            if not is_password_correct:
                raise HTTPException(status_code=401, detail="Unauthorized.")
            return user

        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error")
        
