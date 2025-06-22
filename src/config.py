import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Необходимо установить TELEGRAM_TOKEN и GEMINI_API_KEY в .env файле")
MAX_MESSAGE_LENGTH = 4096