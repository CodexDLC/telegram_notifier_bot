# Используем легкую версию Python 3.12
FROM python:3.12-slim

# Указываем рабочую папку внутри контейнера
WORKDIR /app

# Отключаем создание .pyc файлов и буферизацию вывода (чтобы логи появлялись сразу)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем файл с зависимостями
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Открываем порт 8000 (на котором работает FastAPI)
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]