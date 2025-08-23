"""
Application configuration management using Pydantic settings.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Application
    DEBUG: bool = Field(default=False, description="Debug mode")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="Secret key for JWT")
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000"], description="CORS allowed origins")
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost/ai_articles", description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    CACHE_TTL: int = Field(default=3600, description="Default cache TTL in seconds")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", description="Celery result backend URL")
    
    # AI/LLM Configuration
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-exp", description="Gemini model to use")
    MAX_TOKENS_PER_REQUEST: int = Field(default=4000, description="Max tokens per LLM request")
    
    # Azure OpenAI Configuration (optional)
    AZURE_OPENAI_API_KEY: str = Field(default="", description="Azure OpenAI API key")
    AZURE_OPENAI_ENDPOINT: str = Field(default="", description="Azure OpenAI endpoint")
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-02-15-preview", description="Azure OpenAI API version")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(default="gpt-4", description="Azure OpenAI deployment name")
    
    # Rate Limiting for Free Tier APIs
    MAX_REQUESTS_PER_MINUTE: int = Field(default=15, description="Max requests per minute for free tier")
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable rate limiting")
    
    # Search API
    GOOGLE_SEARCH_API_KEY: str = Field(default="", description="Google Custom Search API key")
    GOOGLE_SEARCH_ENGINE_ID: str = Field(default="", description="Google Custom Search Engine ID")
    MAX_SEARCH_RESULTS: int = Field(default=10, description="Maximum search results per query")
    
    # Web Scraping
    SCRAPING_TIMEOUT: int = Field(default=30, description="Web scraping timeout in seconds")
    MAX_CONCURRENT_SCRAPES: int = Field(default=10, description="Maximum concurrent scraping operations")
    PLAYWRIGHT_ENABLED: bool = Field(default=True, description="Enable Playwright for JS-heavy sites")
    
    # Article Generation
    MAX_ARTICLE_LENGTH: int = Field(default=10000, description="Maximum article length in words")
    MIN_SOURCES_PER_SECTION: int = Field(default=3, description="Minimum sources required per section")
    FACT_CHECK_THRESHOLD: float = Field(default=0.8, description="Minimum confidence for fact verification")
    
    # Monitoring & Observability
    ENABLE_TRACING: bool = Field(default=True, description="Enable OpenTelemetry tracing")
    METRICS_PORT: int = Field(default=9090, description="Prometheus metrics port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = Field(default=60, description="Rate limit for API requests")
    MAX_JOBS_PER_USER_PER_HOUR: int = Field(default=5, description="Max article generation jobs per user per hour")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    """
    return Settings()
