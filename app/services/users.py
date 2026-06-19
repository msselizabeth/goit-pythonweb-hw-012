from app.repository.users import UserRepository
from app.schemas.users import UserCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.auth import hash_helper, create_access_token


class UserService:
    """Handles user registration, authentication, and avatar updates."""

    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def register_user(self, data: UserCreate):
        """
        Register a new user.

        :param data: New user's registration data (email, password).
        :return: The newly created user.
        :raises HTTPException: If a user with this email already exists, or on a database error.
        """
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
        """
        Authenticate a user by email and password.

        :param email: User's email address.
        :param password: Plain-text password to verify.
        :return: The authenticated user.
        :raises HTTPException: If credentials are invalid, or on a database error.
        """
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
    
    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.

        :param email: Email of the user to update.
        :param url: New avatar URL (e.g. from Cloudinary).
        :return: The updated user.
        """
        
        return await self.repository.update_avatar_url(email, url)

