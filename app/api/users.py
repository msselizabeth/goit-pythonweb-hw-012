from fastapi import APIRouter, Depends, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.db_connection import get_db
from app.db.models import User
from app.services.auth import get_current_user, require_admin
from app.repository.users import UserRepository
from app.services.users import UserService  # Добавили импорт UserService
from app.config import settings
from app.schemas.users import UserResponse
from app.services.upload_file import UploadFileService

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def get_me(request: Request, current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile.

    Rate-limited to 5 requests per minute per client.

    :param request: Incoming HTTP request (required by the rate limiter).
    :param current_user: The authenticated user.
    :return: The current user's profile data.
    """
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and set a new avatar image for the current user.

    Restricted to admin users only.

    :param file: Image file to upload.
    :param current_user: The authenticated admin user.
    :param db: Database session.
    :return: The updated user profile, including the new avatar URL.
    :raises HTTPException: If the current user is not an admin.
    """
   
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME, 
        settings.CLOUDINARY_API_KEY, 
        settings.CLOUDINARY_API_SECRET
    ).upload_file(file, current_user.email)

    
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    user = await user_service.update_avatar_url(current_user.email, avatar_url)

    return user