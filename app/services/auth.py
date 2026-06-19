from datetime import datetime, timedelta, UTC
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.config import settings
from app.db.db_connection import get_db
from app.db.models import User
from app.schemas.users import UserResponse
from app.repository.users import UserRepository
from app.services.cache import get_redis_client
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Hash:
    """Provides password hashing and verification using bcrypt."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Check whether a plain-text password matches its hashed version.

        :param plain_password: The password provided by the user.
        :param hashed_password: The previously hashed password from the database.
        :return: True if the password is correct, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a plain-text password.

        :param password: The password to hash.
        :return: The hashed password.
        """
        return self.pwd_context.hash(password)

hash_helper = Hash()

def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Generate a JWT access token.

    :param data: Payload to encode in the token (e.g. {"sub": email}).
    :param expires_delta: Token lifetime in seconds. Defaults to 15 minutes.
    :return: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Retrieve the currently authenticated user from the JWT token.

    Checks Redis cache first; falls back to the database on a cache miss
    and stores the result in Redis for subsequent requests.

    :param token: JWT access token from the Authorization header.
    :param db: Database session.
    :return: The authenticated user.
    :raises HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the incoming JWT token
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    redis = await get_redis_client()
    cache = await redis.get(f"user:{email}")
    if cache:
        return UserResponse(**json.loads(cache))
    else:
        repository = UserRepository(db)
        
        user = await repository.get_user_by_email(email)
        if user is None:
            raise credentials_exception
        
        user_response = UserResponse.model_validate(user)

        await redis.set(
            f"user:{email}",
            user_response.model_dump_json(),
            ex=900
            
        )
        
        return user_response


def require_admin(current_user: User = Depends(get_current_user)):
    """
    Restrict access to admin users only.

    :param current_user: The currently authenticated user.
    :return: The user, if they have the admin role.
    :raises HTTPException: If the user's role is not "admin" (403 Forbidden).
    """
    if not current_user.role == "admin":
        raise HTTPException(403, "Access denied.")
    return current_user

