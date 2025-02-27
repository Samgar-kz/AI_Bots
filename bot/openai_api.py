import aiohttp
import redis
import os
from config import OPENAI_API_KEY
from logger import logger

# Подключаем Redis для хранения истории диалогов
redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# Запрещенные слова (фильтрация спама и нежелательных тем)
banned_words = ["оскорбление", "политика", "18+", "спам"]

async def ask_openai(user_id, user_question, source="Telegram", available_functions=None):
    if available_functions is None:
        available_functions = ["Просмотреть товары", "Связаться с поддержкой"]

    try:
        # Фильтрация нежелательных вопросов
        if any(word in user_question.lower() for word in banned_words):
            return "🚫 Этот вопрос недопустим. Попробуйте другой."

        # Ключ в Redis для хранения истории пользователя
        history_key = f"history:{user_id}"

        # Загружаем историю (последние 10 сообщений)
        history = redis_client.lrange(history_key, -10, -1)
        history_messages = [{"role": "user" if i % 2 == 0 else "assistant", "content": msg} for i, msg in enumerate(history)]

        # Добавляем новый вопрос пользователя в историю
        history_messages.append({"role": "user", "content": user_question})

        # Кастомный системный промт
        system_prompt = """
        Ты — AI-ассистент для бизнеса. 
        Твоя задача — отвечать на вопросы клиентов, помогать с выбором товаров и вести вежливую беседу.
        Если клиент спрашивает про цену — отправь его в магазин.
        Если клиент задает повторяющиеся вопросы — постарайся дать новую информацию.
        Не придумывай ничего, если не знаешь ответа.
        """
        history_messages.insert(0, {"role": "system", "content": system_prompt})

        # Выбор модели OpenAI (GPT-3.5 для быстрых, GPT-4-Turbo для сложных запросов)
        if len(user_question) > 50 or "объясни" in user_question.lower():
            model = "gpt-4-turbo"
        else:
            model = "gpt-3.5-turbo"

        # Отправляем запрос в OpenAI
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": history_messages}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    bot_response = data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Ошибка OpenAI: {response.status} {await response.text()}")
                    return "❌ Ошибка AI. Попробуйте позже."

        # Сохраняем новый ответ в историю (ограничиваем до 10 сообщений)
        redis_client.rpush(history_key, user_question, bot_response)
        redis_client.ltrim(history_key, -10, -1)

        return bot_response

    except Exception as e:
        logger.error(f"Ошибка запроса к OpenAI: {e}")
        return "❌ Ошибка AI. Попробуйте позже."