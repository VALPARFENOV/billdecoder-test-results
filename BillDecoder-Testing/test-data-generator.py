#!/usr/bin/env python3
"""
Генератор тестовых данных для BillDecoder/LabDecoder
Создает различные типы медицинских документов для тестирования промтов
"""

import json
import random
import datetime
from typing import Dict, List, Any
import os
from dataclasses import dataclass
from faker import Faker

fake = Faker('en_US')

@dataclass
class MedicalCode:
    """Медицинский код с описанием"""
    code: str
    description: str
    category: str

@dataclass
class LabValue:
    """Лабораторное значение"""
    test_name: str
    value: float
    unit: str
    reference_range: str
    status: str  # normal, high, low, critical

class TestDataGenerator:
    """Генератор тестовых данных для медицинских документов"""
    
    def __init__(self):
        self.medical_codes = self._load_medical_codes()
        self.lab_tests = self._load_lab_tests()
        self.providers = self._generate_providers()
        self.insurance_companies = self._generate_insurance_companies()
    
    def _load_medical_codes(self) -> List[MedicalCode]:
        """Loads medical codes for testing"""
        return [
            # CPT codes
            MedicalCode("99213", "Office visit, expanded problem focused", "CPT"),
            MedicalCode("99214", "Office visit, detailed", "CPT"),
            MedicalCode("36415", "Venipuncture", "CPT"),
            MedicalCode("80053", "Comprehensive metabolic panel", "CPT"),
            MedicalCode("85025", "Complete blood count with differential", "CPT"),
            MedicalCode("93000", "Electrocardiogram", "CPT"),
            MedicalCode("99281", "Emergency department visit, level 1", "CPT"),
            MedicalCode("99282", "Emergency department visit, level 2", "CPT"),
            MedicalCode("99283", "Emergency department visit, level 3", "CPT"),
            MedicalCode("99284", "Emergency department visit, level 4", "CPT"),
            MedicalCode("99285", "Emergency department visit, level 5", "CPT"),
            
            # ICD-10 codes
            MedicalCode("Z00.00", "General adult medical examination", "ICD-10"),
            MedicalCode("I10", "Essential hypertension", "ICD-10"),
            MedicalCode("E11.9", "Type 2 diabetes mellitus without complications", "ICD-10"),
            MedicalCode("M79.3", "Panniculitis, unspecified", "ICD-10"),
            MedicalCode("R50.9", "Fever, unspecified", "ICD-10"),
            MedicalCode("K21.9", "Gastro-esophageal reflux disease without esophagitis", "ICD-10"),
            
            # HCPCS codes
            MedicalCode("A4253", "Blood glucose test strips", "HCPCS"),
            MedicalCode("J1815", "Injection, insulin, per 5 units", "HCPCS"),
            MedicalCode("G0008", "Administration of influenza virus vaccine", "HCPCS"),
        ]
    
    def _load_lab_tests(self) -> List[Dict[str, Any]]:
        """Loads laboratory test data"""
        return [
            {
                "name": "Glucose",
                "unit": "mg/dL",
                "normal_range": "70-100",
                "category": "metabolic"
            },
            {
                "name": "Total Cholesterol",
                "unit": "mg/dL",
                "normal_range": "<200",
                "category": "lipid"
            },
            {
                "name": "HDL Cholesterol",
                "unit": "mg/dL",
                "normal_range": ">40",
                "category": "lipid"
            },
            {
                "name": "LDL Cholesterol",
                "unit": "mg/dL",
                "normal_range": "<100",
                "category": "lipid"
            },
            {
                "name": "Triglycerides",
                "unit": "mg/dL",
                "normal_range": "<150",
                "category": "lipid"
            },
            {
                "name": "Hemoglobin",
                "unit": "g/dL",
                "normal_range": "12.0-15.5",
                "category": "CBC"
            },
            {
                "name": "Hematocrit",
                "unit": "%",
                "normal_range": "36-46",
                "category": "CBC"
            },
            {
                "name": "White Blood Cells",
                "unit": "K/uL",
                "normal_range": "4.5-11.0",
                "category": "CBC"
            },
            {
                "name": "Platelets",
                "unit": "K/uL",
                "normal_range": "150-450",
                "category": "CBC"
            },
            {
                "name": "Creatinine",
                "unit": "mg/dL",
                "normal_range": "0.6-1.2",
                "category": "renal"
            },
            {
                "name": "ALT",
                "unit": "U/L",
                "normal_range": "7-56",
                "category": "liver"
            },
            {
                "name": "AST",
                "unit": "U/L",
                "normal_range": "10-40",
                "category": "liver"
            },
            {
                "name": "TSH",
                "unit": "mIU/L",
                "normal_range": "0.4-4.0",
                "category": "thyroid"
            },
            {
                "name": "Free T4",
                "unit": "ng/dL",
                "normal_range": "0.8-1.8",
                "category": "thyroid"
            }
        ]
    
    def _generate_providers(self) -> List[Dict[str, str]]:
        """Generates list of medical providers"""
        return [
            {"name": "HealthCare Medical Center", "npi": "1234567890", "specialty": "Internal Medicine"},
            {"name": "CardioPlus Clinic", "npi": "2345678901", "specialty": "Cardiology"},
            {"name": "LabCorp Diagnostics", "npi": "3456789012", "specialty": "Laboratory Services"},
            {"name": "City General Hospital", "npi": "4567890123", "specialty": "Emergency Medicine"},
            {"name": "Endocrine Care Center", "npi": "5678901234", "specialty": "Endocrinology"},
            {"name": "Family Practice Associates", "npi": "6789012345", "specialty": "Family Medicine"},
            {"name": "Metro Urgent Care", "npi": "7890123456", "specialty": "Urgent Care"},
            {"name": "Regional Medical Group", "npi": "8901234567", "specialty": "Primary Care"},
        ]
    
    def _generate_insurance_companies(self) -> List[Dict[str, str]]:
        """Generates list of insurance companies"""
        return [
            {"name": "Blue Cross Blue Shield", "code": "BCBS"},
            {"name": "Aetna", "code": "AET"},
            {"name": "Cigna", "code": "CIG"},
            {"name": "UnitedHealthcare", "code": "UHC"},
            {"name": "Humana", "code": "HUM"},
            {"name": "Kaiser Permanente", "code": "KP"},
            {"name": "Anthem", "code": "ANT"},
            {"name": "Medicare", "code": "MED"},
        ]
    
    def generate_medical_bill(self, complexity: str = "simple", include_errors: bool = False) -> Dict[str, Any]:
        """Генерирует медицинский счет"""
        provider = random.choice(self.providers)
        insurance = random.choice(self.insurance_companies)
        service_date = fake.date_between(start_date='-30d', end_date='today')
        
        # Генерируем услуги в зависимости от сложности
        if complexity == "simple":
            services = self._generate_simple_services()
        elif complexity == "medium":
            services = self._generate_medium_services()
        else:  # complex
            services = self._generate_complex_services()
        
        # Добавляем ошибки если нужно
        if include_errors:
            services = self._add_billing_errors(services)
        
        total_charges = sum(service['charge'] for service in services)
        insurance_payment = total_charges * random.uniform(0.6, 0.9)
        patient_responsibility = total_charges - insurance_payment
        
        bill = {
            "document_type": "medical_bill",
            "provider": provider,
            "patient": {
                "name": fake.name(),
                "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
                "member_id": fake.bothify(text='???#######'),
                "address": fake.address()
            },
            "insurance": {
                "company": insurance,
                "policy_number": fake.bothify(text='POL#######'),
                "group_number": fake.bothify(text='GRP#####')
            },
            "service_date": service_date.strftime('%Y-%m-%d'),
            "billing_date": fake.date_between(start_date=service_date, end_date='today').strftime('%Y-%m-%d'),
            "services": services,
            "financial_summary": {
                "total_charges": round(total_charges, 2),
                "insurance_payment": round(insurance_payment, 2),
                "patient_responsibility": round(patient_responsibility, 2),
                "deductible": round(random.uniform(0, 500), 2),
                "copay": round(random.uniform(0, 50), 2)
            },
            "billing_codes": {
                "diagnosis_codes": [random.choice(self.medical_codes).code for _ in range(random.randint(1, 3))],
                "procedure_codes": [service['code'] for service in services]
            }
        }
        
        return bill
    
    def _generate_simple_services(self) -> List[Dict[str, Any]]:
        """Generates simple medical services"""
        services = []
        base_services = [
            {"code": "99213", "description": "Office visit", "base_charge": 150},
            {"code": "36415", "description": "Venipuncture", "base_charge": 25},
            {"code": "80053", "description": "Basic metabolic panel", "base_charge": 80}
        ]
        
        for service in random.sample(base_services, random.randint(1, 2)):
            services.append({
                "code": service["code"],
                "description": service["description"],
                "charge": round(service["base_charge"] * random.uniform(0.8, 1.2), 2),
                "quantity": 1,
                "date": fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
            })
        
        return services
    
    def _generate_medium_services(self) -> List[Dict[str, Any]]:
        """Generates medium complexity medical services"""
        services = self._generate_simple_services()
        
        additional_services = [
            {"code": "93000", "description": "Electrocardiogram", "base_charge": 45},
            {"code": "99214", "description": "Detailed office visit", "base_charge": 200},
            {"code": "85025", "description": "Complete blood count", "base_charge": 60}
        ]
        
        for service in random.sample(additional_services, random.randint(1, 2)):
            services.append({
                "code": service["code"],
                "description": service["description"],
                "charge": round(service["base_charge"] * random.uniform(0.8, 1.2), 2),
                "quantity": 1,
                "date": fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
            })
        
        return services
    
    def _generate_complex_services(self) -> List[Dict[str, Any]]:
        """Generates complex medical services"""
        services = self._generate_medium_services()
        
        complex_services = [
            {"code": "99284", "description": "Emergency department visit, level 4", "base_charge": 800},
            {"code": "99285", "description": "Emergency department visit, level 5", "base_charge": 1200},
            {"code": "36415", "description": "Additional venipuncture", "base_charge": 25},
            {"code": "80053", "description": "Comprehensive metabolic panel", "base_charge": 120}
        ]
        
        for service in random.sample(complex_services, random.randint(2, 4)):
            services.append({
                "code": service["code"],
                "description": service["description"],
                "charge": round(service["base_charge"] * random.uniform(0.8, 1.2), 2),
                "quantity": random.randint(1, 3),
                "date": fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
            })
        
        return services
    
    def _add_billing_errors(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Добавляет ошибки в медицинский счет"""
        error_types = [
            "duplicate_charge",
            "upcoding",
            "mathematical_error",
            "wrong_date",
            "unbundling"
        ]
        
        error_type = random.choice(error_types)
        
        if error_type == "duplicate_charge":
            # Дублируем случайную услугу
            duplicate_service = random.choice(services).copy()
            duplicate_service["charge"] = duplicate_service["charge"] * 1.1  # Небольшое изменение
            services.append(duplicate_service)
        
        elif error_type == "upcoding":
            # Заменяем простой код на более сложный
            simple_codes = ["99213", "36415"]
            complex_codes = ["99214", "99284"]
            for service in services:
                if service["code"] in simple_codes:
                    service["code"] = random.choice(complex_codes)
                    service["charge"] *= 1.5
        
        elif error_type == "mathematical_error":
            # Добавляем математическую ошибку
            for service in services:
                if random.random() < 0.3:
                    service["charge"] *= random.uniform(1.1, 1.3)
        
        elif error_type == "wrong_date":
            # Меняем дату на неправильную
            for service in services:
                if random.random() < 0.5:
                    service["date"] = fake.date_between(start_date='-60d', end_date='-31d').strftime('%Y-%m-%d')
        
        elif error_type == "unbundling":
            # Split services that should be bundled
            new_services = []
            for service in services:
                if service["code"] == "80053":  # Comprehensive metabolic panel
                    # Split into separate components
                    components = [
                        {"code": "80048", "description": "Basic metabolic panel", "charge": service["charge"] * 0.6},
                        {"code": "80051", "description": "Electrolytes", "charge": service["charge"] * 0.4}
                    ]
                    new_services.extend(components)
                else:
                    new_services.append(service)
            services = new_services
        
        return services
    
    def generate_lab_results(self, complexity: str = "normal", include_abnormal: bool = False) -> Dict[str, Any]:
        """Генерирует результаты лабораторных анализов"""
        lab_provider = random.choice([p for p in self.providers if "Lab" in p["name"] or "Diagnostics" in p["name"]])
        test_date = fake.date_between(start_date='-30d', end_date='today')
        
        # Select tests based on complexity
        if complexity == "basic":
            test_categories = ["metabolic", "CBC"]
        elif complexity == "comprehensive":
            test_categories = ["metabolic", "lipid", "CBC", "renal"]
        else:  # full
            test_categories = ["metabolic", "lipid", "CBC", "renal", "liver", "thyroid"]
        
        selected_tests = [test for test in self.lab_tests if test["category"] in test_categories]
        
        lab_values = []
        for test in selected_tests:
            value = self._generate_lab_value(test, include_abnormal)
            lab_values.append({
                "test_name": value.test_name,
                "value": value.value,
                "unit": value.unit,
                "reference_range": value.reference_range,
                "status": value.status
            })
        
        # Добавляем трендовые данные если нужно
        trend_data = []
        if complexity in ["comprehensive", "full"] and random.random() < 0.7:
            trend_data = self._generate_trend_data(selected_tests, test_date)
        
        lab_results = {
            "document_type": "lab_results",
            "provider": lab_provider,
            "patient": {
                "name": fake.name(),
                "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
                "member_id": fake.bothify(text='???#######'),
                "gender": random.choice(["M", "F"])
            },
            "test_date": test_date.strftime('%Y-%m-%d'),
            "report_date": fake.date_between(start_date=test_date, end_date='today').strftime('%Y-%m-%d'),
            "lab_values": lab_values,
            "trend_data": trend_data,
            "ordering_physician": {
                "name": fake.name(),
                "npi": fake.bothify(text='##########'),
                "specialty": random.choice(["Internal Medicine", "Cardiology", "Endocrinology", "Family Medicine"])
            },
            "clinical_notes": self._generate_clinical_notes(lab_values)
        }
        
        return lab_results
    
    def _generate_lab_value(self, test: Dict[str, Any], include_abnormal: bool = False) -> LabValue:
        """Генерирует значение лабораторного теста"""
        normal_range = test["normal_range"]
        
        # Парсим нормальный диапазон
        if "<" in normal_range:
            max_value = float(normal_range.replace("<", ""))
            normal_value = random.uniform(max_value * 0.3, max_value * 0.9)
        elif ">" in normal_range:
            min_value = float(normal_range.replace(">", ""))
            normal_value = random.uniform(min_value * 1.1, min_value * 1.5)
        else:
            # Диапазон вида "70-100"
            min_val, max_val = map(float, normal_range.split("-"))
            normal_value = random.uniform(min_val, max_val)
        
        # Определяем статус
        if include_abnormal and random.random() < 0.3:
            # Генерируем аномальное значение
            if random.random() < 0.5:
                # Высокое значение
                abnormal_value = normal_value * random.uniform(1.5, 3.0)
                status = "high"
            else:
                # Низкое значение
                abnormal_value = normal_value * random.uniform(0.3, 0.7)
                status = "low"
            
            # Проверяем на критические значения
            if abnormal_value > normal_value * 2.5 or abnormal_value < normal_value * 0.5:
                status = "critical"
            
            value = abnormal_value
        else:
            value = normal_value
            status = "normal"
        
        return LabValue(
            test_name=test["name"],
            value=round(value, 2),
            unit=test["unit"],
            reference_range=normal_range,
            status=status
        )
    
    def _generate_trend_data(self, tests: List[Dict[str, Any]], current_date: datetime.date) -> List[Dict[str, Any]]:
        """Генерирует трендовые данные за несколько месяцев"""
        trend_data = []
        
        for months_ago in [3, 6, 9, 12]:
            trend_date = current_date - datetime.timedelta(days=months_ago * 30)
            
            trend_values = []
            for test in random.sample(tests, random.randint(3, len(tests))):
                value = self._generate_lab_value(test, include_abnormal=False)
                trend_values.append({
                    "test_name": value.test_name,
                    "value": value.value,
                    "unit": value.unit,
                    "reference_range": value.reference_range,
                    "status": value.status
                })
            
            trend_data.append({
                "date": trend_date.strftime('%Y-%m-%d'),
                "values": trend_values
            })
        
        return trend_data
    
    def _generate_clinical_notes(self, lab_values: List[Dict[str, Any]]) -> str:
        """Generates clinical notes based on results"""
        abnormal_values = [v for v in lab_values if v["status"] != "normal"]
        
        if not abnormal_values:
            return "All laboratory values are within normal limits. Continue current treatment as prescribed."
        
        notes = []
        for value in abnormal_values:
            if value["status"] == "critical":
                notes.append(f"CRITICAL value for {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']}). Immediate attention required.")
            elif value["status"] == "high":
                notes.append(f"Elevated {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']}).")
            else:
                notes.append(f"Low {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']}).")
        
        return " ".join(notes) + " Recommend consultation with primary care physician."
    
    def generate_eob(self, bill: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует EOB (Explanation of Benefits) на основе счета"""
        eob = {
            "document_type": "eob",
            "insurance_company": bill["insurance"]["company"],
            "patient": bill["patient"],
            "provider": bill["provider"],
            "service_date": bill["service_date"],
            "processed_date": fake.date_between(
                start_date=datetime.datetime.strptime(bill["service_date"], '%Y-%m-%d').date(),
                end_date='today'
            ).strftime('%Y-%m-%d'),
            "claim_number": fake.bothify(text='CLM#######'),
            "services": []
        }
        
        for service in bill["services"]:
            # Определяем покрытие страховкой
            if random.random() < 0.1:  # 10% chance of denial
                coverage_status = "denied"
                insurance_payment = 0
                patient_responsibility = service["charge"]
                denial_reason = random.choice([
                    "Service not covered under plan",
                    "Prior authorization required",
                    "Out-of-network provider",
                    "Benefit limit exceeded",
                    "Medical necessity not established"
                ])
            else:
                coverage_status = "covered"
                insurance_payment = service["charge"] * random.uniform(0.7, 0.9)
                patient_responsibility = service["charge"] - insurance_payment
                denial_reason = None
            
            eob["services"].append({
                "code": service["code"],
                "description": service["description"],
                "date": service["date"],
                "billed_amount": service["charge"],
                "insurance_payment": round(insurance_payment, 2),
                "patient_responsibility": round(patient_responsibility, 2),
                "coverage_status": coverage_status,
                "denial_reason": denial_reason
            })
        
        return eob
    
    def save_test_data(self, data: Dict[str, Any], filename: str, output_dir: str = "test-data"):
        """Сохраняет тестовые данные в файл"""
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        if filename.endswith('.json'):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif filename.endswith('.txt'):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._format_as_text(data))
        
        print(f"Сохранено: {filepath}")
        return filepath
    
    def _format_as_text(self, data: Dict[str, Any]) -> str:
        """Форматирует данные как текст для имитации реального документа"""
        if data["document_type"] == "medical_bill":
            return self._format_bill_as_text(data)
        elif data["document_type"] == "lab_results":
            return self._format_lab_as_text(data)
        elif data["document_type"] == "eob":
            return self._format_eob_as_text(data)
        else:
            return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _format_bill_as_text(self, bill: Dict[str, Any]) -> str:
        """Formats bill as text"""
        text = f"""
MEDICAL BILL

Provider: {bill['provider']['name']}
NPI: {bill['provider']['npi']}
Specialty: {bill['provider']['specialty']}

Patient: {bill['patient']['name']}
Date of Birth: {bill['patient']['dob']}
Member ID: {bill['patient']['member_id']}
Address: {bill['patient']['address']}

Insurance Company: {bill['insurance']['company']['name']}
Policy Number: {bill['insurance']['policy_number']}
Group Number: {bill['insurance']['group_number']}

Service Date: {bill['service_date']}
Billing Date: {bill['billing_date']}

SERVICES:
"""
        
        for service in bill['services']:
            text += f"""
Code: {service['code']}
Description: {service['description']}
Date: {service.get('date', 'N/A')}
Quantity: {service.get('quantity', 1)}
Charge: ${service['charge']}
"""
        
        text += f"""
FINANCIAL SUMMARY:
Total Charges: ${bill['financial_summary']['total_charges']}
Insurance Payment: ${bill['financial_summary']['insurance_payment']}
Patient Responsibility: ${bill['financial_summary']['patient_responsibility']}
Deductible: ${bill['financial_summary']['deductible']}
Copay: ${bill['financial_summary']['copay']}

Diagnosis Codes: {', '.join(bill['billing_codes']['diagnosis_codes'])}
Procedure Codes: {', '.join(bill['billing_codes']['procedure_codes'])}
"""
        
        return text
    
    def _format_lab_as_text(self, lab: Dict[str, Any]) -> str:
        """Formats laboratory results as text"""
        text = f"""
LABORATORY RESULTS

Laboratory: {lab['provider']['name']}
NPI: {lab['provider']['npi']}

Patient: {lab['patient']['name']}
Date of Birth: {lab['patient']['dob']}
Gender: {lab['patient']['gender']}
Member ID: {lab['patient']['member_id']}

Test Date: {lab['test_date']}
Report Date: {lab['report_date']}

Ordering Physician: {lab['ordering_physician']['name']}
NPI: {lab['ordering_physician']['npi']}
Specialty: {lab['ordering_physician']['specialty']}

RESULTS:
"""
        
        for value in lab['lab_values']:
            status_symbol = "✅" if value["status"] == "normal" else "⚠️" if value["status"] in ["high", "low"] else "❌"
            text += f"""
{status_symbol} {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']})
"""
        
        if lab['trend_data']:
            text += "\nTREND DATA:\n"
            for trend in lab['trend_data']:
                text += f"\nDate: {trend['date']}\n"
                for value in trend['values']:
                    text += f"  {value['test_name']}: {value['value']} {value['unit']}\n"
        
        text += f"\nCLINICAL NOTES:\n{lab['clinical_notes']}\n"
        
        return text
    
    def _format_eob_as_text(self, eob: Dict[str, Any]) -> str:
        """Formats EOB as text"""
        text = f"""
EXPLANATION OF BENEFITS (EOB)

Insurance Company: {eob['insurance_company']['name']}
Claim Number: {eob['claim_number']}

Patient: {eob['patient']['name']}
Member ID: {eob['patient']['member_id']}

Provider: {eob['provider']['name']}
NPI: {eob['provider']['npi']}

Service Date: {eob['service_date']}
Processed Date: {eob['processed_date']}

COVERAGE DETAILS:
"""
        
        for service in eob['services']:
            status_symbol = "✅" if service['coverage_status'] == "covered" else "❌"
            text += f"""
{status_symbol} Code: {service['code']}
   Description: {service['description']}
   Date: {service['date']}
   Billed Amount: ${service['billed_amount']}
   Insurance Payment: ${service['insurance_payment']}
   Patient Responsibility: ${service['patient_responsibility']}
"""
            if service['denial_reason']:
                text += f"   Denial Reason: {service['denial_reason']}\n"
        
        return text


def main():
    """Main function for generating test data"""
    generator = TestDataGenerator()
    
    # Create directories for different data types
    os.makedirs("test-data/bills", exist_ok=True)
    os.makedirs("test-data/lab-results", exist_ok=True)
    os.makedirs("test-data/eob", exist_ok=True)
    os.makedirs("test-data/edge-cases", exist_ok=True)
    
    print("Generating test data for BillDecoder/LabDecoder...")
    
    # Generate medical bills
    print("\n=== Generating Medical Bills ===")
    for i in range(10):
        complexity = random.choice(["simple", "medium", "complex"])
        include_errors = random.random() < 0.3  # 30% bills with errors
        
        bill = generator.generate_medical_bill(complexity=complexity, include_errors=include_errors)
        
        # Save as JSON
        json_filename = f"bills/bill_{i+1:03d}_{complexity}.json"
        generator.save_test_data(bill, json_filename)
        
        # Save as text
        txt_filename = f"bills/bill_{i+1:03d}_{complexity}.txt"
        generator.save_test_data(bill, txt_filename)
    
    # Generate laboratory results
    print("\n=== Generating Laboratory Results ===")
    for i in range(10):
        complexity = random.choice(["basic", "comprehensive", "full"])
        include_abnormal = random.random() < 0.4  # 40% with abnormal values
        
        lab = generator.generate_lab_results(complexity=complexity, include_abnormal=include_abnormal)
        
        # Save as JSON
        json_filename = f"lab-results/lab_{i+1:03d}_{complexity}.json"
        generator.save_test_data(lab, json_filename)
        
        # Save as text
        txt_filename = f"lab-results/lab_{i+1:03d}_{complexity}.txt"
        generator.save_test_data(lab, txt_filename)
    
    # Generate EOB
    print("\n=== Generating EOB ===")
    for i in range(5):
        # Create bill for EOB
        bill = generator.generate_medical_bill(complexity="medium")
        eob = generator.generate_eob(bill)
        
        # Save as JSON
        json_filename = f"eob/eob_{i+1:03d}.json"
        generator.save_test_data(eob, json_filename)
        
        # Save as text
        txt_filename = f"eob/eob_{i+1:03d}.txt"
        generator.save_test_data(eob, txt_filename)
    
    # Generate edge cases
    print("\n=== Generating Edge Cases ===")
    
    # Bill with multiple errors
    complex_bill = generator.generate_medical_bill(complexity="complex", include_errors=True)
    generator.save_test_data(complex_bill, "edge-cases/bill_multiple_errors.json")
    generator.save_test_data(complex_bill, "edge-cases/bill_multiple_errors.txt")
    
    # Laboratory results with critical values
    critical_lab = generator.generate_lab_results(complexity="full", include_abnormal=True)
    # Force some values to be critical
    for value in critical_lab['lab_values']:
        if value["status"] in ["high", "low"] and random.random() < 0.5:
            value["status"] = "critical"
    generator.save_test_data(critical_lab, "edge-cases/lab_critical_values.json")
    generator.save_test_data(critical_lab, "edge-cases/lab_critical_values.txt")
    
    # EOB with multiple denials
    denied_bill = generator.generate_medical_bill(complexity="medium")
    denied_eob = generator.generate_eob(denied_bill)
    # Force denial of most services
    for service in denied_eob['services']:
        if random.random() < 0.7:
            service['coverage_status'] = "denied"
            service['insurance_payment'] = 0
            service['patient_responsibility'] = service['billed_amount']
            service['denial_reason'] = random.choice([
                "Service not covered under plan",
                "Prior authorization required",
                "Out-of-network provider",
                "Benefit limit exceeded"
            ])
    generator.save_test_data(denied_eob, "edge-cases/eob_multiple_denials.json")
    generator.save_test_data(denied_eob, "edge-cases/eob_multiple_denials.txt")
    
    print(f"\n✅ Generation completed!")
    print(f"📁 Files created:")
    print(f"   - Medical Bills: 20 files")
    print(f"   - Laboratory Results: 20 files") 
    print(f"   - EOB: 10 files")
    print(f"   - Edge Cases: 6 files")
    print(f"📊 Total: 56 test files")


if __name__ == "__main__":
    main()
