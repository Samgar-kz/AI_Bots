import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN
from handlers import start_command, reset_session, handle_message
from logger import logger

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Регистрируем обработчики
dp.message.register(start_command, Command("start"))
dp.message.register(reset_session, Command("reset"))
dp.message.register(handle_message)

async def main():
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())