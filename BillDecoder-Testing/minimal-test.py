#!/usr/bin/env python3
"""
Минимальный тест для проверки работы Hathr API с одним документом
"""

import json
import requests
import time

def test_single_document():
    """Тестирует один документ с простым промтом"""
    
    # Конфигурация API (рабочие ключи из test2.sh)
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
    print(f"✅ Токен получен (длина: {len(access_token)})")
    
    # Загружаем тестовый документ
    print("\n📄 Загрузка тестового документа...")
    
    try:
        with open("test-data/bills/bill_001_simple.json", 'r', encoding='utf-8') as f:
            bill_data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл test-data/bills/bill_001_simple.json не найден!")
        return
    
    # Форматируем документ для промта
    document_text = f"""
MEDICAL BILL

Provider: {bill_data['provider']['name']}
Patient: {bill_data['patient']['name']}
Service Date: {bill_data['service_date']}

Services:
"""
    for service in bill_data.get("services", []):
        document_text += f"""
Code: {service['code']}
Description: {service['description']}
Charge: ${service['charge']}
"""
    
    document_text += f"""
Total Charges: ${bill_data['financial_summary']['total_charges']}
Insurance Payment: ${bill_data['financial_summary']['insurance_payment']}
Patient Responsibility: ${bill_data['financial_summary']['patient_responsibility']}
"""
    
    # Простой промт для тестирования
    prompt = """Classify this healthcare document and extract key metadata:

Document types to identify:
- Medical bill/invoice
- EOB (Explanation of Benefits)
- Lab results
- Imaging reports
- Insurance correspondence
- Provider statements

Extract:
- Document type
- Date of service
- Provider name
- Patient identifier (redacted)
- Key services/tests mentioned
- Urgency level (routine/urgent/emergency)"""
    
    # Формируем сообщение
    message = f"{prompt}\n\n[DOCUMENT]\n{document_text}"
    
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
        print(f"📊 Структура ответа: {list(response_data.keys())}")
        
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
    test_single_document()
