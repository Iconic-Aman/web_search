from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    tavily_api_key: str
    database_url: str = "./chat.db"

    class Config:
        env_file = ".env"


settings = Settings()
