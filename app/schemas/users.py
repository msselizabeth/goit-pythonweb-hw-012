import re
from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator


class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_format(cls, value: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.fullmatch(pattern, value):
            raise ValueError("Invalid email format.")
        return value
    
    
    @field_validator("password")
    @classmethod
    def name_min_length(cls, value: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.fullmatch(pattern, value):
            raise ValueError("Password must be at least 8 characters, containing at least one uppercase letter, one lowercase letter, one number, and one special character")
        return value.strip()


class UserResponse(BaseModel):
    id: int
    email: str
    avatar_url: str | None
    is_verified: bool
    model_config = ConfigDict(from_attributes=True)
