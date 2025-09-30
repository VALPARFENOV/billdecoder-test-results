# Система тестирования промтов BillDecoder/LabDecoder

Комплексная система для тестирования и валидации AI-промтов медицинского анализа документов.

## 🎯 Обзор

Эта система обеспечивает:
- **Автоматическую генерацию тестовых данных** (медицинские счета, лабораторные результаты, EOB)
- **Комплексное тестирование промтов** с метриками качества и производительности
- **Локальную инфраструктуру** на основе Docker для изолированного тестирования
- **Веб-дашборд** для мониторинга результатов в реальном времени
- **Автоматическую генерацию отчетов** в различных форматах

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Data     │    │   Prompt        │    │   Results       │
│   Generator     │───▶│   Tester        │───▶│   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Medical       │    │   Hathr AI      │    │   PostgreSQL    │
│   Documents     │    │   API           │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
# Клонируйте репозиторий и перейдите в директорию
cd BillDecoder

# Запустите скрипт настройки
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Конфигурация API

Обновите файл `.env` с вашими учетными данными Hathr API:

```env
HATHR_CLIENT_ID=your_client_id
HATHR_CLIENT_SECRET=your_client_secret
```

### 3. Запуск полного цикла тестирования

```bash
# Сделайте скрипты исполняемыми
chmod +x scripts/run-tests.sh

# Запустите полный цикл тестирования
./scripts/run-tests.sh --full
```

## 📊 Компоненты системы

### 1. Генератор тестовых данных (`test-data-generator.py`)

Создает реалистичные медицинские документы для тестирования:

**Типы документов:**
- **Медицинские счета** (простые, средние, сложные)
- **Лабораторные результаты** (базовые, комплексные, полные)
- **EOB** (Explanation of Benefits)
- **Граничные случаи** (с ошибками, критическими значениями)

**Особенности:**
- Реалистичные медицинские коды (CPT, ICD-10, HCPCS)
- Различные уровни сложности
- Встроенные ошибки для тестирования детекции
- Трендовые данные для лабораторных анализов

### 2. Автоматизированный тестер (`automated-test-runner.py`)

Тестирует все промты на сгенерированных данных:

**Промты для тестирования:**
- `primary_bill_analysis` - Основной анализ медицинских счетов
- `bill_error_investigation` - Расследование ошибок в счетах
- `lab_results_explanation` - Объяснение лабораторных результатов
- `trend_analysis` - Анализ трендов
- `abnormal_results_focus` - Фокус на аномальных результатах
- `document_classification` - Классификация документов
- `confidence_scoring` - Оценка уверенности
- `privacy_protection` - Защита конфиденциальности

**Метрики качества:**
- **Точность** (0-10): Корректность анализа медицинских кодов
- **Ясность** (0-10): Понятность для обычных пользователей
- **Уверенность** (0-10): Надежность анализа
- **Производительность**: Время ответа, частота ошибок

### 3. Docker-инфраструктура

**Сервисы:**
- `prompt-tester` - Основной контейнер для тестирования
- `test-database` - PostgreSQL для хранения результатов
- `redis` - Кэширование и очереди
- `test-dashboard` - Веб-интерфейс для мониторинга
- `prometheus` - Сбор метрик
- `grafana` - Визуализация метрик

## 🛠️ Использование

### Команды для тестирования

```bash
# Полный цикл тестирования
./scripts/run-tests.sh --full

# Только генерация тестовых данных
./scripts/run-tests.sh --generate-data

# Только запуск тестов
./scripts/run-tests.sh --test

# Тестирование в фоновом режиме
./scripts/run-tests.sh --test --daemon

# Просмотр логов
./scripts/run-tests.sh --logs

# Статус системы
./scripts/run-tests.sh --status

# Генерация отчета
./scripts/run-tests.sh --report

# Очистка результатов
./scripts/run-tests.sh --clean
```

### Прямое использование Python скриптов

```bash
# Генерация тестовых данных
python test-data-generator.py

# Запуск тестирования
python automated-test-runner.py
```

### Docker команды

```bash
# Запуск всей инфраструктуры
docker-compose up -d

# Просмотр логов
docker-compose logs -f prompt-tester

# Выполнение команд в контейнере
docker-compose exec prompt-tester python test-data-generator.py

# Остановка всех сервисов
docker-compose down
```

## 📈 Мониторинг и отчеты

### Веб-дашборд
- **URL**: http://localhost:8080
- **Функции**: Мониторинг в реальном времени, метрики качества, детальные результаты

### Grafana
- **URL**: http://localhost:3000
- **Логин**: admin / admin
- **Функции**: Расширенная аналитика, графики производительности

### Prometheus
- **URL**: http://localhost:9090
- **Функции**: Сбор и хранение метрик

### Отчеты
- **JSON**: `test-results/report.json` - Структурированные данные
- **TXT**: `test-results/report.txt` - Человекочитаемый отчет
- **HTML**: `reports/` - Веб-отчеты
- **PDF**: `reports/` - Печатные отчеты

## 📋 Структура результатов

### Метрики производительности
- Среднее время ответа
- Медианное время ответа
- Процент успешных запросов
- Частота ошибок

### Метрики качества
- **Точность анализа**: Корректность интерпретации медицинских кодов
- **Ясность объяснений**: Понятность для пациентов
- **Уверенность системы**: Надежность рекомендаций
- **Соответствие стандартам**: HIPAA, медицинские дисклеймеры

### Детальные результаты
```json
{
  "test_id": "primary_bill_analysis_medical_bill_1234567890",
  "prompt_type": "primary_bill_analysis",
  "document_type": "medical_bill",
  "complexity": "medium",
  "success": true,
  "response_time": 2.5,
  "accuracy_score": 9.2,
  "clarity_score": 8.8,
  "confidence_score": 8.5,
  "issues_found": ["duplicate_charge_detected"],
  "metrics": {
    "has_plain_english": true,
    "has_financial_breakdown": true,
    "has_error_detection": true,
    "uses_formatting": true,
    "hipaa_compliant": true
  }
}
```

## 🔧 Конфигурация

### Переменные окружения (.env)
```env
# Hathr API
HATHR_CLIENT_ID=your_client_id
HATHR_CLIENT_SECRET=your_client_secret

# База данных
POSTGRES_DB=test_results
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password

# Мониторинг
GRAFANA_ADMIN_PASSWORD=admin
```

### Настройка тестирования
Можно изменить параметры тестирования в `automated-test-runner.py`:
- Количество тестовых файлов для каждого типа
- Пороговые значения для метрик
- Время ожидания между запросами
- Критерии оценки качества

## 🐛 Устранение неполадок

### Частые проблемы

**1. Ошибка аутентификации Hathr API**
```bash
# Проверьте учетные данные в .env
cat .env

# Проверьте доступность API
curl -X POST "https://hathr.auth-fips.us-gov-west-1.amazoncognito.com/oauth2/token" \
  -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET&scope=hathr/llm"
```

**2. Проблемы с Docker**
```bash
# Перезапуск контейнеров
docker-compose down
docker-compose up -d

# Очистка кэша Docker
docker system prune -a
```

**3. Отсутствие тестовых данных**
```bash
# Принудительная генерация данных
./scripts/run-tests.sh --generate-data
```

**4. Проблемы с базой данных**
```bash
# Проверка статуса PostgreSQL
docker-compose exec test-database pg_isready -U test_user

# Сброс базы данных
docker-compose down -v
docker-compose up -d test-database
```

### Логи и отладка

```bash
# Просмотр всех логов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs prompt-tester

# Логи в реальном времени
docker-compose logs -f prompt-tester

# Проверка статуса контейнеров
docker-compose ps
```

## 📚 Дополнительные ресурсы

### Документация
- [План тестирования промтов](План_тестирования_промтов.md)
- [API описание Hathr](api_description.md)
- [Промты для Claude](Decoder%20MD%20Prompts%20for%20Claude.md)

### Полезные команды
```bash
# Экспорт результатов в CSV
python -c "
import json
import pandas as pd
with open('test-results/report.json') as f:
    data = json.load(f)
df = pd.DataFrame(data['detailed_results'])
df.to_csv('test-results/results.csv', index=False)
"

# Создание резервной копии результатов
tar -czf test-results-backup-$(date +%Y%m%d).tar.gz test-results/

# Мониторинг использования ресурсов
docker stats
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

Этот проект предназначен для внутреннего использования в рамках разработки BillDecoder/LabDecoder.

---

**Поддержка**: При возникновении проблем создайте issue в репозитории или обратитесь к команде разработки.
