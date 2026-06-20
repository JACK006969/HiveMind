from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "HiveMind AI Copilot"
    ENVIRONMENT: str = "production"
    FRONTEND_URL: str
    
    # Database & Cache
    DATABASE_URL: str
    REDIS_URL: str
    
    # AI
    GROQ_API_KEY: str
    
    # Exchange Data (API Key only for rate limit benefits)
    BYBIT_API_KEY: str
    
    # Auth & Security
  GITHUB_CLIENT_ID: str
GITHUB_CLIENT_SECRET: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
