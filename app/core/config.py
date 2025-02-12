from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Würzburg Student Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    VECTOR_STORE_PATH: str = "data/vector_store"
    GENERAL_INFO_PATH: str = "data/json_data/general_info.json"
    
    DATABASE_URL: str = ""
    
    OPENAI_API_KEY: str = ""
    
    TELEGRAM_BOT_TOKEN: str = ""
    
    # Development Mode
    DEVELOPMENT_MODE: bool = False
    DEVELOPER_USER_ID: int = None

    # OpenAI Models
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"  # Models: text-embedding-3-small, text-embedding-ada-002
    OPENAI_CHAT_MODEL: str = "gpt-3.5-turbo" # Models: gpt-3.5-turbo, gpt-4o-mini, gpt-4o
    MODEL_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
