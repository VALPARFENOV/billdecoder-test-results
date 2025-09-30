FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY test-data-generator.py .
COPY automated-test-runner.py .
COPY scripts/ ./scripts/

# Создаем необходимые директории
RUN mkdir -p /app/test-data /app/test-results /app/logs

# Устанавливаем права на выполнение
RUN chmod +x test-data-generator.py automated-test-runner.py

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 tester && chown -R tester:tester /app
USER tester

# По умолчанию запускаем генератор тестовых данных
CMD ["python", "test-data-generator.py"]
