#!/bin/bash

# Скрипт для запуска тестирования промтов
# BillDecoder/LabDecoder Prompt Testing Runner

set -e

echo "🧪 Запуск тестирования промтов BillDecoder/LabDecoder..."

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose и попробуйте снова."
    exit 1
fi

# Проверяем наличие файла .env
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Запустите сначала ./scripts/setup.sh"
    exit 1
fi

# Функция для отображения справки
show_help() {
    echo "Использование: $0 [ОПЦИИ]"
    echo ""
    echo "ОПЦИИ:"
    echo "  -h, --help              Показать эту справку"
    echo "  -g, --generate-data     Сгенерировать тестовые данные"
    echo "  -t, --test              Запустить тестирование промтов"
    echo "  -f, --full              Полный цикл: генерация данных + тестирование"
    echo "  -c, --clean             Очистить результаты предыдущих тестов"
    echo "  -d, --daemon            Запустить в фоновом режиме"
    echo "  -l, --logs              Показать логи тестирования"
    echo "  -s, --status            Показать статус контейнеров"
    echo "  -r, --report            Сгенерировать отчет"
    echo ""
    echo "ПРИМЕРЫ:"
    echo "  $0 --full               # Полный цикл тестирования"
    echo "  $0 --generate-data      # Только генерация данных"
    echo "  $0 --test --daemon      # Тестирование в фоне"
    echo "  $0 --logs               # Просмотр логов"
}

# Функция для генерации тестовых данных
generate_test_data() {
    echo "📊 Генерация тестовых данных..."
    
    # Проверяем, запущены ли контейнеры
    if ! docker-compose ps | grep -q "Up"; then
        echo "🚀 Запуск контейнеров..."
        docker-compose up -d test-database redis
        sleep 10
    fi
    
    # Генерируем тестовые данные
    docker-compose run --rm prompt-tester python test-data-generator.py
    
    echo "✅ Тестовые данные сгенерированы!"
}

# Функция для запуска тестирования
run_tests() {
    echo "🧪 Запуск тестирования промтов..."
    
    # Проверяем наличие тестовых данных
    if [ ! -d "test-data" ] || [ -z "$(ls -A test-data)" ]; then
        echo "⚠️ Тестовые данные не найдены. Генерируем..."
        generate_test_data
    fi
    
    # Запускаем тестирование
    if [ "$DAEMON_MODE" = true ]; then
        echo "🔄 Запуск тестирования в фоновом режиме..."
        docker-compose up -d prompt-tester
    else
        echo "🔄 Запуск тестирования..."
        docker-compose run --rm prompt-tester python automated-test-runner.py
    fi
    
    echo "✅ Тестирование завершено!"
}

# Функция для очистки результатов
clean_results() {
    echo "🧹 Очистка результатов предыдущих тестов..."
    
    # Останавливаем контейнеры
    docker-compose down
    
    # Удаляем результаты тестов
    rm -rf test-results/*
    rm -rf reports/*
    
    # Очищаем логи
    docker-compose logs --no-color > /dev/null 2>&1 || true
    
    echo "✅ Очистка завершена!"
}

# Функция для просмотра логов
show_logs() {
    echo "📋 Логи тестирования:"
    docker-compose logs -f prompt-tester
}

# Функция для показа статуса
show_status() {
    echo "📊 Статус контейнеров:"
    docker-compose ps
    
    echo ""
    echo "📈 Статистика:"
    if [ -f "test-results/report.json" ]; then
        echo "Последний отчет: $(stat -c %y test-results/report.json)"
        echo "Размер отчета: $(du -h test-results/report.json | cut -f1)"
    else
        echo "Отчеты не найдены"
    fi
    
    if [ -d "test-data" ]; then
        echo "Тестовых файлов: $(find test-data -name "*.json" | wc -l)"
    else
        echo "Тестовые данные не найдены"
    fi
}

# Функция для генерации отчета
generate_report() {
    echo "📄 Генерация отчета..."
    
    if [ ! -f "test-results/report.json" ]; then
        echo "❌ Отчет не найден. Запустите сначала тестирование."
        exit 1
    fi
    
    # Создаем HTML отчет
    docker-compose run --rm report-generator python report-generator.py
    
    echo "✅ Отчет сгенерирован в директории reports/"
}

# Функция для полного цикла
run_full_cycle() {
    echo "🔄 Запуск полного цикла тестирования..."
    
    # Очищаем предыдущие результаты
    clean_results
    
    # Генерируем данные
    generate_test_data
    
    # Запускаем тестирование
    run_tests
    
    # Генерируем отчет
    generate_report
    
    echo "🎉 Полный цикл тестирования завершен!"
    echo "📊 Результаты доступны в:"
    echo "  - Веб-дашборд: http://localhost:8080"
    echo "  - Отчеты: reports/"
    echo "  - JSON данные: test-results/"
}

# Парсинг аргументов командной строки
GENERATE_DATA=false
RUN_TESTS=false
FULL_CYCLE=false
CLEAN_RESULTS=false
DAEMON_MODE=false
SHOW_LOGS=false
SHOW_STATUS=false
GENERATE_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -g|--generate-data)
            GENERATE_DATA=true
            shift
            ;;
        -t|--test)
            RUN_TESTS=true
            shift
            ;;
        -f|--full)
            FULL_CYCLE=true
            shift
            ;;
        -c|--clean)
            CLEAN_RESULTS=true
            shift
            ;;
        -d|--daemon)
            DAEMON_MODE=true
            shift
            ;;
        -l|--logs)
            SHOW_LOGS=true
            shift
            ;;
        -s|--status)
            SHOW_STATUS=true
            shift
            ;;
        -r|--report)
            GENERATE_REPORT=true
            shift
            ;;
        *)
            echo "❌ Неизвестная опция: $1"
            show_help
            exit 1
            ;;
    esac
done

# Выполняем запрошенные действия
if [ "$FULL_CYCLE" = true ]; then
    run_full_cycle
elif [ "$CLEAN_RESULTS" = true ]; then
    clean_results
elif [ "$GENERATE_DATA" = true ]; then
    generate_test_data
elif [ "$RUN_TESTS" = true ]; then
    run_tests
elif [ "$SHOW_LOGS" = true ]; then
    show_logs
elif [ "$SHOW_STATUS" = true ]; then
    show_status
elif [ "$GENERATE_REPORT" = true ]; then
    generate_report
else
    echo "❌ Не указана опция. Используйте --help для справки."
    exit 1
fi
