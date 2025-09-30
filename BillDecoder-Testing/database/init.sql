-- Инициализация базы данных для тестирования промтов

-- Создание таблицы для результатов тестов
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(255) UNIQUE NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_file VARCHAR(255) NOT NULL,
    prompt_type VARCHAR(100) NOT NULL,
    test_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    response_time FLOAT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    response_text TEXT,
    error_message TEXT,
    quality_score FLOAT,
    safety_score FLOAT,
    performance_score FLOAT,
    metadata JSONB
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_test_results_document_type ON test_results(document_type);
CREATE INDEX IF NOT EXISTS idx_test_results_prompt_type ON test_results(prompt_type);
CREATE INDEX IF NOT EXISTS idx_test_results_timestamp ON test_results(test_timestamp);
CREATE INDEX IF NOT EXISTS idx_test_results_success ON test_results(success);

-- Создание таблицы для метрик
CREATE TABLE IF NOT EXISTS test_metrics (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES test_results(test_id)
);

-- Создание таблицы для сессий тестирования
CREATE TABLE IF NOT EXISTS test_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    session_name VARCHAR(255),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_tests INTEGER DEFAULT 0,
    successful_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    average_response_time FLOAT,
    total_tokens_used INTEGER,
    status VARCHAR(50) DEFAULT 'running'
);

-- Создание представления для статистики
CREATE OR REPLACE VIEW test_statistics AS
SELECT 
    document_type,
    prompt_type,
    COUNT(*) as total_tests,
    COUNT(CASE WHEN success = true THEN 1 END) as successful_tests,
    COUNT(CASE WHEN success = false THEN 1 END) as failed_tests,
    ROUND(AVG(response_time)::numeric, 2) as avg_response_time,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
    ROUND(AVG(safety_score)::numeric, 2) as avg_safety_score,
    ROUND(AVG(performance_score)::numeric, 2) as avg_performance_score,
    SUM(total_tokens) as total_tokens_used
FROM test_results
GROUP BY document_type, prompt_type;

-- Вставка тестовых данных (если нужно)
INSERT INTO test_sessions (session_id, session_name) 
VALUES ('initial_session', 'Initial Test Session')
ON CONFLICT (session_id) DO NOTHING;