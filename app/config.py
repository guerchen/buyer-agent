from pydantic import BaseSettings


class Settings(BaseSettings):
    LLM_API_KEY: str
    STORE_BASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
