#!/usr/bin/env python3
"""
Простой веб-сервер для просмотра презентации результатов тестирования
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_server():
    """Запускает локальный веб-сервер"""
    
    # Определяем порт
    PORT = 8080
    
    # Переходим в директорию с результатами
    results_dir = Path("test-results")
    if not results_dir.exists():
        print("❌ Директория test-results не найдена!")
        return
    
    # Проверяем наличие файла презентации
    presentation_file = results_dir / "web-presentation-with-data.html"
    if not presentation_file.exists():
        print("❌ Файл презентации не найден! Запустите сначала generate-web-presentation.py")
        return
    
    # Меняем рабочую директорию
    os.chdir(results_dir)
    
    # Создаем обработчик для обслуживания файлов
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Добавляем заголовки для CORS
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_GET(self):
            # Если запрашивается корневая директория, показываем английскую презентацию
            if self.path == '/' or self.path == '':
                self.path = '/web-presentation-english.html'
            return super().do_GET()
    
    try:
        # Создаем сервер
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 Веб-сервер запущен на http://localhost:{PORT}")
            print(f"📊 Презентация доступна по адресу: http://localhost:{PORT}")
            print(f"📁 Рабочая директория: {results_dir.absolute()}")
            print("\n💡 Функции презентации:")
            print("   - 📊 Общая статистика тестирования")
            print("   - 🤖 Детальные результаты по каждому промту")
            print("   - 📄 Анализ по типам документов")
            print("   - 🔍 Поиск и фильтрация результатов")
            print("   - 💬 Просмотр полных ответов AI")
            print("\n⏹️  Для остановки сервера нажмите Ctrl+C")
            
            # Автоматически открываем браузер
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print(f"\n🌐 Браузер автоматически открыт")
            except:
                print(f"\n🌐 Откройте браузер и перейдите по адресу: http://localhost:{PORT}")
            
            # Запускаем сервер
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Сервер остановлен")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Порт {PORT} уже используется. Попробуйте другой порт.")
        else:
            print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    start_server()
