from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

# Determine the project root directory relative to this config file
# config.py is in ZYNAPSE/backend/core/
# Project root is ZYNAPSE/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Zynapse"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(PROJECT_ROOT, 'database.db')}")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_change_me") # CHANGE THIS!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    # OpenAI
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    

    # WhatsApp Bot Paths (NEW)
    # Default paths assume the script is run from the project root or the backend directory
    WHATSAPP_BOT_WORKING_DIR: str = os.getenv("WHATSAPP_BOT_WORKING_DIR", os.path.join(PROJECT_ROOT, "whatsapp-bot"))
    WHATSAPP_BOT_SCRIPT_PATH: str = os.getenv("WHATSAPP_BOT_SCRIPT_PATH", os.path.join(PROJECT_ROOT, "whatsapp-bot", "index.js"))
    WHATSAPP_BOT_PID_FILE: str = os.getenv("WHATSAPP_BOT_PID_FILE", os.path.join(PROJECT_ROOT, "whatsapp_bot.pid"))
    WHATSAPP_BOT_LOG_FILE: str = os.getenv("WHATSAPP_BOT_LOG_FILE", os.path.join(PROJECT_ROOT, "whatsapp_bot.log"))


    class Config:
        env_file = os.path.join(PROJECT_ROOT, ".env") # Load .env from project root
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Allow extra fields if needed, though not strictly necessary here
        # extra = 'allow' 

settings = Settings()

# Print resolved paths for debugging during startup (optional)
# print(f"Project Root: {PROJECT_ROOT}")
# print(f"Database URL: {settings.DATABASE_URL}")
# print(f"Bot Working Dir: {settings.WHATSAPP_BOT_WORKING_DIR}")
# print(f"Bot Script Path: {settings.WHATSAPP_BOT_SCRIPT_PATH}")
# print(f"Bot PID File: {settings.WHATSAPP_BOT_PID_FILE}")
# print(f"Bot Log File: {settings.WHATSAPP_BOT_LOG_FILE}")

