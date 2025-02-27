import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time
from config import GOOGLE_SHEETS_JSON, SPREADSHEET_NAME
from logger import logger

# Настраиваем доступ к Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(GOOGLE_SHEETS_JSON, scopes=scopes)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME)

# Кэш данных
cached_data = {"products": [], "faq": [], "last_updated": 0}

def update_cache():
    """Обновляет кэш товаров и FAQ раз в 10 минут"""
    global cached_data
    now = time.time()
    if now - cached_data["last_updated"] > 600:  # 10 минут
        try:
            logger.info("🔄 Обновление данных из Google Sheets...")
            cached_data["products"] = sheet.worksheet("Products").get_all_records()
            cached_data["faq"] = sheet.worksheet("FAQ").get_all_records()
            cached_data["last_updated"] = now
            logger.info("✅ Данные обновлены!")
        except Exception as e:
            logger.error(f"Ошибка обновления кэша: {e}")

def get_product_info(product_name):
    """Получаем информацию о товаре из кэша"""
    update_cache()  # Обновляем данные перед поиском
    product_name = product_name.strip().lower()

    for row in cached_data["products"]:
        if row["Товар"].strip().lower() == product_name:
            return f"📦 {row['Товар']}\n💰 Цена: {row['Цена']}\n📖 {row['Описание']}", row.get("Фото", None)

    return None, None

def get_faq_answer(question):
    """Ищем ответ в FAQ из кэша"""
    update_cache()  # Обновляем данные перед поиском
    question = question.strip().lower()

    for row in cached_data["faq"]:
        if question in row["Вопрос"].strip().lower():
            return row["Ответ"]

    return None


def log_query(user_question, bot_answer):
    """Логируем запрос пользователя в Google Sheets"""
    try:
        analytics_sheet = sheet.worksheet("Analytics")
        analytics_sheet.append_row([user_question, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), bot_answer])
    except Exception as e:
        logger.error(f"Ошибка логирования в Google Sheets: {e}")