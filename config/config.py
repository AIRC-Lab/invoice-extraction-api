import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    PROVIDER: str = os.getenv("PROVIDER")

settings = Settings()

