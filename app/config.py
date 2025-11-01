from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str

    # App settings
    app_name: str
    app_version: str
    debug: bool

    # Data settings
    data_directory: str

    # API settings
    api_host: str
    api_port: int

    # Job settings
    refresh_interval_hours: int

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
