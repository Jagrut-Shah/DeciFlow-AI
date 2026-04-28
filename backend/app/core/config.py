from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Literal, Optional, Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DeciFlow AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"       # "development" | "staging" | "production"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change_me_in_production_extremely_long_string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    RATE_LIMIT_PER_MINUTE: int = 60
    TASK_TIMEOUT: int = 120                 # Seconds before a background task is killed
    # LLM & Vertex AI
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: str = "bio-budget"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS_PATH: Optional[str] = None
    
    # Model configuration
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"
    
    @property
    def GEMINI_MODELS(self) -> dict:
        return {
            "flash": self.GEMINI_FLASH_MODEL,
            "pro": self.GEMINI_PRO_MODEL,
            "embedding": "text-embedding-004"
        }


    RESULT_TTL: int = 3600                 # Seconds to keep results in memory (1 hour)

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ----------------------------------------------------------------------- #
    # Backend Behavior Configuration                                          #
    # ----------------------------------------------------------------------- #
    PIPELINE_MODE: Literal["STRICT", "RESILIENT"] = "STRICT"
    MAX_RETRIES: int = 3
    RESULT_STORE_ENABLED: bool = True

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Prevents running with the default insecure SECRET_KEY in any
        non-development environment. Set SECRET_KEY in your .env file.
        """
        insecure_defaults = {
            "change_me_in_production_extremely_long_string",
            "secret",
            "supersecret",
            "",
        }
        if v in insecure_defaults:
            import os
            env = os.getenv("ENVIRONMENT", "development")
            if env in ("production", "staging"):
                raise ValueError(
                    "SECRET_KEY must be overridden from its default value in "
                    f"'{env}' environment. Set it via the SECRET_KEY env variable."
                )
        return v

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],   # check backend dir then project root
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
