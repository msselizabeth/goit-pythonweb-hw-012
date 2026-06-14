from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from jose import jwt, JWTError

from app.db.db_connection import get_db
from app.repository.users import UserRepository
from app.services.auth import create_access_token
from app.schemas.users import UserCreate, UserResponse
from app.services.users import UserService
from app.services.email import send_verification_email
from app.config import settings

class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: str

router = APIRouter(prefix="/auth", tags=["auth"])

def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)

@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup_user(
    request: Request, 
    user_data: UserCreate, 
    service: UserService = Depends(get_service)
):
    new_user = await service.register_user(user_data)
    
    token = create_access_token(data={"sub": new_user.email})
    
    base_url = str(request.base_url).rstrip("/")
    await send_verification_email(new_user.email, f"{base_url}/api/", token)
    
    return new_user

@router.post("/login", response_model=AuthenticationResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    service: UserService = Depends(get_service)
):
    user = await service.auth_user(form_data.username, form_data.password)
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email is not verified.")
        
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid verification token.")
    except JWTError:
        raise HTTPException(status_code=400, detail="Verification token has expired or is invalid.")

    repository = UserRepository(db)
    user = await repository.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if user.is_verified:
        return {"message": "Email is already verified."}

    await repository.verify_user_email(email)
    await db.commit()
    return {"message": "Email verified successfully."}