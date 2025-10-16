"""
Application configuration
"""
import os
import dotenv

from pydantic_settings import BaseSettings
from typing import List

dotenv.load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Project
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Fund Performance Analysis System")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    
    # API
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://funduser:fundpass@localhost:5432/funddb")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    #ollama
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    #FlashRank
    FLASHRANK_MODEL: str = os.getenv("FLASHRANK_MODEL", "ms-marco-TinyBERT-L-2-v2")

    BREAKPOINT_THRESHOLD_TYPE: str = os.getenv("BREAKPOINT_THRESHOLD_TYPE", "percentile")
    BREAKPOINT_THRESHOLD: float = os.getenv("BREAKPOINT_THRESHOLD", 95)
    
    # Anthropic (optional)
    ANTHROPIC_API_KEY: str = ""
    
    # Vector Store
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
    
    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024)  # 50MB
    
    # Document Processing
    CHUNK_SIZE: int = os.getenv("CHUNK_SIZE", 1000)
    CHUNK_OVERLAP: int = os.getenv("CHUNK_OVERLAP", 200)
    
    # RAG
    TOP_K_RESULTS: int = os.getenv("TOP_K_RESULTS", 5)
    SIMILARITY_THRESHOLD: float = os.getenv("SIMILARITY_THRESHOLD", 0.7)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
