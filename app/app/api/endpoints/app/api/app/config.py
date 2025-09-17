from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Application runtime configuration."""

    app_name: str = "PiVend Controller"
    api_v1_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{data_dir / 'vending.db'}"
    gpio_mode: str = "mock"
    analytics_cache_seconds: int = 60
    default_currency: str = "USD"
    telemetry_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_prefix="PIVEND_")


settings = Settings()
