from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PyCrawler Research Studio"
    app_env: str = "development"
    app_debug: bool = True

    api_v1_prefix: str = "/api/v1"

    frontend_host: str = "127.0.0.1"
    frontend_port: int = 5173
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "pycrawler"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0

    celery_default_queue: str = "research-default"
    scientific_api_mailto: str | None = None
    scientific_store_path: str = "backend/data/scientific_store.json"
    scientific_http_timeout_seconds: float = 20.0
    pdf_store_path: str = "backend/data/pdf_store.json"
    pdf_download_dir: str = "backend/data/pdf_cache"
    pdf_http_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def frontend_url(self) -> str:
        return f"http://{self.frontend_host}:{self.frontend_port}"

    @property
    def backend_url(self) -> str:
        return f"http://{self.backend_host}:{self.backend_port}"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url

    @property
    def cors_origins(self) -> list[str]:
        return [
            self.frontend_url,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
