"""Application configuration module."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter Configuration
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Application Configuration
    app_name: str = "AI Chat Application"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Telemetry Configuration
    jaeger_host: str = "jaeger"
    jaeger_port: int = 6831
    otel_service_name: str = "chat-backend"
    otel_exporter_otlp_endpoint: str = "http://jaeger:4317"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
