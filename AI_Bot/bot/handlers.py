from aiogram import types
from aiogram.filters import Command
from google_sheets import get_product_info, get_faq_answer, log_query
from openai_api import ask_openai
from logger import logger

# Храним сессии пользователей (бот помнит историю последних 10 сообщений)
sessions = {}

async def start_command(message: types.Message):
    """Приветственное сообщение с названием компании"""
    
    greeting = "👋 Привет! Я ваш AI-ассистент. Напишите свой вопрос, и я помогу вам!"

    await message.answer(greeting, parse_mode="Markdown")

async def help_command(message: types.Message):
    """Отправляет справку о возможностях бота"""
    help_text = """
    🤖 *AI Бизнес-ассистент* – поможет вам:
    
    ✅ Узнать информацию о товарах и услугах
    ✅ Ответить на частые вопросы
    ✅ Связаться с поддержкой
    ✅ Получить рекомендации по покупкам
    
    🔹 Просто напишите свой вопрос, и бот ответит! 
    """
    await message.answer(help_text, parse_mode="Markdown")

async def reset_session(message: types.Message):
    """Очищает историю сообщений пользователя"""
    user_id = message.from_user.id
    if user_id in sessions:
        del sessions[user_id]  # Удаляем сессию
        await message.answer("🔄 История очищена! Начнем заново.")
    else:
        await message.answer("У вас нет активной сессии.")

async def handle_message(message: types.Message):
    """Обрабатывает входящие сообщения"""

    # Проверяем, не голосовое или видеосообщение
    if message.voice or message.video_note or message.audio or message.video:
        await message.answer("🚫 Голосовые и видеосообщения запрещены. Отправьте текст.")
        return

    user_id = message.from_user.id  # ID пользователя для сохранения сессии
    user_text = message.text.strip().lower()

    try:
        # Ищем товар в базе данных Google Sheets
        product_info, photo_url = get_product_info(user_text)
        if product_info:
            if photo_url:
                await message.answer_photo(photo_url, caption=product_info)
            else:
                await message.answer(product_info)
            log_query(user_text, product_info)  # Записываем в аналитику
            return

        # Ищем ответ в Google Sheets (FAQ)
        faq_answer = get_faq_answer(user_text)
        if faq_answer:
            await message.answer(faq_answer)
            log_query(user_text, faq_answer)
            return

        # Если ничего не найдено — отправляем запрос в OpenAI (с историей)
        response = await ask_openai(user_id, user_text, source="Telegram")
        await message.answer(response)
        log_query(user_text, response)

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")