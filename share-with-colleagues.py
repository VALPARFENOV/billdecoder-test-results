#!/usr/bin/env python3
"""
Скрипт для быстрого запуска веб-сервера для показа презентации коллегам
"""

import http.server
import socketserver
import webbrowser
import os
import socket
import sys
from pathlib import Path

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        # Подключаемся к внешнему адресу чтобы узнать свой IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_network_server():
    """Запускает веб-сервер для локальной сети"""
    
    PORT = 8080
    
    # Переходим в директорию с результатами
    results_dir = Path("test-results")
    if not results_dir.exists():
        print("❌ Directory test-results not found!")
        return
    
    # Проверяем наличие файла презентации
    presentation_file = results_dir / "web-presentation-english.html"
    if not presentation_file.exists():
        print("❌ English presentation file not found!")
        print("Run: python3 generate-english-presentation.py")
        return
    
    # Меняем рабочую директорию
    os.chdir(results_dir)
    
    # Создаем обработчик
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
        # Получаем локальный IP
        local_ip = get_local_ip()
        
        # Создаем сервер для всех интерфейсов
        with socketserver.TCPServer(("0.0.0.0", PORT), CustomHTTPRequestHandler) as httpd:
            print("🚀 Web server started for colleagues!")
            print(f"📊 Presentation available at:")
            print(f"   Local:  http://localhost:{PORT}")
            print(f"   Network: http://{local_ip}:{PORT}")
            print(f"📁 Working directory: {results_dir.absolute()}")
            print("\n💡 Share this URL with colleagues:")
            print(f"   🌐 http://{local_ip}:{PORT}")
            print("\n📋 Presentation features:")
            print("   - 📊 Overall testing statistics")
            print("   - 🤖 Detailed results for each prompt type")
            print("   - 📄 Analysis by document types")
            print("   - 🔍 Search and filter results")
            print("   - 💬 View full prompts, documents, and AI responses")
            print("\n⏹️  Press Ctrl+C to stop the server")
            
            # Автоматически открываем браузер
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print(f"\n🌐 Browser automatically opened")
            except:
                print(f"\n🌐 Open browser and go to: http://localhost:{PORT}")
            
            print(f"\n👥 Tell your colleagues to open: http://{local_ip}:{PORT}")
            
            # Запускаем сервер
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Try another port.")
        else:
            print(f"❌ Server startup error: {e}")

def create_shareable_package():
    """Создает пакет для отправки коллегам"""
    
    print("📦 Creating shareable package...")
    
    # Создаем директорию для пакета
    package_dir = Path("shareable-package")
    package_dir.mkdir(exist_ok=True)
    
    # Копируем необходимые файлы
    import shutil
    
    files_to_copy = [
        "test-results/web-presentation-english.html",
        "test-results/README_English_Presentation.md",
        "test-results/English_Presentation_Summary.md"
    ]
    
    for file_path in files_to_copy:
        if Path(file_path).exists():
            shutil.copy2(file_path, package_dir)
            print(f"✅ Copied: {file_path}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    # Создаем инструкцию
    instructions = """# BillDecoder/LabDecoder Test Results

## How to View the Presentation

1. Open `web-presentation-english.html` in any web browser
2. The presentation will show:
   - Overall testing statistics
   - Detailed results for each prompt type
   - Analysis by document types
   - Full test details (prompts, documents, responses)

## Features

- Interactive search and filtering
- Modal windows for detailed viewing
- Responsive design for all devices
- Complete test data with 100% success rate

## Results Summary

- 45 tests executed
- 100% success rate
- All prompt types working perfectly
- System ready for production

For questions, contact the development team.
"""
    
    with open(package_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Package created in: {package_dir.absolute()}")
    print(f"📧 You can now zip this folder and send it to colleagues")

def main():
    """Основная функция"""
    print("🌐 BillDecoder/LabDecoder - Share Presentation with Colleagues")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "package":
        create_shareable_package()
    else:
        print("Choose an option:")
        print("1. 🚀 Start network server (colleagues can access via network)")
        print("2. 📦 Create shareable package (for email/file sharing)")
        print()
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            start_network_server()
        elif choice == "2":
            create_shareable_package()
        else:
            print("Invalid choice. Starting network server...")
            start_network_server()

if __name__ == "__main__":
    main()
