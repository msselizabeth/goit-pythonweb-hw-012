from fastapi import APIRouter, Depends, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.db_connection import get_db
from app.db.models import User
from app.services.auth import get_current_user
from app.repository.users import UserRepository
from app.config import settings
from app.schemas.users import UserResponse

# Initialize Limiter locally within the router file to avoid circular imports
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])

# Configure Cloudinary credentials
cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def get_me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    upload_result = cloudinary.uploader.upload(file.file, public_id=f"avatars/{current_user.id}")
    avatar_url = upload_result.get("secure_url")
    
    repository = UserRepository(db)
    updated_user = await repository.update_user_avatar(current_user.email, avatar_url)
    await db.commit()
    
    return updated_user