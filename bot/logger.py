import logging
import os
from logging.handlers import RotatingFileHandler

# Папка для логов
LOGS_DIR = os.path.dirname(os.path.abspath(__file__))

# Файл логов
LOG_FILE = os.path.join(LOGS_DIR, "bot.log")

# Ограничиваем размер логов до 5MB и храним 3 версии
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,      # Лог в файл (ограниченный размер)
        logging.StreamHandler()  # Лог в консоль
    ]
)

logger = logging.getLogger(__name__)