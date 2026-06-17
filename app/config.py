from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = Field(description="URL to connect to PostgreSQL")
    
    # JWT Authentication configuration
    JWT_SECRET: str = Field(description="Secret Key")
    JWT_ALGORITHM: str = "HS256"  # default value

    # Mail configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    
    # Cloudinary configuration
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: str = 6379
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )


settings = Settings()