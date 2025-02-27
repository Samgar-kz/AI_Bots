# Используем легковесный Python-образ
FROM python:3.11-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы бота
COPY . .

# Запускаем бота
CMD ["python", "bot/main.py"]