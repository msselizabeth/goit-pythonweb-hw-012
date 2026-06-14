from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
    additional_data: str | None

    @field_validator("birthday")
    @classmethod
    def birthday_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Birtday cannot be in the future")
        return value
    
    @field_validator("phone")
    @classmethod
    def phone_format(cls, value: str) -> str:
        cleaned = value.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("Phone must contain only digits")
        if not len(cleaned) == 10:
            raise ValueError("Phone length is invalid. Expected format: 0996996969")
        return value
    
    @field_validator("first_name", "last_name")
    @classmethod
    def name_min_length(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Must be at least 2 characters")
        return v.strip()


class ContactResponse(ContactModel):
    id: int
    model_config = ConfigDict(from_attributes=True)
