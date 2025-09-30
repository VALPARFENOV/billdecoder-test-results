#!/usr/bin/env python3
"""
Тест лабораторных результатов с Hathr API
"""

import json
import requests
import time

def test_lab_results():
    """Тестирует анализ лабораторных результатов"""
    
    # Конфигурация API
    client_id = "4vau54clia0s5esf9ahojcn7kv"
    client_secret = "i0n0t1kbihsl44tbjsvbkhml865ln8d2p4bq9afrp649km3jidq"
    scope = "hathr/llm"
    token_url = "https://hathr.auth-fips.us-gov-west-1.amazoncognito.com/oauth2/token"
    api_url = "https://api.hathr.ai/v1/chat"
    
    print("🔑 Получение токена доступа...")
    
    # Получаем токен
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    
    token_response = requests.post(token_url, data=token_data)
    
    if token_response.status_code != 200:
        print(f"❌ Ошибка получения токена: {token_response.status_code} - {token_response.text}")
        return
    
    access_token = token_response.json()["access_token"]
    print(f"✅ Токен получен")
    
    # Загружаем лабораторные результаты
    print("\n📄 Загрузка лабораторных результатов...")
    
    try:
        with open("test-data/lab-results/lab_001_full.json", 'r', encoding='utf-8') as f:
            lab_data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл test-data/lab-results/lab_001_full.json не найден!")
        return
    
    # Форматируем документ для промта
    document_text = f"""
LABORATORY RESULTS

Patient: {lab_data['patient']['name']}
Test Date: {lab_data['test_date']}
Laboratory: {lab_data['provider']['name']}

Results:
"""
    for value in lab_data.get("lab_values", []):
        status_symbol = "✅" if value["status"] == "normal" else "⚠️" if value["status"] in ["high", "low"] else "❌"
        document_text += f"{status_symbol} {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']})\n"
    
    if lab_data.get('clinical_notes'):
        document_text += f"\nClinical Notes: {lab_data['clinical_notes']}"
    
    # Промт для анализа лабораторных результатов
    prompt = """You are a medical educator helping patients understand their lab results. Analyze these lab values and provide:

1. **Results Summary**: Overall health picture in simple terms
2. **Individual Test Explanations**: What each test measures and why it matters
3. **Abnormal Values**: Clear explanation of any concerning results
4. **Trend Analysis**: If multiple dates available, show changes over time
5. **Next Steps**: What patient should discuss with their doctor
6. **Educational Content**: Brief background on relevant health conditions

Use analogies and everyday language. Avoid medical jargon. Always remind patients to consult their healthcare provider for medical advice."""
    
    # Формируем сообщение
    message = f"{prompt}\n\n[LAB RESULTS DATA]\n{document_text}"
    
    print("\n🤖 Отправка запроса к Hathr API...")
    
    # Отправляем запрос
    payload = {
        "messages": [
            {"role": "user", "text": message}
        ],
        "temperature": 0.2,
        "topP": 1.0
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    response = requests.post(api_url, json=payload, headers=headers)
    response_time = time.time() - start_time
    
    print(f"⏱️ Время ответа: {response_time:.2f} секунд")
    
    if response.status_code == 200:
        response_data = response.json()
        print(f"✅ Успешный ответ!")
        
        # Извлекаем текст ответа
        if "response" in response_data and "text" in response_data["response"]:
            ai_response = response_data["response"]["text"]
            print(f"\n🤖 Ответ AI:")
            print("-" * 50)
            print(ai_response)
            print("-" * 50)
            
            # Показываем статистику использования токенов
            if "usage" in response_data["response"]:
                usage = response_data["response"]["usage"]
                print(f"\n📈 Статистика токенов:")
                print(f"   Входные токены: {usage.get('inputTokens', 'N/A')}")
                print(f"   Выходные токены: {usage.get('outputTokens', 'N/A')}")
                print(f"   Всего токенов: {usage.get('totalTokens', 'N/A')}")
        else:
            print(f"❌ Неожиданная структура ответа: {response_data}")
    else:
        print(f"❌ Ошибка API: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_lab_results()
