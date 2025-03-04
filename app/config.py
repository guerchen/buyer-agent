import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(override=True)
LLM_API_KEY = os.getenv("LLM_API_KEY")
STORE_BASE_URL = os.getenv("STORE_BASE_URL")


@dataclass
class Settings:
    LLM_API_KEY: str
    STORE_BASE_URL: str


settings = Settings(LLM_API_KEY=LLM_API_KEY, STORE_BASE_URL=STORE_BASE_URL)
