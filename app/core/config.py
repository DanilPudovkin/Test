from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Async Task Service"
    app_env: str = "local"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tasks"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    task_queue_name: str = "tasks"
    worker_concurrency: int = 4
    healthcheck_timeout_seconds: float = 3.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
