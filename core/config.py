from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Gemini API
    gemini_api_key: str
    
    # App Settings
    app_name: str = "Veritas Backend"
    debug: bool = False
    max_claims_per_request: int = 5
    
    # Rate Limiting
    requests_per_minute: int = 10
    
    # Caching
    cache_ttl_seconds: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"

settings = Settings()