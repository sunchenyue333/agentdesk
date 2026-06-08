from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/agentdesk",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    frontend_url: AnyHttpUrl | str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="local-deterministic-agent", alias="OPENAI_MODEL")

    @property
    def cors_origins(self) -> list[str]:
        return [str(self.frontend_url).rstrip("/"), "http://localhost:3000"]


settings = Settings()
