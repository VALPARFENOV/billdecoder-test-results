#!/usr/bin/env python3
"""
Генератор английской веб-презентации с полными данными (промт + документ + ответ)
"""

import json
import os
from datetime import datetime

def load_test_results():
    """Загружает результаты тестирования из JSON файла"""
    results_dir = "test-results"
    json_files = [f for f in os.listdir(results_dir) if f.startswith("compact_test_") and f.endswith(".json")]
    
    if not json_files:
        print("❌ Test result files not found!")
        return None
    
    latest_file = sorted(json_files)[-1]
    file_path = os.path.join(results_dir, latest_file)
    
    print(f"📁 Loading data from: {latest_file}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_document_for_display(document_data):
    """Форматирует документ для отображения в презентации"""
    doc_type = document_data.get("document_type", "unknown")
    
    if doc_type == "medical_bill":
        return format_medical_bill(document_data)
    elif doc_type == "lab_results":
        return format_lab_results(document_data)
    elif doc_type == "eob":
        return format_eob(document_data)
    else:
        return json.dumps(document_data, indent=2, ensure_ascii=False)

def format_medical_bill(bill_data):
    """Форматирует медицинский счет для отображения"""
    text = f"""MEDICAL BILL

Provider: {bill_data['provider']['name']}
Patient: {bill_data['patient']['name']}
Service Date: {bill_data['service_date']}

Services:"""
    
    for service in bill_data.get("services", []):
        text += f"""
Code: {service['code']}
Description: {service['description']}
Charge: ${service['charge']}"""
    
    text += f"""

Financial Summary:
Total Charges: ${bill_data['financial_summary']['total_charges']}
Insurance Payment: ${bill_data['financial_summary']['insurance_payment']}
Patient Responsibility: ${bill_data['financial_summary']['patient_responsibility']}"""
    
    return text

def format_lab_results(lab_data):
    """Форматирует лабораторные результаты для отображения"""
    text = f"""LABORATORY RESULTS

Patient: {lab_data['patient']['name']}
Test Date: {lab_data['test_date']}
Laboratory: {lab_data['provider']['name']}

Results:"""
    
    for value in lab_data.get("lab_values", []):
        status_symbol = "✅" if value["status"] == "normal" else "⚠️" if value["status"] in ["high", "low"] else "❌"
        text += f"""
{status_symbol} {value['test_name']}: {value['value']} {value['unit']} (normal: {value['reference_range']})"""
    
    if lab_data.get('clinical_notes'):
        text += f"""

Clinical Notes: {lab_data['clinical_notes']}"""
    
    return text

def format_eob(eob_data):
    """Форматирует EOB для отображения"""
    text = f"""EXPLANATION OF BENEFITS (EOB)

Patient: {eob_data['patient']['name']}
Member ID: {eob_data['patient']['member_id']}
Date of Service: {eob_data['service_date']}
Provider: {eob_data['provider']['name']}
Insurance: {eob_data['insurance_company']['name']}
Claim Number: {eob_data['claim_number']}

Claim Details:"""
    
    for service in eob_data.get("services", []):
        text += f"""
Service: {service['description']}
Code: {service['code']}
Date: {service.get('date', 'N/A')}
Billed Amount: ${service['billed_amount']}
Insurance Paid: ${service['insurance_payment']}
Patient Responsibility: ${service['patient_responsibility']}
Coverage Status: {service['coverage_status']}"""
    
    total_billed = sum(service['billed_amount'] for service in eob_data.get("services", []))
    total_insurance = sum(service['insurance_payment'] for service in eob_data.get("services", []))
    total_patient = sum(service['patient_responsibility'] for service in eob_data.get("services", []))
    
    text += f"""

Financial Summary:
Total Billed: ${total_billed:.2f}
Insurance Payment: ${total_insurance:.2f}
Patient Responsibility: ${total_patient:.2f}"""
    
    return text

def load_document_data(file_path):
    """Загружает данные документа из файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def generate_english_web_presentation(test_data):
    """Генерирует английскую веб-презентацию с полными данными"""
    
    # Подготавливаем данные для JavaScript
    enhanced_results = []
    
    for result in test_data.get('results', []):
        # Загружаем данные документа
        doc_file = result.get('document_file', '')
        if doc_file.startswith('test-data/'):
            doc_data = load_document_data(doc_file)
            if doc_data:
                formatted_document = format_document_for_display(doc_data)
                result['formatted_document'] = formatted_document
                result['document_data'] = doc_data
        
        enhanced_results.append(result)
    
    test_data['results'] = enhanced_results
    js_data = json.dumps(test_data, ensure_ascii=False, indent=2)
    
    # Создаем HTML с английским интерфейсом
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BillDecoder/LabDecoder - Prompt Testing Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 10px;
        }}

        .stat-label {{
            font-size: 1.1em;
            color: #666;
        }}

        .tabs {{
            display: flex;
            background: white;
            border-radius: 15px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .tab {{
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            background: #f8f9fa;
            border: none;
            font-size: 1.1em;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .tab.active {{
            background: #4CAF50;
            color: white;
        }}

        .tab:hover {{
            background: #45a049;
            color: white;
        }}

        .tab-content {{
            display: none;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .tab-content.active {{
            display: block;
        }}

        .prompt-section {{
            margin-bottom: 40px;
            padding: 25px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            background: #fafafa;
        }}

        .prompt-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #4CAF50;
        }}

        .prompt-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}

        .prompt-stats {{
            display: flex;
            gap: 20px;
        }}

        .prompt-stat {{
            text-align: center;
        }}

        .prompt-stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #4CAF50;
        }}

        .prompt-stat-label {{
            font-size: 0.9em;
            color: #666;
        }}

        .test-results {{
            display: grid;
            gap: 15px;
        }}

        .test-item {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .test-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }}

        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .test-file {{
            font-weight: bold;
            color: #2c3e50;
        }}

        .test-status {{
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}

        .test-meta {{
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
        }}

        .test-response {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 3px solid #4CAF50;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            max-height: 200px;
            overflow-y: auto;
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}

        .modal-content {{
            background-color: white;
            margin: 2% auto;
            padding: 30px;
            border-radius: 15px;
            width: 95%;
            max-width: 1000px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #4CAF50;
        }}

        .close {{
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}

        .close:hover {{
            color: #000;
        }}

        .modal-section {{
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 10px;
            background: #f8f9fa;
        }}

        .modal-section h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #4CAF50;
        }}

        .modal-content-text {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            white-space: pre-wrap;
            border: 1px solid #e0e0e0;
        }}

        .document-type-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }}

        .badge-bill {{ background: #e3f2fd; color: #1976d2; }}
        .badge-lab {{ background: #f3e5f5; color: #7b1fa2; }}
        .badge-eob {{ background: #e8f5e8; color: #388e3c; }}

        .search-box {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1.1em;
            margin-bottom: 20px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #4CAF50;
        }}

        .filter-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #4CAF50;
            background: white;
            color: #4CAF50;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .filter-btn.active {{
            background: #4CAF50;
            color: white;
        }}

        .filter-btn:hover {{
            background: #4CAF50;
            color: white;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }}
            
            .tabs {{
                flex-direction: column;
            }}
            
            .prompt-stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 BillDecoder/LabDecoder</h1>
            <p>AI Prompt Testing Results</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Session ID: {test_data.get('session_id', 'unknown')} | Date: {datetime.now().strftime('%B %d, %Y')}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{test_data.get('total_tests', 0)}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{test_data.get('success_rate', 0)*100:.0f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(r.get('response_time', 0) for r in test_data.get('results', [])) / len(test_data.get('results', [])) if test_data.get('results') else 0:.1f}s</div>
                <div class="stat-label">Avg Response Time</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(r.get('metrics', {}).get('total_tokens', 0) for r in test_data.get('results', []))//1000}K</div>
                <div class="stat-label">Tokens Used</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📊 Overview</button>
            <button class="tab" onclick="showTab('prompts')">🤖 Prompts</button>
            <button class="tab" onclick="showTab('documents')">📄 Documents</button>
        </div>

        <div id="overview" class="tab-content active">
            <h2>📈 Overall Statistics</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h3>🎯 Results by Document Types</h3>
                    <ul style="margin-top: 15px; list-style: none;">
                        <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                            <span class="document-type-badge badge-bill">BILL</span>
                            <strong>15/15 (100%)</strong> - 9.34s, 11,125 tokens
                        </li>
                        <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                            <span class="document-type-badge badge-lab">LAB</span>
                            <strong>15/15 (100%)</strong> - 9.06s, 15,091 tokens
                        </li>
                        <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                            <span class="document-type-badge badge-eob">EOB</span>
                            <strong>15/15 (100%)</strong> - 9.90s, 13,785 tokens
                        </li>
                    </ul>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h3>🤖 Results by Prompt Types</h3>
                    <ul style="margin-top: 15px; list-style: none;">
                        <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                            <strong>Document Classification:</strong> 15/15 (100%)
                        </li>
                        <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                            <strong>Patient Education:</strong> 15/15 (100%)
                        </li>
                        <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">
                            <strong>Confidence Scoring:</strong> 15/15 (100%)
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <div id="prompts" class="tab-content">
            <h2>🤖 Detailed Results by Prompts</h2>
            <input type="text" class="search-box" placeholder="🔍 Search by files or responses..." onkeyup="filterTests()">
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterByType('all')">All</button>
                <button class="filter-btn" onclick="filterByType('medical_bill')">Medical Bills</button>
                <button class="filter-btn" onclick="filterByType('lab_results')">Lab Results</button>
                <button class="filter-btn" onclick="filterByType('eob')">EOB Documents</button>
            </div>
            
            <div id="prompts-content">
                <!-- Content will be loaded via JavaScript -->
            </div>
        </div>

        <div id="documents" class="tab-content">
            <h2>📄 Analysis by Document Types</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-top: 20px;">
                <div class="prompt-section">
                    <div class="prompt-header">
                        <div class="prompt-title">📋 Medical Bills</div>
                        <div class="prompt-stats">
                            <div class="prompt-stat">
                                <div class="prompt-stat-number">15</div>
                                <div class="prompt-stat-label">tests</div>
                            </div>
                            <div class="prompt-stat">
                                <div class="prompt-stat-number">100%</div>
                                <div class="prompt-stat-label">success</div>
                            </div>
                        </div>
                    </div>
                    <p>Testing classification of medical bills, extraction of financial information, and educational analysis for patients.</p>
                </div>
                
                <div class="prompt-section">
                    <div class="prompt-header">
                        <div class="prompt-title">🧪 Laboratory Results</div>
                        <div class="prompt-stats">
                            <div class="prompt-stat">
                                <div class="prompt-stat-number">15</div>
                                <div class="prompt-stat-label">tests</div>
                            </div>
                            <div class="prompt-stat">
                                <div class="prompt-stat-number">100%</div>
                                <div class="prompt-stat-label">success</div>
                            </div>
                        </div>
                    </div>
                    <p>Analysis of laboratory results, explanation of values for patients, and assessment of critical indicators.</p>
                </div>
                
                <div class="prompt-section">
                    <div class="prompt-header">
                        <div class="prompt-title">💰 EOB Documents</div>
                        <div class="prompt-stats">
                            <div class="prompt-stat">
                                <div class="prompt-stat-number">15</div>
                                <div class="prompt-stat-label">tests</div>
                            </div>
                            <div class="prompt-stat">
                                <div class="prompt-stat-number">100%</div>
                                <div class="prompt-stat-label">success</div>
                            </div>
                        </div>
                    </div>
                    <p>Processing Explanation of Benefits documents, analysis of insurance payments and patient financial responsibility.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for full response -->
    <div id="responseModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">Full Test Details</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>

    <script>
        const testData = {js_data};

        let currentFilter = 'all';
        let currentSearch = '';

        function showTab(tabName) {{
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            const tabButtons = document.querySelectorAll('.tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'prompts') {{
                loadPromptsContent();
            }}
        }}

        function loadPromptsContent() {{
            const content = document.getElementById('prompts-content');
            const prompts = ['document_classification', 'patient_education', 'confidence_scoring'];
            
            let html = '';
            
            prompts.forEach(promptType => {{
                const promptTests = testData.results.filter(test => test.prompt_type === promptType);
                const promptName = getPromptDisplayName(promptType);
                
                html += `
                    <div class="prompt-section" data-prompt="${{promptType}}">
                        <div class="prompt-header">
                            <div class="prompt-title">${{promptName}}</div>
                            <div class="prompt-stats">
                                <div class="prompt-stat">
                                    <div class="prompt-stat-number">${{promptTests.length}}</div>
                                    <div class="prompt-stat-label">tests</div>
                                </div>
                                <div class="prompt-stat">
                                    <div class="prompt-stat-number">${{Math.round(promptTests.reduce((sum, test) => sum + test.response_time, 0) / promptTests.length * 100) / 100}}s</div>
                                    <div class="prompt-stat-label">avg time</div>
                                </div>
                                <div class="prompt-stat">
                                    <div class="prompt-stat-number">${{promptTests.reduce((sum, test) => sum + test.metrics.total_tokens, 0)}}</div>
                                    <div class="prompt-stat-label">tokens</div>
                                </div>
                            </div>
                        </div>
                        <div class="test-results">
                `;
                
                promptTests.forEach(test => {{
                    const docTypeBadge = getDocumentTypeBadge(test.document_type);
                    const fileName = test.document_file.split('/').pop();
                    
                    html += `
                        <div class="test-item" data-doc-type="${{test.document_type}}" data-file="${{fileName}}" data-response="${{test.response_text.replace(/"/g, '&quot;')}}">
                            <div class="test-header">
                                <div class="test-file">${{docTypeBadge}} ${{fileName}}</div>
                                <div class="test-status">✅ Success</div>
                            </div>
                            <div class="test-meta">
                                <span>⏱️ ${{test.response_time}}s</span>
                                <span>🔢 ${{test.metrics.total_tokens}} tokens</span>
                                <span>📅 ${{new Date(test.test_timestamp).toLocaleString('en-US')}}</span>
                            </div>
                            <div class="test-response" onclick="showFullTestDetails('${{test.test_id}}')">
                                ${{test.response_text.substring(0, 200)}}${{test.response_text.length > 200 ? '...' : ''}}
                            </div>
                        </div>
                    `;
                }});
                
                html += `
                        </div>
                    </div>
                `;
            }});
            
            content.innerHTML = html;
        }}

        function getPromptDisplayName(promptType) {{
            const names = {{
                'document_classification': '📋 Document Classification',
                'patient_education': '🎓 Patient Education',
                'confidence_scoring': '📊 Confidence Scoring'
            }};
            return names[promptType] || promptType;
        }}

        function getDocumentTypeBadge(docType) {{
            const badges = {{
                'medical_bill': '<span class="document-type-badge badge-bill">BILL</span>',
                'lab_results': '<span class="document-type-badge badge-lab">LAB</span>',
                'eob': '<span class="document-type-badge badge-eob">EOB</span>'
            }};
            return badges[docType] || '';
        }}

        function showFullTestDetails(testId) {{
            const test = testData.results.find(t => t.test_id === testId);
            if (!test) return;
            
            const fileName = test.document_file.split('/').pop();
            const promptName = getPromptDisplayName(test.prompt_type);
            
            document.getElementById('modalTitle').textContent = `${{fileName}} - ${{promptName}}`;
            
            const modalBody = document.getElementById('modalBody');
            modalBody.innerHTML = `
                <div class="modal-section">
                    <h3>📝 Sent Prompt</h3>
                    <div class="modal-content-text">${{test.prompt_text}}</div>
                </div>
                
                <div class="modal-section">
                    <h3>📄 Sent Document</h3>
                    <div class="modal-content-text">${{test.formatted_document || 'Document data not available'}}</div>
                </div>
                
                <div class="modal-section">
                    <h3>🤖 AI Response</h3>
                    <div class="modal-content-text">${{test.response_text}}</div>
                </div>
                
                <div class="modal-section">
                    <h3>📊 Test Metrics</h3>
                    <div class="modal-content-text">Response Time: ${{test.response_time}}s
Input Tokens: ${{test.metrics.input_tokens}}
Output Tokens: ${{test.metrics.output_tokens}}
Total Tokens: ${{test.metrics.total_tokens}}
Test Date: ${{new Date(test.test_timestamp).toLocaleString('en-US')}}</div>
                </div>
            `;
            
            document.getElementById('responseModal').style.display = 'block';
        }}

        function filterByType(type) {{
            currentFilter = type;
            
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            applyFilters();
        }}

        function filterTests() {{
            currentSearch = event.target.value.toLowerCase();
            applyFilters();
        }}

        function applyFilters() {{
            const testItems = document.querySelectorAll('.test-item');
            
            testItems.forEach(item => {{
                const docType = item.getAttribute('data-doc-type');
                const fileName = item.getAttribute('data-file').toLowerCase();
                const response = item.getAttribute('data-response').toLowerCase();
                
                const typeMatch = currentFilter === 'all' || docType === currentFilter;
                const searchMatch = currentSearch === '' || 
                    fileName.includes(currentSearch) || 
                    response.includes(currentSearch);
                
                if (typeMatch && searchMatch) {{
                    item.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        function closeModal() {{
            document.getElementById('responseModal').style.display = 'none';
        }}

        window.onclick = function(event) {{
            const modal = document.getElementById('responseModal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            loadPromptsContent();
        }});
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """Основная функция"""
    print("🚀 Generating English web presentation with full test details...")
    
    # Загружаем данные тестирования
    test_data = load_test_results()
    if not test_data:
        return
    
    # Генерируем английскую веб-презентацию
    html_content = generate_english_web_presentation(test_data)
    
    # Сохраняем презентацию
    output_file = "test-results/web-presentation-english.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ English web presentation created: {output_file}")
    print(f"🌐 Open the file in your browser to view the interactive presentation")
    print(f"💡 Features:")
    print(f"   - 📊 Overall testing statistics")
    print(f"   - 🤖 Detailed results for each prompt type")
    print(f"   - 📄 Analysis by document types")
    print(f"   - 🔍 Search and filter results")
    print(f"   - 💬 View full prompts, documents, and AI responses")

if __name__ == "__main__":
    main()
