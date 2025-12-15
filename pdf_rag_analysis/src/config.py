from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"
    CHROMA_DB_PATH: Path = PROJECT_ROOT / "chroma_db"
    
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: Optional[str] = None
    
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DEVICE: str = "cpu"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.7
    
    CHROMA_COLLECTION_NAME: str = "pdf_documents"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
