from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://arb:arb@localhost:5432/arb_finder"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    log_level: str = "INFO"


settings = Settings()
