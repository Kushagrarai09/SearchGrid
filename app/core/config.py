from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "SearchGrid"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://searchgrid:searchgrid@localhost:5432/searchgrid"
    redis_url: str = "redis://localhost:6379/0"
    elasticsearch_url: str = "http://localhost:9200"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "document-events"
    cache_ttl_seconds: int = 60
    outbox_poll_seconds: int = 2

settings = Settings()
