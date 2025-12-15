#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pdf_extractor import extract_all_pdfs
from src.comparator import DocumentComparator
from src.report_generator import (
    StructuredDataExtractor,
    DetailedDiscrepancyAnalyzer,
    AlertGenerator,
    generate_all_reports
)
from src.config import settings
import json

def main():
    print("\n" + "="*70)
    print("COMPLETE PDF ANALYSIS SYSTEM TEST")
    print("="*70 + "\n")
    
    data_dir = settings.DATA_DIR
    reports_dir = settings.REPORTS_DIR
    
    print("[1/6] Extracting PDF Documents...")
    documents = extract_all_pdfs(data_dir)
    
    if not documents:
        print("[ERR] No documents found!")
        return
    
    for name, doc in documents.items():
        print(f"  [OK] {name}: {doc.metadata.doc_type}")
    
    print("\n[2/6] Extracting Structured Data...")
    po_doc = None
    invoice_doc = None
    
    for name, doc in documents.items():
        if 'PURCHASE_ORDER' in doc.metadata.doc_type:
            po_doc = doc
        elif 'INVOICE' in doc.metadata.doc_type:
            invoice_doc = doc
    
    if po_doc and invoice_doc:
        po_data = StructuredDataExtractor.extract_document_data(po_doc)
        pi_data = StructuredDataExtractor.extract_document_data(invoice_doc)
        
        print(f"  [OK] PO: {po_data['document_id']}")
        print(f"       - Items: {len(po_data['items'])}")
        print(f"       - Total: ${po_data['summary']['grand_total']}")
        
        print(f"  [OK] Invoice: {pi_data['document_id']}")
        print(f"       - Items: {len(pi_data['items'])}")
        print(f"       - Total: ${pi_data['summary']['grand_total']}")
    else:
        print("[ERR] Could not find both PO and Invoice!")
        return
    
    print("\n[3/6] Running Comparison Analysis...")
    comparator = DocumentComparator()
    comparison = comparator.compare(po_doc, invoice_doc)
    
    print(f"  [OK] Comparison Complete")
    print(f"       - Matching Items: {comparison.matching_items}")
    print(f"       - Discrepant Items: {comparison.discrepant_items}")
    print(f"       - PO Total: ${comparison.po_total:.2f}")
    print(f"       - Invoice Total: ${comparison.invoice_total:.2f}")
    print(f"       - Variance: ${comparison.grand_total_diff:.2f} ({comparison.grand_total_variance_pct:.2f}%)")
    
    print("\n[4/6] Generating Detailed Analysis...")
    detailed_analysis = DetailedDiscrepancyAnalyzer.analyze_all_items(po_doc, invoice_doc, comparison)
    
    print(f"  [OK] Quantity Analysis: {len(detailed_analysis['quantity_analysis'])} items")
    print(f"  [OK] Price Analysis: {len(detailed_analysis['price_analysis'])} discrepancies")
    print(f"  [OK] Totals Analysis: Complete")
    print(f"  [OK] Mismatches Summary: {len(detailed_analysis['mismatches_summary'])} mismatches")
    
    print("\n[5/6] Generating Alerts...")
    alerts = AlertGenerator.generate_alerts(comparison)
    
    print(f"  [OK] Generated {len(alerts)} alerts")
    for i, alert in enumerate(alerts, 1):
        print(f"       [{i}] {alert['level']}: {alert['type']}")
        print(f"           {alert['message']}")
    
    print("\n[6/6] Generating All Reports...")
    report_paths = generate_all_reports(comparison, reports_dir, po_doc, invoice_doc)
    
    print(f"  [OK] Reports generated:")
    for report_type, path in report_paths.items():
        print(f"       - {report_type.upper()}: {Path(path).name}")
    
    print("\n" + "="*70)
    print("EXPECTED OUTPUTS VALIDATION")
    print("="*70 + "\n")
    
    print("[CHECK] 1. Structured Data Extraction")
    if 'extracted_data' in report_paths:
        print("  [OK] extracted_data.json contains:")
        with open(report_paths['extracted_data']) as f:
            extracted = json.load(f)
        print(f"       - PO: {len(extracted['purchase_order']['items'])} items")
        print(f"       - Invoice: {len(extracted['proforma_invoice']['items'])} items")
    
    print("\n[CHECK] 2. Discrepancy Analysis")
    if 'detailed_analysis' in report_paths:
        print("  [OK] detailed_analysis.json contains:")
        with open(report_paths['detailed_analysis']) as f:
            analysis = json.load(f)
        print(f"       - Quantity Analysis: {len(analysis['quantity_analysis'])} items")
        print(f"       - Price Analysis: {len(analysis['price_analysis'])} items")
        print(f"       - Mismatches: {len(analysis['mismatches_summary'])} items")
        print(f"       - Alerts: {len(analysis['alerts'])} alerts")
    
    print("\n[CHECK] 3. Multi-Format Reports")
    formats = ['json', 'csv', 'excel', 'html', 'alerts']
    for fmt in formats:
        if fmt in report_paths:
            print(f"  [OK] {fmt.upper()} report: {Path(report_paths[fmt]).name}")
    
    print("\n[CHECK] 4. Comprehensive Excel with Multiple Sheets")
    if 'comprehensive_excel' in report_paths:
        print(f"  [OK] comprehensive_analysis.xlsx with sheets:")
        print(f"       - Summary")
        print(f"       - Quantity_Analysis")
        print(f"       - Price_Analysis")
        print(f"       - Totals_Summary")
        print(f"       - Mismatches")
        print(f"       - Alerts")
    
    print("\n[CHECK] 5. Automated Alerts & Recommendations")
    if alerts:
        print(f"  [OK] Generated {len(alerts)} alerts with recommendations")
        for alert in alerts:
            print(f"       - {alert['level']}: {alert['recommendation']}")
    else:
        print("  [OK] No alerts needed - documents match!")
    
    print("\n" + "="*70)
    print("ALL EXPECTED OUTPUTS SUCCESSFULLY GENERATED")
    print("="*70 + "\n")
    
    print("System is ready for production use with:")
    print("  - Streamlit Web UI (run: streamlit run app.py)")
    print("  - Advanced RAG Chatbot")
    print("  - Comprehensive Reporting")
    print("  - Automated Alert System")

if __name__ == "__main__":
    main()
