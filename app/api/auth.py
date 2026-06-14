from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_connection import get_db
from app.repository.users import UserRepository
from app.services.auth import create_access_token
from app.schemas.users import UserCreate, UserResponse
from app.services.users import UserService

from pydantic import BaseModel


class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: str


router = APIRouter(prefix="/auth", tags=["auth"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)


@router.post("/signup", response_model=UserResponse)
async def signup_user(
    user_data: UserCreate, service: UserService = Depends(get_service)
):
    return await service.register_user(user_data)


@router.post("/login", response_model=AuthenticationResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_service),
):
    user = await service.auth_user(form_data.email, form_data.password)
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
