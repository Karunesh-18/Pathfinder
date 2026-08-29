import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PathFinder Adaptive Learning API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database URL defaults to SQLite local fallback if Postgres is unavailable
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pathfinder.db")
    
    # Session rules
    MAX_QUESTIONS_PER_SESSION: int = 2
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()
