import os
from dotenv import load_dotenv

load_dotenv(".env.local")  # Загружаем переменные окружения из .env

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEETS_JSON = os.getenv("GOOGLE_SHEETS_JSON")
SPREADSHEET_NAME = "AI Bot 1"