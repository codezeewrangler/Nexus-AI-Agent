# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Keys
    gemini_api_key: str = ""
    
    # Vector DB
    chroma_persist_directory: str = "./data/chroma"
    embedding_model: str = "models/text-embedding-004"
    embedding_dimensions: int = 768
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 10
    
    # LLM
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.1
    max_tokens: int = 1000
    
    # Retrieval
    top_k_chunks: int = 5
    similarity_threshold: float = 0.7
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379


@lru_cache()
def get_settings() -> Settings:
    return Settings()
