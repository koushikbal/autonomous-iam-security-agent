from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str | None = None
    github_token: str | None = None
    github_repository: str | None = None
    github_base_branch: str = "main"
    llm_model: str = "gpt-4o"
    max_validation_attempts: int = 3
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

