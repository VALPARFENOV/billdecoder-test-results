#!/usr/bin/env python3
"""
Тест EOB (Explanation of Benefits) с Hathr API
"""

import json
import requests
import time

def test_eob():
    """Тестирует анализ EOB документов"""
    
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
    
    # Загружаем EOB документ
    print("\n📄 Загрузка EOB документа...")
    
    try:
        with open("test-data/eob/eob_001.json", 'r', encoding='utf-8') as f:
            eob_data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл test-data/eob/eob_001.json не найден!")
        return
    
    # Форматируем документ для промта
    document_text = f"""
EXPLANATION OF BENEFITS (EOB)

Patient: {eob_data['patient']['name']}
Member ID: {eob_data['patient']['member_id']}
Date of Service: {eob_data['service_date']}
Provider: {eob_data['provider']['name']}
Insurance: {eob_data['insurance_company']['name']}
Claim Number: {eob_data['claim_number']}

Claim Details:
"""
    for service in eob_data.get("services", []):
        document_text += f"""
Service: {service['description']}
Code: {service['code']}
Date: {service.get('date', 'N/A')}
Billed Amount: ${service['billed_amount']}
Insurance Paid: ${service['insurance_payment']}
Patient Responsibility: ${service['patient_responsibility']}
Coverage Status: {service['coverage_status']}
"""
    
    # Вычисляем общие суммы
    total_billed = sum(service['billed_amount'] for service in eob_data.get("services", []))
    total_insurance = sum(service['insurance_payment'] for service in eob_data.get("services", []))
    total_patient = sum(service['patient_responsibility'] for service in eob_data.get("services", []))
    
    document_text += f"""
Financial Summary:
Total Billed: ${total_billed:.2f}
Insurance Payment: ${total_insurance:.2f}
Patient Responsibility: ${total_patient:.2f}
"""
    
    # Промт для анализа EOB
    prompt = """You are a healthcare financial counselor helping patients understand their insurance EOB. Analyze this document and provide:

1. **EOB Summary**: What this document tells us about the claim
2. **Service Breakdown**: Explanation of each service and its coverage
3. **Financial Impact**: What the patient owes and why
4. **Coverage Analysis**: How insurance applied their benefits
5. **Action Items**: Any steps the patient needs to take
6. **Questions to Ask**: What to discuss with insurance or provider
7. **Appeal Information**: If applicable, guidance on disputing charges

Use clear, non-technical language. Help patients understand their rights and options."""
    
    # Формируем сообщение
    message = f"{prompt}\n\n[EOB DATA]\n{document_text}"
    
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
    test_eob()
