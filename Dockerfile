# 1. Используем официальный Python
FROM python:3.12-slim

# 2. Обновляем pip и устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 4. Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# 5. Рабочая директория
WORKDIR /app

# 6. Копируем только файлы зависимостей для кэширования слоев
COPY pyproject.toml poetry.lock* /app/

# 7. Устанавливаем зависимости без dev
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# 8. Копируем весь проект
COPY . /app

# 9. Указываем команду запуска (uvicorn)
CMD ["uvicorn", "src.my_booking.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


