from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = Field(description="URL to connect to PostgreSQL")
    
    # JWT Authentication configuration
    JWT_SECRET: str = Field(description="Secret Key")
    JWT_ALGORITHM: str = "HS256"  # default value
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )

settings = Settings()