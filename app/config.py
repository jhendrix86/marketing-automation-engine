"""
Configuration management for Marketing Automation Engine
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/marketing")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Email
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    default_sender_email: str = os.getenv("DEFAULT_SENDER_EMAIL", "marketing@company.com")
    
    # Social Media
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_secret: str = os.getenv("TWITTER_ACCESS_SECRET", "")
    
    linkedin_api_key: str = os.getenv("LINKEDIN_API_KEY", "")
    linkedin_api_secret: str = os.getenv("LINKEDIN_API_SECRET", "")
    
    # Application
    app_name: str = "Marketing Automation Engine"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Integration
    funnel_automation_url: str = os.getenv("FUNNEL_AUTOMATION_URL", "http://localhost:8000")
    content_engine_url: str = os.getenv("CONTENT_ENGINE_URL", "http://localhost:8040")
    analytics_engine_url: str = os.getenv("ANALYTICS_ENGINE_URL", "http://localhost:8041")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
