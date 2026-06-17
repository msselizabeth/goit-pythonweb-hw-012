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
from app.repository.users import UserRepository
from app.services.cache import get_redis_client
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

hash_helper = Hash()

def create_access_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
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
        return json.loads(cache)
    else:
        repository = UserRepository(db)
        print("DB hit  checking cache")
        user = await repository.get_user_by_email(email)
        if user is None:
            raise credentials_exception

        await redis.set(
            f"user:{email}",
            json.dumps(
                {
                    "id": user.id,
                    "email": user.email,
                    "is_verified": user.is_verified,
                    "avatar_url": user.avatar_url,
                }
            ),
            ex=900
            
        )
        # add "role": user.role later, sill need to add it to the model
        return user
