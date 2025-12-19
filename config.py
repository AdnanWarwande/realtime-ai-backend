from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    
    supabase_url: str = ""
    supabase_key: str = ""
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
