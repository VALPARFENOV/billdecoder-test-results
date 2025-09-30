#!/usr/bin/env python3
"""
Упрощенный тестер промтов для BillDecoder/LabDecoder
Запускает минимальные тесты без Docker инфраструктуры
"""

import json
import os
import time
import requests
from typing import Dict, List, Any
from datetime import datetime

class SimplePromptTester:
    """Упрощенный тестер промтов"""
    
    def __init__(self, hathr_config: Dict[str, str]):
        self.hathr_config = hathr_config
        self.test_results = []
        
    def get_access_token(self) -> str:
        """Получает токен доступа от Hathr API"""
        token_url = self.hathr_config["token_url"]
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.hathr_config["client_id"],
            "client_secret": self.hathr_config["client_secret"],
            "scope": self.hathr_config["scope"]
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Ошибка получения токена: {response.status_code} - {response.text}")
    
    def call_hathr_api(self, prompt: str, document_data: str = None) -> tuple[bool, str, float]:
        """Вызывает Hathr API с промтом"""
        try:
            access_token = self.get_access_token()
            api_url = self.hathr_config["api_url"]
            
            # Формируем сообщение
            if document_data:
                message = f"{prompt}\n\n[ДОКУМЕНТ]\n{document_data}"
            else:
                message = prompt
            
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
            
            if response.status_code == 200:
                response_data = response.json()
                # Проверяем структуру ответа
                if "response" in response_data and "text" in response_data["response"]:
                    return True, response_data["response"]["text"], response_time
                elif "data" in response_data and "message" in response_data["data"]:
                    return True, response_data["data"]["message"], response_time
                else:
                    return False, f"Unexpected response structure: {response_data}", response_time
            else:
                return False, f"API Error: {response.status_code} - {response.text}", response_time
                
        except Exception as e:
            return False, f"Exception: {str(e)}", 0.0
    
    def format_document_for_prompt(self, document_data: Dict[str, Any]) -> str:
        """Форматирует данные документа для передачи в промт"""
        if document_data["document_type"] == "medical_bill":
            result = f"""
MEDICAL BILL

Provider: {document_data['provider']['name']}
Patient: {document_data['patient']['name']}
Service Date: {document_data['service_date']}

Services:
"""
            for service in document_data.get("services", []):
                result += f"""
Code: {service['code']}
Description: {service['description']}
Charge: ${service['charge']}
"""
            result += f"""
Total Charges: ${document_data['financial_summary']['total_charges']}
Insurance Payment: ${document_data['financial_summary']['insurance_payment']}
Patient Responsibility: ${document_data['financial_summary']['patient_responsibility']}
"""
            return result
        
        elif document_data["document_type"] == "lab_results":
            result = f"""
LABORATORY RESULTS

Patient: {document_data['patient']['name']}
Test Date: {document_data['test_date']}

Results:
"""
            for value in document_data.get("lab_values", []):
                status_symbol = "✅" if value["status"] == "normal" else "⚠️" if value["status"] in ["high", "low"] else "❌"
                result += f"{status_symbol} {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']})\n"
            
            return result
        
        elif document_data["document_type"] == "eob":
            result = f"""
EOB (EXPLANATION OF BENEFITS)

Insurance Company: {document_data['insurance_company']['name']}
Patient: {document_data['patient']['name']}
Service Date: {document_data['service_date']}

Coverage Details:
"""
            for service in document_data.get("services", []):
                status_symbol = "✅" if service["coverage_status"] == "covered" else "❌"
                result += f"{status_symbol} {service['code']}: ${service['billed_amount']} -> Insurance: ${service['insurance_payment']}, Patient: ${service['patient_responsibility']}\n"
                if service.get("denial_reason"):
                    result += f"   Denial Reason: {service['denial_reason']}\n"
            
            return result
        
        return json.dumps(document_data, ensure_ascii=False, indent=2)
    
    def test_simple_prompts(self) -> None:
        """Запускает простые тесты промтов"""
        print("🚀 Запуск простых тестов промтов...")
        
        # Простые промты для тестирования
        prompts = {
            "document_classification": """Classify this healthcare document and extract key metadata:

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
- Urgency level (routine/urgent/emergency)""",
            
            "confidence_scoring": """Rate your confidence in this analysis on a scale of 1-10 and explain any limitations:

Consider factors:
- Document quality/readability
- Completeness of information
- Complexity of medical terminology
- Potential for misinterpretation
- Need for human expert review

Provide specific recommendations for when users should seek additional professional help."""
        }
        
        # Загружаем несколько тестовых файлов
        test_files = []
        for root, dirs, files in os.walk("test-data"):
            for file in files:
                if file.endswith('.json') and len(test_files) < 6:  # Берем только 6 файлов
                    test_files.append(os.path.join(root, file))
        
        total_tests = 0
        successful_tests = 0
        
        for file_path in test_files:
            print(f"\n📋 Тестирование файла: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                document_data = json.load(f)
            
            document_text = self.format_document_for_prompt(document_data)
            
            for prompt_name, prompt_text in prompts.items():
                print(f"  🔍 Тестирование промта: {prompt_name}")
                
                success, response, response_time = self.call_hathr_api(prompt_text, document_text)
                total_tests += 1
                
                if success:
                    successful_tests += 1
                    print(f"    ✅ Успех - Время: {response_time:.2f}с")
                    print(f"    📝 Ответ: {response[:100]}...")
                else:
                    print(f"    ❌ Ошибка: {response}")
                
                # Небольшая пауза между запросами
                time.sleep(2)
        
        print(f"\n📊 Результаты тестирования:")
        print(f"   Всего тестов: {total_tests}")
        print(f"   Успешных: {successful_tests}")
        print(f"   Неудачных: {total_tests - successful_tests}")
        print(f"   Процент успеха: {successful_tests/total_tests*100:.1f}%")

def main():
    """Основная функция для запуска простых тестов"""
    # Конфигурация Hathr API (из TestCode/test2.sh - рабочие ключи)
    hathr_config = {
        "client_id": "4vau54clia0s5esf9ahojcn7kv",
        "client_secret": "i0n0t1kbihsl44tbjsvbkhml865ln8d2p4bq9afrp649km3jidq",
        "scope": "hathr/llm",
        "token_url": "https://hathr.auth-fips.us-gov-west-1.amazoncognito.com/oauth2/token",
        "api_url": "https://api.hathr.ai/v1/chat"
    }
    
    # Создаем тестер
    tester = SimplePromptTester(hathr_config)
    
    # Проверяем наличие тестовых данных
    if not os.path.exists("test-data"):
        print("❌ Директория test-data не найдена!")
        print("Запустите сначала test-data-generator.py для создания тестовых данных")
        return
    
    # Запускаем простые тесты
    try:
        tester.test_simple_prompts()
        print("\n🎉 Простые тесты завершены!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")

if __name__ == "__main__":
    main()
