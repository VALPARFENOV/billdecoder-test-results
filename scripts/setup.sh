#!/bin/bash

# Скрипт настройки инфраструктуры для тестирования промтов
# BillDecoder/LabDecoder Testing Infrastructure Setup

set -e

echo "🚀 Настройка инфраструктуры тестирования промтов BillDecoder/LabDecoder..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p test-data/{bills,lab-results,eob,edge-cases}
mkdir -p test-results/{reports,logs,metrics}
mkdir -p scripts
mkdir -p database
mkdir -p test-dashboard/{css,js}
mkdir -p monitoring/{grafana/{dashboards,datasources},prometheus}
mkdir -p reports

# Создаем файл .env если его нет
if [ ! -f .env ]; then
    echo "📝 Создание файла .env..."
    cat > .env << EOF
# Hathr API Configuration
HATHR_CLIENT_ID=your_client_id_here
HATHR_CLIENT_SECRET=your_client_secret_here

# Database Configuration
POSTGRES_DB=test_results
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password

# Redis Configuration
REDIS_PASSWORD=

# Monitoring
GRAFANA_ADMIN_PASSWORD=admin
EOF
    echo "✅ Файл .env создан. Пожалуйста, обновите учетные данные Hathr API."
fi

# Создаем SQL скрипт для инициализации базы данных
echo "🗄️ Создание схемы базы данных..."
cat > database/init.sql << 'EOF'
-- Создание таблиц для хранения результатов тестирования

CREATE TABLE IF NOT EXISTS test_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) UNIQUE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_tests INTEGER DEFAULT 0,
    successful_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) REFERENCES test_runs(run_id),
    test_id VARCHAR(255) NOT NULL,
    prompt_type VARCHAR(100) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    complexity VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    response_time FLOAT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    raw_response TEXT,
    confidence_score FLOAT,
    accuracy_score FLOAT,
    clarity_score FLOAT,
    issues_found TEXT[],
    metrics JSONB
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) REFERENCES test_runs(run_id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quality_metrics (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) REFERENCES test_runs(run_id),
    prompt_type VARCHAR(100) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    accuracy_avg FLOAT,
    clarity_avg FLOAT,
    confidence_avg FLOAT,
    test_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_test_results_run_id ON test_results(run_id);
CREATE INDEX IF NOT EXISTS idx_test_results_prompt_type ON test_results(prompt_type);
CREATE INDEX IF NOT EXISTS idx_test_results_document_type ON test_results(document_type);
CREATE INDEX IF NOT EXISTS idx_test_results_timestamp ON test_results(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_run_id ON performance_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_quality_metrics_run_id ON quality_metrics(run_id);

-- Функция для автоматического обновления статистики
CREATE OR REPLACE FUNCTION update_test_run_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE test_runs 
    SET 
        total_tests = (SELECT COUNT(*) FROM test_results WHERE run_id = NEW.run_id),
        successful_tests = (SELECT COUNT(*) FROM test_results WHERE run_id = NEW.run_id AND success = true),
        failed_tests = (SELECT COUNT(*) FROM test_results WHERE run_id = NEW.run_id AND success = false)
    WHERE run_id = NEW.run_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического обновления статистики
DROP TRIGGER IF EXISTS trigger_update_test_run_stats ON test_results;
CREATE TRIGGER trigger_update_test_run_stats
    AFTER INSERT ON test_results
    FOR EACH ROW
    EXECUTE FUNCTION update_test_run_stats();
EOF

# Создаем конфигурацию Nginx для дашборда
echo "🌐 Создание конфигурации Nginx..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    server {
        listen       80;
        server_name  localhost;
        
        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }
        
        location /api/ {
            proxy_pass http://prompt-tester:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /reports/ {
            alias /app/test-results/reports/;
            autoindex on;
        }
        
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }
}
EOF

# Создаем простой HTML дашборд
echo "📊 Создание веб-дашборда..."
cat > test-dashboard/index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BillDecoder/LabDecoder - Результаты тестирования</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .metric-card {
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .status-success { color: #28a745; }
        .status-error { color: #dc3545; }
        .status-warning { color: #ffc107; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-vial"></i> BillDecoder/LabDecoder Testing Dashboard
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <h2>Результаты тестирования промтов</h2>
                <p class="text-muted">Мониторинг качества и производительности AI-промтов</p>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card bg-primary text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="card-title" id="total-tests">-</h4>
                                <p class="card-text">Всего тестов</p>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-flask fa-2x"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="card metric-card bg-success text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="card-title" id="success-rate">-</h4>
                                <p class="card-text">Успешных тестов</p>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-check-circle fa-2x"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="card metric-card bg-info text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="card-title" id="avg-response-time">-</h4>
                                <p class="card-text">Среднее время ответа (с)</p>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-clock fa-2x"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="card metric-card bg-warning text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 class="card-title" id="avg-accuracy">-</h4>
                                <p class="card-text">Средняя точность</p>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-bullseye fa-2x"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Детальные результаты</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped" id="results-table">
                                <thead>
                                    <tr>
                                        <th>Тест ID</th>
                                        <th>Промт</th>
                                        <th>Тип документа</th>
                                        <th>Сложность</th>
                                        <th>Статус</th>
                                        <th>Время ответа</th>
                                        <th>Точность</th>
                                        <th>Ясность</th>
                                        <th>Уверенность</th>
                                    </tr>
                                </thead>
                                <tbody id="results-tbody">
                                    <tr>
                                        <td colspan="9" class="text-center">Загрузка данных...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Функция для загрузки данных
        async function loadTestResults() {
            try {
                const response = await fetch('/api/test-results');
                const data = await response.json();
                
                // Обновляем метрики
                document.getElementById('total-tests').textContent = data.summary.total_tests || 0;
                document.getElementById('success-rate').textContent = 
                    data.summary.successful_tests || 0;
                document.getElementById('avg-response-time').textContent = 
                    (data.performance.average_response_time || 0).toFixed(2);
                document.getElementById('avg-accuracy').textContent = 
                    (data.quality.accuracy.average || 0).toFixed(1);
                
                // Обновляем таблицу
                const tbody = document.getElementById('results-tbody');
                tbody.innerHTML = '';
                
                if (data.detailed_results && data.detailed_results.length > 0) {
                    data.detailed_results.forEach(result => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${result.test_id}</td>
                            <td>${result.prompt_type}</td>
                            <td>${result.document_type}</td>
                            <td>${result.complexity}</td>
                            <td><span class="badge ${result.success ? 'bg-success' : 'bg-danger'}">
                                ${result.success ? 'Успех' : 'Ошибка'}
                            </span></td>
                            <td>${result.response_time ? result.response_time.toFixed(2) : '-'}</td>
                            <td>${result.accuracy_score ? result.accuracy_score.toFixed(1) : '-'}</td>
                            <td>${result.clarity_score ? result.clarity_score.toFixed(1) : '-'}</td>
                            <td>${result.confidence_score ? result.confidence_score.toFixed(1) : '-'}</td>
                        `;
                        tbody.appendChild(row);
                    });
                } else {
                    tbody.innerHTML = '<tr><td colspan="9" class="text-center">Нет данных</td></tr>';
                }
                
            } catch (error) {
                console.error('Ошибка загрузки данных:', error);
                document.getElementById('results-tbody').innerHTML = 
                    '<tr><td colspan="9" class="text-center text-danger">Ошибка загрузки данных</td></tr>';
            }
        }
        
        // Загружаем данные при загрузке страницы
        document.addEventListener('DOMContentLoaded', loadTestResults);
        
        // Обновляем данные каждые 30 секунд
        setInterval(loadTestResults, 30000);
    </script>
</body>
</html>
EOF

# Создаем конфигурацию Prometheus
echo "📈 Создание конфигурации мониторинга..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'prompt-tester'
    static_configs:
      - targets: ['prompt-tester:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['test-database:5432']
    scrape_interval: 30s
EOF

# Создаем конфигурацию Grafana
mkdir -p monitoring/grafana/datasources
cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

echo "✅ Настройка инфраструктуры завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Обновите учетные данные Hathr API в файле .env"
echo "2. Запустите: docker-compose up -d"
echo "3. Откройте дашборд: http://localhost:8080"
echo "4. Мониторинг: http://localhost:3000 (Grafana)"
echo "5. Метрики: http://localhost:9090 (Prometheus)"
echo ""
echo "🔧 Полезные команды:"
echo "  docker-compose logs -f prompt-tester  # Просмотр логов"
echo "  docker-compose exec prompt-tester python test-data-generator.py  # Генерация тестовых данных"
echo "  docker-compose exec prompt-tester python automated-test-runner.py  # Запуск тестов"
