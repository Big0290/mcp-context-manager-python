"""
Configuration settings for the MCP Memory Server.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    database_url: str = Field(
        default="postgresql://user:password@localhost/mcp_memory", env="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Vector database settings
    vector_db_type: str = Field(default="qdrant", env="VECTOR_DB_TYPE")
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")

    # Embedding settings
    embedding_model: str = Field(default="sentence-transformers", env="EMBEDDING_MODEL")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    sentence_transformer_model: str = Field(
        default="all-MiniLM-L6-v2", env="SENTENCE_TRANSFORMER_MODEL"
    )

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")

    # Memory settings
    memory_relevancy_threshold: float = Field(
        default=0.7, env="MEMORY_RELEVANCY_THRESHOLD"
    )
    max_memory_chunk_size: int = Field(default=1000, env="MAX_MEMORY_CHUNK_SIZE")
    auto_summarize_threshold: int = Field(default=50, env="AUTO_SUMMARIZE_THRESHOLD")
    max_short_term_memory: int = Field(default=100, env="MAX_SHORT_TERM_MEMORY")

    # Security settings
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
