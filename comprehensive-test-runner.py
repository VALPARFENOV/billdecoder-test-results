#!/usr/bin/env python3
"""
Комплексный тестировщик промтов для BillDecoder/LabDecoder
Работает локально без Docker, сохраняет результаты в JSON файлы
"""

import json
import requests
import time
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Tuple
import uuid

class ComprehensivePromptTester:
    def __init__(self, hathr_config: Dict[str, str]):
        self.hathr_config = hathr_config
        self.access_token = None
        self.token_expires_at = None
        self.results = []
        self.session_id = str(uuid.uuid4())
        
    def get_access_token(self) -> str:
        """Получает токен доступа к Hathr API"""
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token
            
        print("🔑 Получение нового токена доступа...")
        
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.hathr_config["client_id"],
            "client_secret": self.hathr_config["client_secret"],
            "scope": self.hathr_config["scope"]
        }
        
        try:
            response = requests.post(self.hathr_config["token_url"], data=token_data)
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info["access_token"]
                # Токен действителен 24 часа, но обновляем за час до истечения
                self.token_expires_at = time.time() + (token_info.get("expires_in", 86400) - 3600)
                print(f"✅ Токен получен (действителен до {datetime.fromtimestamp(self.token_expires_at)})")
                return self.access_token
            else:
                raise Exception(f"Ошибка получения токена: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Ошибка получения токена: {str(e)}")
    
    def test_prompt(self, document_data: Dict[str, Any], prompt_type: str, prompt_text: str) -> Tuple[bool, str, float, Dict[str, Any]]:
        """Тестирует один промт на одном документе"""
        try:
            # Получаем токен
            token = self.get_access_token()
            
            # Форматируем документ
            document_text = self.format_document_for_prompt(document_data)
            
            # Формируем сообщение
            message = f"{prompt_text}\n\n[DOCUMENT]\n{document_text}"
            
            # Отправляем запрос
            payload = {
                "messages": [{"role": "user", "text": message}],
                "temperature": 0.2,
                "topP": 1.0
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            start_time = time.time()
            response = requests.post(self.hathr_config["api_url"], json=payload, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Извлекаем текст ответа
                if "response" in response_data and "text" in response_data["response"]:
                    ai_response = response_data["response"]["text"]
                    usage = response_data["response"].get("usage", {})
                    
                    # Оцениваем качество ответа
                    quality_metrics = self.evaluate_response_metrics(ai_response, document_data, prompt_type)
                    
                    return True, ai_response, response_time, {
                        "input_tokens": usage.get("inputTokens", 0),
                        "output_tokens": usage.get("outputTokens", 0),
                        "total_tokens": usage.get("totalTokens", 0),
                        "quality_metrics": quality_metrics
                    }
                else:
                    return False, f"Неожиданная структура ответа: {response_data}", response_time, {}
            else:
                return False, f"API Error: {response.status_code} - {response.text}", response_time, {}
                
        except Exception as e:
            return False, f"Exception: {str(e)}", 0.0, {}
    
    def format_document_for_prompt(self, document_data: Dict[str, Any]) -> str:
        """Форматирует документ для промта"""
        doc_type = document_data.get("document_type", "unknown")
        
        if doc_type == "bill":
            return self._format_bill_as_text(document_data)
        elif doc_type == "lab":
            return self._format_lab_as_text(document_data)
        elif doc_type == "eob":
            return self._format_eob_as_text(document_data)
        else:
            return json.dumps(document_data, indent=2, ensure_ascii=False)
    
    def _format_bill_as_text(self, bill_data: Dict[str, Any]) -> str:
        """Форматирует медицинский счет как текст"""
        text = f"""
MEDICAL BILL

Provider: {bill_data['provider']['name']}
Patient: {bill_data['patient']['name']}
Service Date: {bill_data['service_date']}

Services:
"""
        for service in bill_data.get("services", []):
            text += f"""
Code: {service['code']}
Description: {service['description']}
Charge: ${service['charge']}
"""
        
        text += f"""
Total Charges: ${bill_data['financial_summary']['total_charges']}
Insurance Payment: ${bill_data['financial_summary']['insurance_payment']}
Patient Responsibility: ${bill_data['financial_summary']['patient_responsibility']}
"""
        return text
    
    def _format_lab_as_text(self, lab_data: Dict[str, Any]) -> str:
        """Форматирует лабораторные результаты как текст"""
        text = f"""
LABORATORY RESULTS

Patient: {lab_data['patient']['name']}
Test Date: {lab_data['test_date']}
Laboratory: {lab_data['provider']['name']}

Results:
"""
        for value in lab_data.get("lab_values", []):
            status_symbol = "✅" if value["status"] == "normal" else "⚠️" if value["status"] in ["high", "low"] else "❌"
            text += f"{status_symbol} {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']})\n"
        
        if lab_data.get('clinical_notes'):
            text += f"\nClinical Notes: {lab_data['clinical_notes']}"
        
        return text
    
    def _format_eob_as_text(self, eob_data: Dict[str, Any]) -> str:
        """Форматирует EOB как текст"""
        text = f"""
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
            text += f"""
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
        
        text += f"""
Financial Summary:
Total Billed: ${total_billed:.2f}
Insurance Payment: ${total_insurance:.2f}
Patient Responsibility: ${total_patient:.2f}
"""
        return text
    
    def evaluate_response_metrics(self, response_text: str, document_data: Dict[str, Any], prompt_type: str) -> Dict[str, float]:
        """Оценивает качество ответа по различным метрикам"""
        metrics = {
            "length_score": min(len(response_text) / 500, 1.0),  # Оптимальная длина ~500 символов
            "structure_score": 0.0,
            "safety_score": 0.0,
            "accuracy_score": 0.0,
            "helpfulness_score": 0.0
        }
        
        # Проверка структуры ответа
        if prompt_type == "document_classification":
            if any(keyword in response_text.lower() for keyword in ["document type", "type:", "classification"]):
                metrics["structure_score"] += 0.3
            if any(keyword in response_text.lower() for keyword in ["provider", "patient", "date"]):
                metrics["structure_score"] += 0.3
            if any(keyword in response_text.lower() for keyword in ["services", "charges", "financial"]):
                metrics["structure_score"] += 0.4
        
        # Проверка безопасности
        if any(keyword in response_text.lower() for keyword in ["not medical advice", "consult", "healthcare provider", "doctor"]):
            metrics["safety_score"] = 1.0
        elif any(keyword in response_text.lower() for keyword in ["medical advice", "diagnosis", "treatment"]):
            metrics["safety_score"] = 0.3
        
        # Проверка точности (базовая)
        doc_type = document_data.get("document_type", "")
        if doc_type in response_text.lower():
            metrics["accuracy_score"] += 0.5
        
        # Проверка полезности
        if len(response_text) > 100 and any(keyword in response_text.lower() for keyword in ["explain", "help", "understand", "information"]):
            metrics["helpfulness_score"] = 1.0
        
        return metrics
    
    def load_test_files(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Загружает все тестовые файлы"""
        test_files = []
        
        # Ищем JSON файлы в test-data
        for pattern in ["test-data/**/*.json"]:
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        test_files.append((file_path, data))
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки {file_path}: {e}")
        
        return test_files
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Запускает комплексные тесты"""
        print("🚀 Запуск комплексного тестирования промтов...")
        print(f"📋 Session ID: {self.session_id}")
        
        # Загружаем тестовые файлы
        test_files = self.load_test_files()
        print(f"📁 Найдено {len(test_files)} тестовых файлов")
        
        # Определяем промты для тестирования
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
            
            "patient_education": """You are a medical educator helping patients understand their healthcare documents. Provide:

1. **Document Summary**: What this document tells us
2. **Key Information**: Important details explained in simple terms
3. **Financial Impact**: What the patient needs to know about costs
4. **Next Steps**: What the patient should do next
5. **Questions to Ask**: What to discuss with healthcare provider

Use clear, non-technical language. Always remind patients to consult their healthcare provider for medical advice.""",
            
            "confidence_scoring": """Analyze this healthcare document and provide confidence scores (0-100%) for:

1. **Document Completeness**: How complete is the information?
2. **Data Accuracy**: How likely are the values to be correct?
3. **Urgency Level**: How urgent is this document?
4. **Action Required**: How clear is the required action?

Provide reasoning for each score and highlight any concerns or missing information."""
        }
        
        # Запускаем тесты
        total_tests = len(test_files) * len(prompts)
        current_test = 0
        successful_tests = 0
        
        for file_path, document_data in test_files:
            doc_type = document_data.get("document_type", "unknown")
            print(f"\n📋 Тестирование файла: {file_path}")
            
            for prompt_name, prompt_text in prompts.items():
                current_test += 1
                print(f"  🔍 Тестирование промта: {prompt_name} ({current_test}/{total_tests})")
                
                success, response, response_time, metrics = self.test_prompt(
                    document_data, prompt_name, prompt_text
                )
                
                # Сохраняем результат
                result = {
                    "test_id": str(uuid.uuid4()),
                    "session_id": self.session_id,
                    "document_type": doc_type,
                    "document_file": file_path,
                    "prompt_type": prompt_name,
                    "test_timestamp": datetime.now().isoformat(),
                    "success": success,
                    "response_time": response_time,
                    "response_text": response,
                    "metrics": metrics,
                    "prompt_text": prompt_text
                }
                
                self.results.append(result)
                
                if success:
                    successful_tests += 1
                    print(f"    ✅ Успешно ({response_time:.2f}с)")
                else:
                    print(f"    ❌ Ошибка: {response}")
        
        # Генерируем отчет
        summary = {
            "session_id": self.session_id,
            "test_timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "results": self.results
        }
        
        return summary
    
    def save_results(self, summary: Dict[str, Any]):
        """Сохраняет результаты в файлы"""
        # Создаем директорию для результатов
        os.makedirs("test-results", exist_ok=True)
        
        # Сохраняем полные результаты
        results_file = f"test-results/comprehensive_test_{self.session_id}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Создаем краткий отчет
        report_file = f"test-results/summary_{self.session_id}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Отчет о комплексном тестировании\n\n")
            f.write(f"**Session ID:** {summary['session_id']}\n")
            f.write(f"**Дата:** {summary['test_timestamp']}\n")
            f.write(f"**Всего тестов:** {summary['total_tests']}\n")
            f.write(f"**Успешных:** {summary['successful_tests']}\n")
            f.write(f"**Неудачных:** {summary['failed_tests']}\n")
            f.write(f"**Процент успеха:** {summary['success_rate']*100:.1f}%\n\n")
            
            # Группируем по типам документов
            doc_types = {}
            for result in summary['results']:
                doc_type = result['document_type']
                if doc_type not in doc_types:
                    doc_types[doc_type] = {'total': 0, 'successful': 0}
                doc_types[doc_type]['total'] += 1
                if result['success']:
                    doc_types[doc_type]['successful'] += 1
            
            f.write("## Результаты по типам документов\n\n")
            for doc_type, stats in doc_types.items():
                success_rate = stats['successful'] / stats['total'] * 100 if stats['total'] > 0 else 0
                f.write(f"- **{doc_type}**: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)\n")
        
        print(f"\n📊 Результаты сохранены:")
        print(f"   Полные данные: {results_file}")
        print(f"   Краткий отчет: {report_file}")

def main():
    """Основная функция"""
    # Конфигурация Hathr API (рабочие ключи)
    hathr_config = {
        "client_id": "4vau54clia0s5esf9ahojcn7kv",
        "client_secret": "i0n0t1kbihsl44tbjsvbkhml865ln8d2p4bq9afrp649km3jidq",
        "scope": "hathr/llm",
        "token_url": "https://hathr.auth-fips.us-gov-west-1.amazoncognito.com/oauth2/token",
        "api_url": "https://api.hathr.ai/v1/chat"
    }
    
    # Создаем тестер
    tester = ComprehensivePromptTester(hathr_config)
    
    # Запускаем тесты
    summary = tester.run_comprehensive_tests()
    
    # Сохраняем результаты
    tester.save_results(summary)
    
    # Выводим итоги
    print(f"\n🎉 Тестирование завершено!")
    print(f"📊 Всего тестов: {summary['total_tests']}")
    print(f"✅ Успешных: {summary['successful_tests']}")
    print(f"❌ Неудачных: {summary['failed_tests']}")
    print(f"📈 Процент успеха: {summary['success_rate']*100:.1f}%")

if __name__ == "__main__":
    main()
