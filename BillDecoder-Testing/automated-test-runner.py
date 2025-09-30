#!/usr/bin/env python3
"""
Автоматизированный тестер промтов для BillDecoder/LabDecoder
Использует сгенерированные тестовые данные для проверки всех промтов
"""

import json
import os
import time
import requests
import subprocess
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class TestResult:
    """Результат тестирования промта"""
    test_id: str
    prompt_type: str
    document_type: str
    complexity: str
    timestamp: str
    response_time: float
    success: bool
    error_message: str = None
    raw_response: str = None
    confidence_score: float = None
    accuracy_score: float = None
    clarity_score: float = None
    issues_found: List[str] = None
    metrics: Dict[str, Any] = None

class PromptTester:
    """Тестер промтов для BillDecoder/LabDecoder"""
    
    def __init__(self, hathr_config: Dict[str, str]):
        self.hathr_config = hathr_config
        self.test_results: List[TestResult] = []
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, str]:
        """Загружает все промты для тестирования"""
        return {
            "primary_bill_analysis": """You are a medical billing expert helping patients understand their healthcare bills. Analyze the uploaded medical bill/EOB and provide:

1. **Plain English Summary**: Translate all medical codes and terminology into simple language
2. **Financial Breakdown**: Clearly explain what patient owes vs. what insurance covered
3. **Billing Error Detection**: Flag potential overcharges, duplicate charges, or coding errors
4. **Action Items**: Specific next steps for the patient
5. **Cost Comparison**: If possible, note if charges seem unusually high for the services

Format your response with clear sections and use ✅ for normal items, ⚠️ for concerns, and ❌ for definite errors.""",

            "appeal_letter_generation": """Generate a professional insurance appeal letter based on this billing dispute:

**Dispute Details**: [USER INPUT]
**Patient Info**: [NAME/POLICY NUMBER - REDACTED FOR PRIVACY]
**Service Details**: [FROM BILL ANALYSIS]

Create a formal letter that:
- References specific policy provisions
- Cites medical necessity when appropriate
- Includes relevant billing codes and dates
- Maintains professional tone
- Requests specific action and timeline

Format as a ready-to-send business letter.""",

            "bill_error_investigation": """Acting as a medical billing auditor, examine this bill for potential errors:

Focus on:
- Duplicate charges or services
- Upcoding (charging for more complex service than provided)
- Unbundling (separately billing components that should be bundled)
- Non-covered services billed as covered
- Mathematical errors in calculations
- Timeline inconsistencies

Provide confidence scores (1-10) for each potential error identified.""",

            "lab_results_explanation": """You are a medical educator helping patients understand their lab results. Analyze these lab values and provide:

1. **Results Summary**: Overall health picture in simple terms
2. **Individual Test Explanations**: What each test measures and why it matters
3. **Abnormal Values**: Clear explanation of any concerning results
4. **Trend Analysis**: If multiple dates available, show changes over time
5. **Next Steps**: What patient should discuss with their doctor
6. **Educational Content**: Brief background on relevant health conditions

Use analogies and everyday language. Avoid medical jargon. Always remind patients to consult their healthcare provider for medical advice.""",

            "trend_analysis": """Analyze this series of lab results over time:

**Time Period**: [DATE RANGE]
**Tests Included**: [TEST NAMES]

Create a health trends report showing:
- Improving, stable, or declining patterns
- Clinically significant changes
- Correlation between different test values
- Visual trend descriptions (since graphs aren't available)
- Risk factor progression

Focus on empowering the patient with knowledge while emphasizing the need for professional medical interpretation.""",

            "abnormal_results_focus": """The following lab values are outside normal ranges. Provide patient-friendly explanations:

For each abnormal value:
1. **What it means**: Simple explanation of the test
2. **Why it might be abnormal**: Common causes
3. **Potential implications**: What this could indicate
4. **Urgency level**: How quickly to follow up
5. **Questions for doctor**: Specific questions to ask

Maintain a calm, informative tone. Avoid causing unnecessary anxiety while ensuring patients understand the importance of follow-up.""",

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

Provide specific recommendations for when users should seek additional professional help.""",

            "privacy_protection": """Review this response for any potential privacy concerns:

Check for:
- Inadvertent inclusion of personal identifiers
- Overly specific medical details that could identify patient
- References to specific providers that should be generalized
- Compliance with healthcare privacy best practices"""
        }
    
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
    
    def call_hathr_api(self, prompt: str, document_data: str = None) -> Tuple[bool, str, float]:
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
                return True, response.json()["data"]["message"], response_time
            else:
                return False, f"API Error: {response.status_code} - {response.text}", response_time
                
        except Exception as e:
            return False, f"Exception: {str(e)}", 0.0
    
    def analyze_response_quality(self, response: str, document_type: str) -> Dict[str, Any]:
        """Анализирует качество ответа"""
        metrics = {
            "has_plain_english": False,
            "has_financial_breakdown": False,
            "has_error_detection": False,
            "has_action_items": False,
            "uses_formatting": False,
            "has_disclaimers": False,
            "confidence_mentioned": False,
            "medical_advice_avoided": True,
            "hipaa_compliant": True
        }
        
        response_lower = response.lower()
        
        # Check for key elements
        if "plain english" in response_lower or "simple language" in response_lower:
            metrics["has_plain_english"] = True
        
        if "financial" in response_lower or "cost" in response_lower or "payment" in response_lower or "charge" in response_lower:
            metrics["has_financial_breakdown"] = True
        
        if "error" in response_lower or "❌" in response:
            metrics["has_error_detection"] = True
        
        if "action" in response_lower or "next step" in response_lower or "recommend" in response_lower:
            metrics["has_action_items"] = True
        
        if "✅" in response or "⚠️" in response or "❌" in response:
            metrics["uses_formatting"] = True
        
        if "disclaimer" in response_lower or "not medical advice" in response_lower:
            metrics["has_disclaimers"] = True
        
        if "confidence" in response_lower:
            metrics["confidence_mentioned"] = True
        
        # Check for medical advice
        medical_advice_indicators = [
            "you should take",
            "prescribe",
            "diagnosis",
            "you need to"
        ]
        
        for indicator in medical_advice_indicators:
            if indicator in response_lower:
                metrics["medical_advice_avoided"] = False
                break
        
        # Check for potential data leaks
        privacy_indicators = [
            "ssn", "social security",
            "phone number",
            "address"
        ]
        
        for indicator in privacy_indicators:
            if indicator in response_lower:
                metrics["hipaa_compliant"] = False
                break
        
        return metrics
    
    def calculate_scores(self, response: str, metrics: Dict[str, Any]) -> Tuple[float, float, float]:
        """Вычисляет оценки качества ответа"""
        # Оценка точности (0-10)
        accuracy_score = 0.0
        if metrics["has_plain_english"]:
            accuracy_score += 2.0
        if metrics["has_financial_breakdown"]:
            accuracy_score += 2.0
        if metrics["has_error_detection"]:
            accuracy_score += 2.0
        if metrics["has_action_items"]:
            accuracy_score += 2.0
        if metrics["uses_formatting"]:
            accuracy_score += 1.0
        if metrics["confidence_mentioned"]:
            accuracy_score += 1.0
        
        # Оценка ясности (0-10)
        clarity_score = 0.0
        if metrics["has_plain_english"]:
            clarity_score += 3.0
        if metrics["uses_formatting"]:
            clarity_score += 2.0
        if metrics["has_disclaimers"]:
            clarity_score += 2.0
        if len(response) > 200:  # Достаточно подробный ответ
            clarity_score += 2.0
        if "consult" in response.lower() or "консультация" in response.lower():
            clarity_score += 1.0
        
        # Оценка уверенности (0-10)
        confidence_score = 5.0  # Базовая оценка
        if metrics["medical_advice_avoided"]:
            confidence_score += 2.0
        if metrics["hipaa_compliant"]:
            confidence_score += 2.0
        if metrics["confidence_mentioned"]:
            confidence_score += 1.0
        
        return accuracy_score, clarity_score, confidence_score
    
    def test_prompt(self, prompt_name: str, document_data: Dict[str, Any]) -> TestResult:
        """Тестирует конкретный промт на документе"""
        test_id = f"{prompt_name}_{document_data['document_type']}_{int(time.time())}"
        
        # Определяем сложность документа
        complexity = "simple"
        if document_data["document_type"] == "medical_bill":
            if len(document_data.get("services", [])) > 3:
                complexity = "complex"
            elif len(document_data.get("services", [])) > 1:
                complexity = "medium"
        elif document_data["document_type"] == "lab_results":
            if len(document_data.get("lab_values", [])) > 8:
                complexity = "complex"
            elif len(document_data.get("lab_values", [])) > 4:
                complexity = "medium"
        
        # Формируем данные документа для промта
        document_text = self._format_document_for_prompt(document_data)
        
        # Вызываем API
        success, response, response_time = self.call_hathr_api(
            self.prompts[prompt_name], 
            document_text
        )
        
        # Анализируем результат
        if success:
            metrics = self.analyze_response_quality(response, document_data["document_type"])
            accuracy_score, clarity_score, confidence_score = self.calculate_scores(response, metrics)
            
            # Извлекаем найденные проблемы
            issues_found = []
            if "❌" in response:
                issues_found.append("definite_errors")
            if "⚠️" in response:
                issues_found.append("concerns")
            if "duplicate" in response.lower() or "дублир" in response.lower():
                issues_found.append("duplicate_charges")
            if "overcharge" in response.lower() or "завышен" in response.lower():
                issues_found.append("overcharges")
            
            return TestResult(
                test_id=test_id,
                prompt_type=prompt_name,
                document_type=document_data["document_type"],
                complexity=complexity,
                timestamp=datetime.now().isoformat(),
                response_time=response_time,
                success=True,
                raw_response=response,
                confidence_score=confidence_score,
                accuracy_score=accuracy_score,
                clarity_score=clarity_score,
                issues_found=issues_found,
                metrics=metrics
            )
        else:
            return TestResult(
                test_id=test_id,
                prompt_type=prompt_name,
                document_type=document_data["document_type"],
                complexity=complexity,
                timestamp=datetime.now().isoformat(),
                response_time=response_time,
                success=False,
                error_message=response
            )
    
    def _format_document_for_prompt(self, document_data: Dict[str, Any]) -> str:
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
    
    def run_comprehensive_tests(self, test_data_dir: str = "test-data") -> None:
        """Runs comprehensive testing of all prompts"""
        print("🚀 Starting comprehensive prompt testing...")
        
        # Define which prompts to test for which document types
        test_matrix = {
            "medical_bill": [
                "primary_bill_analysis",
                "bill_error_investigation", 
                "document_classification",
                "confidence_scoring"
            ],
            "lab_results": [
                "lab_results_explanation",
                "trend_analysis",
                "abnormal_results_focus",
                "document_classification",
                "confidence_scoring"
            ],
            "eob": [
                "primary_bill_analysis",
                "document_classification",
                "confidence_scoring"
            ]
        }
        
        # Load test data
        test_files = self._load_test_files(test_data_dir)
        
        total_tests = 0
        for doc_type, files in test_files.items():
            for file_path in files[:3]:  # Test 3 files of each type
                for prompt_name in test_matrix.get(doc_type, []):
                    print(f"📋 Testing: {prompt_name} on {doc_type} ({file_path})")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        document_data = json.load(f)
                    
                    result = self.test_prompt(prompt_name, document_data)
                    self.test_results.append(result)
                    total_tests += 1
                    
                    if result.success:
                        print(f"   ✅ Success - Time: {result.response_time:.2f}s, Accuracy: {result.accuracy_score:.1f}/10")
                    else:
                        print(f"   ❌ Error: {result.error_message}")
                    
                    # Small pause between requests
                    time.sleep(1)
        
        print(f"\n📊 Testing completed! Total tests: {total_tests}")
    
    def _load_test_files(self, test_data_dir: str) -> Dict[str, List[str]]:
        """Loads paths to test files"""
        test_files = {
            "medical_bill": [],
            "lab_results": [],
            "eob": []
        }
        
        for root, dirs, files in os.walk(test_data_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    
                    # Determine document type by path
                    if 'bills' in file_path:
                        test_files["medical_bill"].append(file_path)
                    elif 'lab-results' in file_path:
                        test_files["lab_results"].append(file_path)
                    elif 'eob' in file_path:
                        test_files["eob"].append(file_path)
        
        return test_files
    
    def generate_report(self, output_file: str = "test-results/report.json") -> None:
        """Generates testing report"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Prepare data for report
        report_data = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if r.success]),
                "failed_tests": len([r for r in self.test_results if not r.success]),
                "test_date": datetime.now().isoformat()
            },
            "performance_metrics": self._calculate_performance_metrics(),
            "quality_metrics": self._calculate_quality_metrics(),
            "detailed_results": [
                {
                    "test_id": r.test_id,
                    "prompt_type": r.prompt_type,
                    "document_type": r.document_type,
                    "complexity": r.complexity,
                    "success": r.success,
                    "response_time": r.response_time,
                    "accuracy_score": r.accuracy_score,
                    "clarity_score": r.clarity_score,
                    "confidence_score": r.confidence_score,
                    "issues_found": r.issues_found,
                    "error_message": r.error_message
                }
                for r in self.test_results
            ]
        }
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # Generate text report
        self._generate_text_report(report_data, output_file.replace('.json', '.txt'))
        
        print(f"📄 Report saved: {output_file}")
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculates performance metrics"""
        successful_results = [r for r in self.test_results if r.success]
        
        if not successful_results:
            return {"error": "No successful tests"}
        
        response_times = [r.response_time for r in successful_results]
        
        return {
            "average_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "success_rate": len(successful_results) / len(self.test_results) * 100
        }
    
    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculates quality metrics"""
        successful_results = [r for r in self.test_results if r.success and r.accuracy_score is not None]
        
        if not successful_results:
            return {"error": "No successful tests with scores"}
        
        accuracy_scores = [r.accuracy_score for r in successful_results]
        clarity_scores = [r.clarity_score for r in successful_results]
        confidence_scores = [r.confidence_score for r in successful_results]
        
        return {
            "accuracy": {
                "average": statistics.mean(accuracy_scores),
                "median": statistics.median(accuracy_scores),
                "min": min(accuracy_scores),
                "max": max(accuracy_scores)
            },
            "clarity": {
                "average": statistics.mean(clarity_scores),
                "median": statistics.median(clarity_scores),
                "min": min(clarity_scores),
                "max": max(clarity_scores)
            },
            "confidence": {
                "average": statistics.mean(confidence_scores),
                "median": statistics.median(confidence_scores),
                "min": min(confidence_scores),
                "max": max(confidence_scores)
            }
        }
    
    def _generate_text_report(self, report_data: Dict[str, Any], output_file: str) -> None:
        """Generates text report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("BILLDECODER/LABDECODER PROMPT TESTING REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            # Summary
            summary = report_data["test_summary"]
            f.write(f"TESTING SUMMARY:\n")
            f.write(f"Date: {summary['test_date']}\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Successful: {summary['successful_tests']}\n")
            f.write(f"Failed: {summary['failed_tests']}\n")
            f.write(f"Success Rate: {summary['successful_tests']/summary['total_tests']*100:.1f}%\n\n")
            
            # Performance
            perf = report_data["performance_metrics"]
            if "error" not in perf:
                f.write(f"PERFORMANCE METRICS:\n")
                f.write(f"Average Response Time: {perf['average_response_time']:.2f} sec\n")
                f.write(f"Median Response Time: {perf['median_response_time']:.2f} sec\n")
                f.write(f"Min Response Time: {perf['min_response_time']:.2f} sec\n")
                f.write(f"Max Response Time: {perf['max_response_time']:.2f} sec\n\n")
            
            # Quality
            quality = report_data["quality_metrics"]
            if "error" not in quality:
                f.write(f"QUALITY METRICS:\n")
                f.write(f"Accuracy - Average: {quality['accuracy']['average']:.1f}/10\n")
                f.write(f"Clarity - Average: {quality['clarity']['average']:.1f}/10\n")
                f.write(f"Confidence - Average: {quality['confidence']['average']:.1f}/10\n\n")
            
            # Detailed results
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 60 + "\n")
            
            for result in report_data["detailed_results"]:
                f.write(f"Test: {result['test_id']}\n")
                f.write(f"Prompt: {result['prompt_type']}\n")
                f.write(f"Document: {result['document_type']} ({result['complexity']})\n")
                f.write(f"Status: {'✅ Success' if result['success'] else '❌ Error'}\n")
                
                if result['success']:
                    f.write(f"Response Time: {result['response_time']:.2f} sec\n")
                    f.write(f"Accuracy Score: {result['accuracy_score']:.1f}/10\n")
                    f.write(f"Clarity Score: {result['clarity_score']:.1f}/10\n")
                    f.write(f"Confidence Score: {result['confidence_score']:.1f}/10\n")
                    if result['issues_found']:
                        f.write(f"Issues Found: {', '.join(result['issues_found'])}\n")
                else:
                    f.write(f"Error: {result['error_message']}\n")
                
                f.write("\n")


def main():
    """Main function for running tests"""
    # Hathr API configuration (from existing scripts)
    hathr_config = {
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here",
        "scope": "hathr/llm",
        "token_url": "https://hathr.auth-fips.us-gov-west-1.amazoncognito.com/oauth2/token",
        "api_url": "https://api.hathr.ai/v1/chat"
    }
    
    # Create tester
    tester = PromptTester(hathr_config)
    
    # Check for test data
    if not os.path.exists("test-data"):
        print("❌ test-data directory not found!")
        print("Run test-data-generator.py first to create test data")
        return
    
    # Run testing
    try:
        tester.run_comprehensive_tests()
        tester.generate_report()
        
        print("\n🎉 Testing completed successfully!")
        print("📊 Check test-results/ directory for detailed reports")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")


if __name__ == "__main__":
    main()
