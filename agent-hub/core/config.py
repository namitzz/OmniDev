"""
OmniDev Core Configuration

Loads and validates all environment variables and application settings.
Provides a centralized configuration object used throughout the application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Literal
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # API Keys
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(None, env="ANTHROPIC_API_KEY")
    github_token: str = Field(..., env="GITHUB_TOKEN")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GitHub Configuration
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    github_owner: str = Field(..., env="GITHUB_OWNER")
    github_repo: str = Field(..., env="GITHUB_REPO")
    github_webhook_secret: str | None = Field(None, env="GITHUB_WEBHOOK_SECRET")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Application Settings
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    app_name: Literal["DevHive", "AutoForge", "MergeMind"] = Field(
        "DevHive", env="APP_NAME"
    )
    environment: Literal["development", "staging", "production"] = Field(
        "development", env="ENVIRONMENT"
    )
    api_port: int = Field(8000, env="API_PORT")
    dashboard_port: int = Field(3000, env="DASHBOARD_PORT")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", env="LOG_LEVEL"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Vector Database
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    vector_db_type: Literal["chromadb", "pinecone", "qdrant"] = Field(
        "chromadb", env="VECTOR_DB_TYPE"
    )
    chromadb_path: str = Field("./data/chromadb", env="CHROMADB_PATH")
    pinecone_api_key: str | None = Field(None, env="PINECONE_API_KEY")
    pinecone_env: str | None = Field(None, env="PINECONE_ENV")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Agent Policies
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    max_loc_per_pr: int = Field(500, env="MAX_LOC_PER_PR")
    allow_new_deps: bool = Field(False, env="ALLOW_NEW_DEPS")
    min_test_coverage: int = Field(80, env="MIN_TEST_COVERAGE")
    allow_breaking_changes: bool = Field(False, env="ALLOW_BREAKING_CHANGES")
    max_retry_attempts: int = Field(3, env="MAX_RETRY_ATTEMPTS")
    auto_merge_enabled: bool = Field(False, env="AUTO_MERGE_ENABLED")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Code Analysis
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    enable_static_analysis: bool = Field(True, env="ENABLE_STATIC_ANALYSIS")
    enable_security_scan: bool = Field(True, env="ENABLE_SECURITY_SCAN")
    enable_dependency_audit: bool = Field(True, env="ENABLE_DEPENDENCY_AUDIT")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Observability
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    enable_structured_logging: bool = Field(True, env="ENABLE_STRUCTURED_LOGGING")
    log_file_path: str = Field("./logs/omnidev.log", env="LOG_FILE_PATH")
    enable_cost_tracking: bool = Field(True, env="ENABLE_COST_TRACKING")
    metrics_export: Literal["prometheus", "statsd", "none"] = Field(
        "prometheus", env="METRICS_EXPORT"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Database
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    database_url: str = Field("sqlite:///./data/omnidev.db", env="DATABASE_URL")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Model Configuration
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    planner_model: str = Field("gpt-4-turbo-preview", env="PLANNER_MODEL")
    feature_dev_model: str = Field("gpt-4-turbo-preview", env="FEATURE_DEV_MODEL")
    tester_model: str = Field("gpt-4-turbo-preview", env="TESTER_MODEL")
    refactor_model: str = Field("gpt-4-turbo-preview", env="REFACTOR_MODEL")
    reviewer_model: str = Field("gpt-4-turbo-preview", env="REVIEWER_MODEL")
    code_generation_temperature: float = Field(0.2, env="CODE_GENERATION_TEMPERATURE")
    max_tokens_per_response: int = Field(4000, env="MAX_TOKENS_PER_RESPONSE")
    enable_embedding_cache: bool = Field(True, env="ENABLE_EMBEDDING_CACHE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("min_test_coverage")
    def validate_coverage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("min_test_coverage must be between 0 and 100")
        return v
    
    @validator("code_generation_temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("code_generation_temperature must be between 0.0 and 1.0")
        return v


# Global settings instance
settings = Settings()
