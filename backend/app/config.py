"""Application configuration settings using Pydantic Settings."""

import os
from typing import List, Union
from pydantic import field_validator

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore


class Settings(BaseSettings):
    """Global configuration settings for Federated Shield backend."""

    # Project Information
    PROJECT_NAME: str = "Privacy-Preserving Federated Learning Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = ""

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./federated_shield.db"

    # CORS configuration - default allows local dev frontend (Vite/React/Next.js)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            if not value:
                return ["*"]
            return [origin.strip() for origin in value.split(",")]
        return value

    # FL Runtime Mode: "real" (Qwen+LoRA via Flower), "mock" (MockLLM, fast),
    #                  "simulation_only" (fake curves for frontend-only dev)
    FL_MODE: str = "real"
    FL_NUM_CLIENTS: int = 4
    FL_USE_SECURE_AGG: bool = False
    FL_MODEL_TYPE: str = "qwen"

    @field_validator("FL_MODE", mode="before")
    @classmethod
    def validate_fl_mode(cls, value: str) -> str:
        allowed = {"real", "mock", "simulation_only"}
        if value not in allowed:
            raise ValueError(f"FL_MODE must be one of {allowed}, got '{value}'")
        return value

    # Simulation settings for Training Engine (used by simulation_only mode
    # and for DP epsilon calculation in all modes)
    DEFAULT_ROUNDS: int = 5
    SIMULATED_ROUND_DURATION_SEC: float = 2.5
    BASE_ACCURACY: float = 0.35
    MAX_ACCURACY: float = 0.94
    INITIAL_LOSS: float = 2.10
    MIN_LOSS: float = 0.28
    EPSILON_PER_ROUND: float = 0.45

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
