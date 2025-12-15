# # import json
# # import csv
# # from pathlib import Path
# # from typing import Dict, List, Any
# # from datetime import datetime
# # import pandas as pd
# # from src.comparator import DocumentComparison, ItemDiscrepancy
# # from src.pdf_extractor import ExtractedDocument


# # class StructuredDataExtractor:
# #     @staticmethod
# #     def extract_document_data(doc: ExtractedDocument) -> Dict[str, Any]:
# #         return {
# #             "document_type": doc.metadata.doc_type,
# #             "document_id": doc.metadata.document_id,
# #             "date": doc.metadata.date,
# #             "vendor": doc.metadata.vendor_name,
# #             "customer": doc.metadata.customer_name,
# #             "items": [
# #                 {
# #                     "sku": item.item_no,
# #                     "description": item.description,
# #                     "unit": item.unit,
# #                     "quantity": item.quantity,
# #                     "unit_price": round(item.unit_price, 2),
# #                     "line_total": round(item.total_price, 2)
# #                 }
# #                 for item in doc.items
# #             ],
# #             "summary": {
# #                 "subtotal": round(doc.subtotal, 2),
# #                 "tax": round(doc.tax, 2),
# #                 "grand_total": round(doc.total, 2)
# #             },
# #             "extraction_timestamp": datetime.now().isoformat()
# #         }
    
# #     @staticmethod
# #     def generate_extraction_json(po_doc: ExtractedDocument, pi_doc: ExtractedDocument, output_dir: Path) -> str:
# #         extraction_data = {
# #             "purchase_order": StructuredDataExtractor.extract_document_data(po_doc),
# #             "proforma_invoice": StructuredDataExtractor.extract_document_data(pi_doc)
# #         }
        
# #         output_path = output_dir / "extracted_data.json"
# #         with open(output_path, 'w') as f:
# #             json.dump(extraction_data, f, indent=2)
        
# #         return str(output_path)


# # class DetailedDiscrepancyAnalyzer:
# #     @staticmethod
# #     def analyze_all_items(po_doc: ExtractedDocument, pi_doc: ExtractedDocument, comparison: DocumentComparison) -> Dict[str, Any]:
# #         analysis = {
# #             "quantity_analysis": DetailedDiscrepancyAnalyzer._analyze_quantities(po_doc, pi_doc, comparison),
# #             "price_analysis": DetailedDiscrepancyAnalyzer._analyze_prices(comparison),
# #             "totals_analysis": DetailedDiscrepancyAnalyzer._analyze_totals(comparison),
# #             "mismatches_summary": DetailedDiscrepancyAnalyzer._summarize_mismatches(comparison)
# #         }
# #         return analysis
    
# #     @staticmethod
# #     def _analyze_quantities(po_doc, pi_doc, comparison):
# #         items = []
# #         po_items_map = {item.item_no: item for item in po_doc.items}
# #         pi_items_map = {item.item_no: item for item in pi_doc.items}
        
# #         all_skus = set(po_items_map.keys()) | set(pi_items_map.keys())
        
# #         for sku in sorted(all_skus):
# #             po_qty = po_items_map.get(sku, None)
# #             pi_qty = pi_items_map.get(sku, None)
            
# #             po_quantity = po_qty.quantity if po_qty else 0
# #             pi_quantity = pi_qty.quantity if pi_qty else 0
# #             diff = pi_quantity - po_quantity
            
# #             items.append({
# #                 "sku": sku,
# #                 "description": (po_qty.description if po_qty else pi_qty.description) if (po_qty or pi_qty) else "Unknown",
# #                 "po_quantity": po_quantity,
# #                 "pi_quantity": pi_quantity,
# #                 "difference": diff,
# #                 "status": "MATCH" if diff == 0 else "MISMATCH"
# #             })
        
# #         return items
    
# #     @staticmethod
# #     def _analyze_prices(comparison):
# #         items = []
# #         for d in comparison.discrepancies:
# #             items.append({
# #                 "sku": d.item_no,
# #                 "description": d.description,
# #                 "po_unit_price": round(d.po_unit_price, 2),
# #                 "pi_unit_price": round(d.invoice_unit_price, 2),
# #                 "unit_price_diff": round(d.price_diff, 2),
# #                 "po_line_total": round(d.po_total, 2),
# #                 "pi_line_total": round(d.invoice_total, 2),
# #                 "line_total_diff": round(d.total_diff, 2),
# #                 "status": "PRICE_MISMATCH" if d.price_variance_pct != 0 else d.status
# #             })
# #         return items
    
# #     @staticmethod
# #     def _analyze_totals(comparison):
# #         return {
# #             "po_subtotal": round(comparison.po_subtotal, 2),
# #             "pi_subtotal": round(comparison.invoice_subtotal, 2),
# #             "subtotal_difference": round(comparison.subtotal_diff, 2),
# #             "subtotal_variance_pct": round(comparison.subtotal_variance_pct, 2),
# #             "po_grand_total": round(comparison.po_total, 2),
# #             "pi_grand_total": round(comparison.invoice_total, 2),
# #             "grand_total_difference": round(comparison.grand_total_diff, 2),
# #             "grand_total_variance_pct": round(comparison.grand_total_variance_pct, 2)
# #         }
    
# #     @staticmethod
# #     def _summarize_mismatches(comparison):
# #         mismatches = []
# #         for d in comparison.discrepancies:
# #             mismatch_types = []
            
# #             if d.quantity_variance_pct != 0:
# #                 mismatch_types.append("Quantity")
# #             if d.price_variance_pct != 0:
# #                 mismatch_types.append("Unit Price")
# #             if d.total_diff != 0 and d.quantity_variance_pct == 0:
# #                 mismatch_types.append("Line Total")
            
# #             mismatches.append({
# #                 "sku": d.item_no,
# #                 "issue_type": " + ".join(mismatch_types) if mismatch_types else "Other",
# #                 "description": d.description,
# #                 "severity": DetailedDiscrepancyAnalyzer._get_severity(d),
# #                 "details": {
# #                     "quantity_diff": d.quantity_diff if d.quantity_variance_pct != 0 else None,
# #                     "price_diff": round(d.price_diff, 2) if d.price_variance_pct != 0 else None,
# #                     "total_diff": round(d.total_diff, 2)
# #                 }
# #             })
        
# #         return mismatches
    
# #     @staticmethod
# #     def _get_severity(d):
# #         if abs(d.quantity_variance_pct) > 50 or abs(d.price_variance_pct) > 50:
# #             return "CRITICAL"
# #         elif abs(d.quantity_variance_pct) > 10 or abs(d.price_variance_pct) > 10:
# #             return "HIGH"
# #         else:
# #             return "MEDIUM"


# # class AlertGenerator:
# #     @staticmethod
# #     def generate_alerts(comparison: DocumentComparison) -> List[Dict[str, Any]]:
# #         alerts = []
        
# #         variance_pct = abs(comparison.grand_total_variance_pct)
        
# #         if variance_pct > 5:
# #             alerts.append({
# #                 "level": "CRITICAL" if variance_pct > 10 else "HIGH",
# #                 "type": "TOTAL_VALUE_MISMATCH",
# #                 "message": f"Invoice total exceeds PO by AED {comparison.grand_total_diff:.2f} ({variance_pct:.2f}%)",
# #                 "recommendation": "Manual review required before payment processing"
# #             })
        
# #         if comparison.discrepant_items > 0:
# #             alerts.append({
# #                 "level": "HIGH",
# #                 "type": "ITEM_DISCREPANCIES",
# #                 "message": f"{comparison.discrepant_items} item(s) with discrepancies detected",
# #                 "recommendation": "Review line-by-line comparison"
# #             })
        
# #         quantity_mismatches = sum(1 for d in comparison.discrepancies if d.quantity_variance_pct != 0)
# #         if quantity_mismatches > 0:
# #             alerts.append({
# #                 "level": "HIGH",
# #                 "type": "QUANTITY_MISMATCH",
# #                 "message": f"Quantity mismatch on {quantity_mismatches} item(s)",
# #                 "recommendation": "Verify with supplier or delivery documentation"
# #             })
        
# #         price_mismatches = sum(1 for d in comparison.discrepancies if d.price_variance_pct != 0)
# #         if price_mismatches > 0:
# #             alerts.append({
# #                 "level": "HIGH",
# #                 "type": "PRICE_MISMATCH",
# #                 "message": f"Price mismatch on {price_mismatches} item(s)",
# #                 "recommendation": "Verify contract pricing and check for unauthorized changes"
# #             })
        
# #         critical_items = sum(1 for d in comparison.discrepancies if abs(d.price_variance_pct) > 20 or abs(d.quantity_variance_pct) > 20)
# #         if critical_items > 0:
# #             alerts.append({
# #                 "level": "CRITICAL",
# #                 "type": "CRITICAL_VARIANCE",
# #                 "message": f"{critical_items} item(s) with variance > 20%",
# #                 "recommendation": "Escalate for immediate management review"
# #             })
        
# #         return alerts


# # class ReportGenerator:
# #     def __init__(self, output_dir: Path):
# #         self.output_dir = Path(output_dir)
# #         self.output_dir.mkdir(parents=True, exist_ok=True)
    
# #     def generate_json_report(self, comparison: DocumentComparison, filename: str = "comparison_report.json") -> str:
# #         report_data = {
# #             'metadata': {
# #                 'po_id': comparison.po_doc_id,
# #                 'invoice_id': comparison.invoice_doc_id,
# #             },
# #             'summary_statistics': {
# #                 'total_items_in_po': comparison.total_items_po,
# #                 'total_items_in_invoice': comparison.total_items_invoice,
# #                 'items_matching': comparison.matching_items,
# #                 'items_with_discrepancies': comparison.discrepant_items,
# #                 'po_total_value': round(comparison.po_total, 2),
# #                 'invoice_total_value': round(comparison.invoice_total, 2),
# #                 'value_difference': round(comparison.grand_total_diff, 2),
# #                 'variance_percentage': round(comparison.grand_total_variance_pct, 2),
# #             },
# #             'discrepancies': [
# #                 {
# #                     'item_number': d.item_no,
# #                     'description': d.description,
# #                     'quantity': {
# #                         'po': d.po_quantity,
# #                         'invoice': d.invoice_quantity,
# #                         'difference': round(d.quantity_diff, 2),
# #                         'variance_percent': round(d.quantity_variance_pct, 2)
# #                     },
# #                     'unit_price': {
# #                         'po': round(d.po_unit_price, 2),
# #                         'invoice': round(d.invoice_unit_price, 2),
# #                         'difference': round(d.price_diff, 2),
# #                         'variance_percent': round(d.price_variance_pct, 2)
# #                     },
# #                     'total_price': {
# #                         'po': round(d.po_total, 2),
# #                         'invoice': round(d.invoice_total, 2),
# #                         'difference': round(d.total_diff, 2),
# #                     },
# #                     'discrepancy_type': d.status,
# #                     'severity': self._calculate_severity(d)
# #                 }
# #                 for d in comparison.discrepancies
# #             ],
# #             'summary_text': comparison.summary
# #         }
        
# #         output_path = self.output_dir / filename
# #         with open(output_path, 'w') as f:
# #             json.dump(report_data, f, indent=2)
        
# #         return str(output_path)
    
# #     def generate_csv_report(self, comparison: DocumentComparison, filename: str = "comparison_report.csv") -> str:
# #         output_path = self.output_dir / filename
        
# #         with open(output_path, 'w', newline='') as f:
# #             fieldnames = [
# #                 'Item_Number',
# #                 'Description',
# #                 'PO_Quantity',
# #                 'Invoice_Quantity',
# #                 'Quantity_Difference',
# #                 'Quantity_Variance_%',
# #                 'PO_Unit_Price',
# #                 'Invoice_Unit_Price',
# #                 'Price_Difference',
# #                 'Price_Variance_%',
# #                 'PO_Total',
# #                 'Invoice_Total',
# #                 'Total_Difference',
# #                 'Discrepancy_Type',
# #                 'Severity'
# #             ]
            
# #             writer = csv.DictWriter(f, fieldnames=fieldnames)
# #             writer.writeheader()
            
# #             for d in comparison.discrepancies:
# #                 writer.writerow({
# #                     'Item_Number': d.item_no,
# #                     'Description': d.description,
# #                     'PO_Quantity': d.po_quantity,
# #                     'Invoice_Quantity': d.invoice_quantity,
# #                     'Quantity_Difference': round(d.quantity_diff, 2),
# #                     'Quantity_Variance_%': round(d.quantity_variance_pct, 2),
# #                     'PO_Unit_Price': round(d.po_unit_price, 2),
# #                     'Invoice_Unit_Price': round(d.invoice_unit_price, 2),
# #                     'Price_Difference': round(d.price_diff, 2),
# #                     'Price_Variance_%': round(d.price_variance_pct, 2),
# #                     'PO_Total': round(d.po_total, 2),
# #                     'Invoice_Total': round(d.invoice_total, 2),
# #                     'Total_Difference': round(d.total_diff, 2),
# #                     'Discrepancy_Type': d.status,
# #                     'Severity': self._calculate_severity(d)
# #                 })
        
# #         return str(output_path)
    
# #     def generate_excel_report(self, comparison: DocumentComparison, filename: str = "comparison_report.xlsx") -> str:
# #         output_path = self.output_dir / filename
        
# #         with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
# #             summary_df = pd.DataFrame([{
# #                 'PO_ID': comparison.po_doc_id,
# #                 'Invoice_ID': comparison.invoice_doc_id,
# #                 'Total_Items_PO': comparison.total_items_po,
# #                 'Total_Items_Invoice': comparison.total_items_invoice,
# #                 'Matching_Items': comparison.matching_items,
# #                 'Discrepant_Items': comparison.discrepant_items,
# #                 'PO_Total': round(comparison.po_total, 2),
# #                 'Invoice_Total': round(comparison.invoice_total, 2),
# #                 'Difference': round(comparison.grand_total_diff, 2),
# #                 'Variance_%': round(comparison.grand_total_variance_pct, 2)
# #             }])
# #             summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
# #             discrepancy_data = []
# #             for d in comparison.discrepancies:
# #                 discrepancy_data.append({
# #                     'Item_Number': d.item_no,
# #                     'Description': d.description,
# #                     'PO_Qty': d.po_quantity,
# #                     'Invoice_Qty': d.invoice_quantity,
# #                     'Qty_Diff': round(d.quantity_diff, 2),
# #                     'Qty_Variance_%': round(d.quantity_variance_pct, 2),
# #                     'PO_Price': round(d.po_unit_price, 2),
# #                     'Invoice_Price': round(d.invoice_unit_price, 2),
# #                     'Price_Diff': round(d.price_diff, 2),
# #                     'Price_Variance_%': round(d.price_variance_pct, 2),
# #                     'PO_Total': round(d.po_total, 2),
# #                     'Invoice_Total': round(d.invoice_total, 2),
# #                     'Total_Diff': round(d.total_diff, 2),
# #                     'Type': d.status,
# #                     'Severity': self._calculate_severity(d)
# #                 })
            
# #             discrepancy_df = pd.DataFrame(discrepancy_data)
# #             discrepancy_df.to_excel(writer, sheet_name='Discrepancies', index=False)
        
# #         return str(output_path)
    
# #     def generate_html_report(self, comparison: DocumentComparison, filename: str = "comparison_report.html") -> str:
# #         html_content = f"""
# # <!DOCTYPE html>
# # <html>
# # <head>
# #     <title>PO vs Invoice Comparison Report</title>
# #     <style>
# #         body {{ font-family: Arial, sans-serif; margin: 20px; }}
# #         h1 {{ color: #333; }}
# #         .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
# #         table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
# #         th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
# #         th {{ background-color: #4CAF50; color: white; }}
# #         tr:nth-child(even) {{ background-color: #f2f2f2; }}
# #         .critical {{ background-color: #ffcccc; }}
# #         .warning {{ background-color: #ffffcc; }}
# #         .info {{ background-color: #ccf2ff; }}
# #     </style>
# # </head>
# # <body>
# #     <h1>Purchase Order vs Invoice Comparison Report</h1>
    
# #     <div class="summary">
# #         <h2>Comparison Summary</h2>
# #         <p><strong>PO ID:</strong> {comparison.po_doc_id}</p>
# #         <p><strong>Invoice ID:</strong> {comparison.invoice_doc_id}</p>
# #         <p><strong>Total Items in PO:</strong> {comparison.total_items_po}</p>
# #         <p><strong>Total Items in Invoice:</strong> {comparison.total_items_invoice}</p>
# #         <p><strong>Matching Items:</strong> {comparison.matching_items}</p>
# #         <p><strong>Items with Discrepancies:</strong> {comparison.discrepant_items}</p>
# #         <p><strong>PO Total Value:</strong> ${comparison.po_total:.2f}</p>
# #         <p><strong>Invoice Total Value:</strong> ${comparison.invoice_total:.2f}</p>
# #         <p><strong>Difference:</strong> ${comparison.grand_total_diff:.2f} ({comparison.grand_total_variance_pct:.2f}%)</p>
# #     </div>
    
# #     <h2>Discrepancies Found</h2>
# #     <table>
# #         <tr>
# #             <th>Item</th>
# #             <th>Description</th>
# #             <th>Quantity (PO)</th>
# #             <th>Quantity (Invoice)</th>
# #             <th>Unit Price (PO)</th>
# #             <th>Unit Price (Invoice)</th>
# #             <th>Total (PO)</th>
# #             <th>Total (Invoice)</th>
# #             <th>Type</th>
# #             <th>Severity</th>
# #         </tr>
# # """
        
# #         for d in comparison.discrepancies:
# #             severity = self._calculate_severity(d)
# #             severity_class = 'critical' if severity == 'CRITICAL' else 'warning' if severity == 'HIGH' else 'info'
            
# #             html_content += f"""
# #         <tr class="{severity_class}">
# #             <td>{d.item_no}</td>
# #             <td>{d.description}</td>
# #             <td>{d.po_quantity}</td>
# #             <td>{d.invoice_quantity}</td>
# #             <td>${d.po_unit_price:.2f}</td>
# #             <td>${d.invoice_unit_price:.2f}</td>
# #             <td>${d.po_total:.2f}</td>
# #             <td>${d.invoice_total:.2f}</td>
# #             <td>{d.status}</td>
# #             <td>{severity}</td>
# #         </tr>
# # """
        
# #         html_content += """
# #     </table>
# # </body>
# # </html>
# # """
        
# #         output_path = self.output_dir / filename
# #         with open(output_path, 'w') as f:
# #             f.write(html_content)
        
# #         return str(output_path)
    
# #     def _calculate_severity(self, discrepancy: ItemDiscrepancy) -> str:
# #         if abs(discrepancy.quantity_variance_pct) > 50 or abs(discrepancy.price_variance_pct) > 50:
# #             return "CRITICAL"
# #         elif abs(discrepancy.quantity_variance_pct) > 10 or abs(discrepancy.price_variance_pct) > 10:
# #             return "HIGH"
# #         elif "MISSING" in discrepancy.status or "EXTRA" in discrepancy.status:
# #             return "HIGH"
# #         else:
# #             return "MEDIUM"
    
# #     def generate_detailed_analysis_json(self, po_doc: ExtractedDocument, pi_doc: ExtractedDocument, comparison: DocumentComparison, filename: str = "detailed_analysis.json") -> str:
# #         detailed_analysis = DetailedDiscrepancyAnalyzer.analyze_all_items(po_doc, pi_doc, comparison)
# #         alerts = AlertGenerator.generate_alerts(comparison)
        
# #         analysis_report = {
# #             "metadata": {
# #                 "po_id": comparison.po_doc_id,
# #                 "invoice_id": comparison.invoice_doc_id,
# #                 "generated_at": datetime.now().isoformat(),
# #                 "total_items_po": comparison.total_items_po,
# #                 "total_items_invoice": comparison.total_items_invoice,
# #                 "matching_items": comparison.matching_items,
# #                 "discrepant_items": comparison.discrepant_items
# #             },
# #             "quantity_analysis": detailed_analysis["quantity_analysis"],
# #             "price_analysis": detailed_analysis["price_analysis"],
# #             "totals_analysis": detailed_analysis["totals_analysis"],
# #             "mismatches_summary": detailed_analysis["mismatches_summary"],
# #             "alerts": alerts
# #         }
        
# #         output_path = self.output_dir / filename
# #         with open(output_path, 'w') as f:
# #             json.dump(analysis_report, f, indent=2)
        
# #         return str(output_path)
    
# #     def generate_comprehensive_excel(self, po_doc: ExtractedDocument, pi_doc: ExtractedDocument, comparison: DocumentComparison, filename: str = "comprehensive_analysis.xlsx") -> str:
# #         detailed_analysis = DetailedDiscrepancyAnalyzer.analyze_all_items(po_doc, pi_doc, comparison)
# #         alerts = AlertGenerator.generate_alerts(comparison)
        
# #         output_path = self.output_dir / filename
        
# #         with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
# #             summary_df = pd.DataFrame([{
# #                 'PO_ID': comparison.po_doc_id,
# #                 'Invoice_ID': comparison.invoice_doc_id,
# #                 'Total_Items_PO': comparison.total_items_po,
# #                 'Total_Items_Invoice': comparison.total_items_invoice,
# #                 'Matching_Items': comparison.matching_items,
# #                 'Discrepant_Items': comparison.discrepant_items,
# #                 'PO_Total': round(comparison.po_total, 2),
# #                 'Invoice_Total': round(comparison.invoice_total, 2),
# #                 'Difference': round(comparison.grand_total_diff, 2),
# #                 'Variance_%': round(comparison.grand_total_variance_pct, 2)
# #             }])
# #             summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
# #             qty_df = pd.DataFrame(detailed_analysis["quantity_analysis"])
# #             qty_df.to_excel(writer, sheet_name='Quantity_Analysis', index=False)
            
# #             price_df = pd.DataFrame(detailed_analysis["price_analysis"])
# #             price_df.to_excel(writer, sheet_name='Price_Analysis', index=False)
            
# #             totals_data = [detailed_analysis["totals_analysis"]]
# #             totals_df = pd.DataFrame(totals_data)
# #             totals_df.to_excel(writer, sheet_name='Totals_Summary', index=False)
            
# #             mismatches_df = pd.DataFrame(detailed_analysis["mismatches_summary"])
# #             mismatches_df.to_excel(writer, sheet_name='Mismatches', index=False)
            
# #             alerts_df = pd.DataFrame(alerts)
# #             alerts_df.to_excel(writer, sheet_name='Alerts', index=False)
        
# #         return str(output_path)
    
# #     def generate_alerts_report(self, comparison: DocumentComparison, filename: str = "alerts_report.json") -> str:
# #         alerts = AlertGenerator.generate_alerts(comparison)
        
# #         output_path = self.output_dir / filename
# #         with open(output_path, 'w') as f:
# #             json.dump({"alerts": alerts, "generated_at": datetime.now().isoformat()}, f, indent=2)
        
# #         return str(output_path)


# # def generate_all_reports(comparison: DocumentComparison, output_dir: Path, po_doc: ExtractedDocument = None, pi_doc: ExtractedDocument = None):
# #     generator = ReportGenerator(output_dir)
    
# #     reports = {
# #         'json': generator.generate_json_report(comparison),
# #         'csv': generator.generate_csv_report(comparison),
# #         'excel': generator.generate_excel_report(comparison),
# #         'html': generator.generate_html_report(comparison),
# #         'alerts': generator.generate_alerts_report(comparison)
# #     }
    
# #     if po_doc and pi_doc:
# #         reports['extracted_data'] = StructuredDataExtractor.generate_extraction_json(po_doc, pi_doc, output_dir)
# #         reports['detailed_analysis'] = generator.generate_detailed_analysis_json(po_doc, pi_doc, comparison)
# #         reports['comprehensive_excel'] = generator.generate_comprehensive_excel(po_doc, pi_doc, comparison)
    
# #     return reports
# import json
# import csv
# from pathlib import Path
# from typing import Dict, List, Any
# from datetime import datetime
# import pandas as pd

# from src.comparator import DocumentComparison, ItemDiscrepancy, SummaryMetrics
# from src.pdf_extractor import ExtractedDocument

# class EnhancedReportGenerator:
#     """Generate reports in the exact format specified"""

#     def __init__(self, output_dir: Path):
#         self.output_dir = Path(output_dir)
#         self.output_dir.mkdir(parents=True, exist_ok=True)

#     def generate_complete_json_report(
#         self, 
#         comparison: DocumentComparison,
#         filename: str = "discrepancy_report.json"
#     ) -> str:
#         """Generate the complete JSON report with all required sections"""

#         # Section 1: Item-Level Comparison
#         item_level_comparison = []
#         for item in comparison.item_level_comparison:
#             item_level_comparison.append({
#                 "SKU": item.item_no,
#                 "Description": item.description,
#                 "Qty_Ordered": item.po_quantity,
#                 "Qty_Invoiced": item.invoice_quantity,
#                 "Unit_Price_Ordered": round(item.po_unit_price, 2),
#                 "Unit_Price_Invoiced": round(item.invoice_unit_price, 2),
#                 "Discount_Pct_Ordered": round(item.po_discount_pct, 2),
#                 "Discount_Pct_Invoiced": round(item.invoice_discount_pct, 2),
#                 "Line_Total_Ordered": round(item.po_line_total, 2),
#                 "Line_Total_Invoiced": round(item.invoice_line_total, 2),
#                 "Quantity_Discrepancy": item.quantity_discrepancy,
#                 "Price_Discrepancy": item.price_discrepancy,
#                 "Total_Discrepancy": item.total_discrepancy,
#                 "Severity": item.severity,
#                 "Reason": item.reason
#             })

#         # Section 2: Summary Metrics
#         metrics = comparison.summary_metrics
#         summary_metrics = {
#             "Subtotal": {
#                 "po": round(metrics.subtotal_po, 2),
#                 "pi": round(metrics.subtotal_pi, 2),
#                 "difference": round(metrics.subtotal_difference, 2)
#             },
#             "Discounts": {
#                 "po": round(metrics.discounts_po, 2),
#                 "pi": round(metrics.discounts_pi, 2),
#                 "difference": round(metrics.discounts_difference, 2)
#             },
#             "Taxable_Amount": {
#                 "po": round(metrics.taxable_amount_po, 2),
#                 "pi": round(metrics.taxable_amount_pi, 2),
#                 "difference": round(metrics.taxable_difference, 2)
#             },
#             "Tax": {
#                 "po": round(metrics.tax_po, 2),
#                 "pi": round(metrics.tax_pi, 2),
#                 "difference": round(metrics.tax_difference, 2)
#             },
#             "Grand_Total": {
#                 "po": round(metrics.grand_total_po, 2),
#                 "pi": round(metrics.grand_total_pi, 2),
#                 "difference": round(metrics.grand_total_difference, 2)
#             }
#         }

#         # Section 3: Products with Mismatches
#         products_with_mismatches = comparison.products_with_mismatches

#         # Section 4: Bonus Alerts
#         bonus_alerts = self._generate_bonus_alerts(comparison)

#         # Complete report structure
#         report = {
#             "discrepancy_report": {
#                 "metadata": {
#                     "po_id": comparison.po_doc_id,
#                     "invoice_id": comparison.invoice_doc_id,
#                     "generated_at": datetime.now().isoformat(),
#                     "total_items_compared": len(comparison.item_level_comparison)
#                 },
#                 "item_level_comparison": item_level_comparison,
#                 "summary_metrics": summary_metrics,
#                 "products_with_mismatches": products_with_mismatches,
#                 "total_quantities_and_values": {
#                     "total_quantity_ordered": comparison.total_quantity_ordered,
#                     "total_quantity_invoiced": comparison.total_quantity_invoiced,
#                     "total_value_ordered": round(comparison.total_value_ordered, 2),
#                     "total_value_invoiced": round(comparison.total_value_invoiced, 2)
#                 }
#             },
#             "bonus_alerts": bonus_alerts
#         }

#         # Write to file
#         output_path = self.output_dir / filename
#         with open(output_path, 'w') as f:
#             json.dump(report, f, indent=2)

#         return str(output_path)

#     def _generate_bonus_alerts(self, comparison: DocumentComparison) -> List[str]:
#         """Generate automated alerts and recommendations"""
#         alerts = []

#         metrics = comparison.summary_metrics

#         # Alert 1: High-value discrepancy
#         total_diff = metrics.grand_total_difference
#         variance_pct = abs(total_diff / metrics.grand_total_po * 100) if metrics.grand_total_po > 0 else 0

#         if abs(total_diff) > 100 or variance_pct > 3:
#             alerts.append(
#                 f"ALERT: Significant total value discrepancy detected. "
#                 f"PO Total: ${metrics.grand_total_po:,.2f} vs. "
#                 f"PI Total: ${metrics.grand_total_pi:,.2f}. "
#                 f"Difference: {'+' if total_diff > 0 else ''}${total_diff:,.2f}. "
#                 f"Please review."
#             )

#         # Alert 2: Item-specific alerts
#         for item in comparison.item_level_comparison:
#             if not item.price_discrepancy and not item.quantity_discrepancy:
#                 continue

#             if item.severity == "CRITICAL" or abs(item.price_diff) > 10:
#                 price_change = "increase" if item.price_diff > 0 else "decrease"
#                 alerts.append(
#                     f"ALERT: SKU {item.item_no} '{item.description}' has a price {price_change} "
#                     f"of ${abs(item.price_diff):.2f} per unit "
#                     f"(from ${item.po_unit_price:.2f} to ${item.invoice_unit_price:.2f}). "
#                     f"This changes the line total by ${abs(item.total_diff):.2f}."
#                 )

#         # Alert 3: Calculation error warnings
#         for item in comparison.item_level_comparison:
#             # Check for suspicious long decimals in discount amounts
#             if item.invoice_discount_amount > 0:
#                 decimal_str = str(item.invoice_discount_amount)
#                 if '.' in decimal_str and len(decimal_str.split('.')[1]) > 10:
#                     alerts.append(
#                         f"WARNING: The Proforma Invoice for SKU {item.item_no} '{item.description}' "
#                         f"shows an extremely long decimal for Discount Amount ({item.invoice_discount_amount}). "
#                         f"This may indicate a rounding or calculation error in the invoice system."
#                     )

#         # Alert 4: Recommendations
#         critical_items = [
#             item for item in comparison.item_level_comparison 
#             if item.severity in ["CRITICAL", "HIGH"] and item.price_discrepancy
#         ]

#         if critical_items:
#             sku_list = ", ".join([item.item_no for item in critical_items[:5]])
#             alerts.append(
#                 f"RECOMMENDATION: Contact the supplier to clarify pricing discrepancies "
#                 f"for SKUs {sku_list} before payment. "
#                 f"Verify if the higher prices are intentional or errors."
#             )

#         # Alert 5: Missing items
#         missing_items = [
#             item for item in comparison.item_level_comparison 
#             if item.status == "MISSING_FROM_INVOICE"
#         ]

#         if missing_items:
#             alerts.append(
#                 f"CRITICAL: {len(missing_items)} item(s) from the Purchase Order are missing "
#                 f"in the Invoice. Review delivery documentation."
#             )

#         return alerts

#     def generate_csv_report(
#         self, 
#         comparison: DocumentComparison,
#         filename: str = "item_comparison.csv"
#     ) -> str:
#         """Generate CSV report for Excel analysis"""

#         output_path = self.output_dir / filename

#         with open(output_path, 'w', newline='') as f:
#             fieldnames = [
#                 'SKU', 'Description',
#                 'Qty_Ordered', 'Qty_Invoiced', 'Qty_Diff',
#                 'Unit_Price_Ordered', 'Unit_Price_Invoiced', 'Price_Diff',
#                 'Discount_Pct_Ordered', 'Discount_Pct_Invoiced',
#                 'Line_Total_Ordered', 'Line_Total_Invoiced', 'Total_Diff',
#                 'Quantity_Discrepancy', 'Price_Discrepancy', 'Total_Discrepancy',
#                 'Severity', 'Reason'
#             ]

#             writer = csv.DictWriter(f, fieldnames=fieldnames)
#             writer.writeheader()

#             for item in comparison.item_level_comparison:
#                 writer.writerow({
#                     'SKU': item.item_no,
#                     'Description': item.description,
#                     'Qty_Ordered': item.po_quantity,
#                     'Qty_Invoiced': item.invoice_quantity,
#                     'Qty_Diff': round(item.quantity_diff, 2),
#                     'Unit_Price_Ordered': round(item.po_unit_price, 2),
#                     'Unit_Price_Invoiced': round(item.invoice_unit_price, 2),
#                     'Price_Diff': round(item.price_diff, 2),
#                     'Discount_Pct_Ordered': round(item.po_discount_pct, 2),
#                     'Discount_Pct_Invoiced': round(item.invoice_discount_pct, 2),
#                     'Line_Total_Ordered': round(item.po_line_total, 2),
#                     'Line_Total_Invoiced': round(item.invoice_line_total, 2),
#                     'Total_Diff': round(item.total_diff, 2),
#                     'Quantity_Discrepancy': item.quantity_discrepancy,
#                     'Price_Discrepancy': item.price_discrepancy,
#                     'Total_Discrepancy': item.total_discrepancy,
#                     'Severity': item.severity,
#                     'Reason': item.reason
#                 })

#         return str(output_path)

#     def generate_excel_report(
#         self,
#         comparison: DocumentComparison,
#         filename: str = "detailed_comparison.xlsx"
#     ) -> str:
#         """Generate Excel report with multiple sheets"""

#         output_path = self.output_dir / filename

#         with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
#             # Sheet 1: Summary
#             metrics = comparison.summary_metrics
#             summary_data = {
#                 'Metric': ['Subtotal', 'Discounts', 'Taxable Amount', 'Tax', 'Grand Total'],
#                 'Purchase_Order': [
#                     round(metrics.subtotal_po, 2),
#                     round(metrics.discounts_po, 2),
#                     round(metrics.taxable_amount_po, 2),
#                     round(metrics.tax_po, 2),
#                     round(metrics.grand_total_po, 2)
#                 ],
#                 'Proforma_Invoice': [
#                     round(metrics.subtotal_pi, 2),
#                     round(metrics.discounts_pi, 2),
#                     round(metrics.taxable_amount_pi, 2),
#                     round(metrics.tax_pi, 2),
#                     round(metrics.grand_total_pi, 2)
#                 ],
#                 'Difference': [
#                     round(metrics.subtotal_difference, 2),
#                     round(metrics.discounts_difference, 2),
#                     round(metrics.taxable_difference, 2),
#                     round(metrics.tax_difference, 2),
#                     round(metrics.grand_total_difference, 2)
#                 ]
#             }
#             summary_df = pd.DataFrame(summary_data)
#             summary_df.to_excel(writer, sheet_name='Summary', index=False)

#             # Sheet 2: Item Comparison
#             item_data = []
#             for item in comparison.item_level_comparison:
#                 item_data.append({
#                     'SKU': item.item_no,
#                     'Description': item.description,
#                     'PO_Qty': item.po_quantity,
#                     'Invoice_Qty': item.invoice_quantity,
#                     'Qty_Match': "✓" if not item.quantity_discrepancy else "✗",
#                     'PO_Price': round(item.po_unit_price, 2),
#                     'Invoice_Price': round(item.invoice_unit_price, 2),
#                     'Price_Match': "✓" if not item.price_discrepancy else "✗",
#                     'PO_Total': round(item.po_line_total, 2),
#                     'Invoice_Total': round(item.invoice_line_total, 2),
#                     'Total_Diff': round(item.total_diff, 2),
#                     'Severity': item.severity,
#                     'Status': item.reason
#                 })

#             items_df = pd.DataFrame(item_data)
#             items_df.to_excel(writer, sheet_name='Item Comparison', index=False)

#             # Sheet 3: Discrepancies Only
#             discrepancy_data = [
#                 item_dict for item_dict in item_data 
#                 if item_dict['Severity'] != 'NONE'
#             ]

#             if discrepancy_data:
#                 disc_df = pd.DataFrame(discrepancy_data)
#                 disc_df.to_excel(writer, sheet_name='Discrepancies', index=False)

#         return str(output_path)

# def generate_all_reports(
#     comparison: DocumentComparison,
#     output_dir: Path,
#     po_doc: ExtractedDocument = None,
#     invoice_doc: ExtractedDocument = None
# ) -> Dict[str, str]:
#     """Generate all report formats"""

#     generator = EnhancedReportGenerator(output_dir)

#     reports = {
#         'json': generator.generate_complete_json_report(comparison),
#         'csv': generator.generate_csv_report(comparison),
#         'excel': generator.generate_excel_report(comparison)
#     }

#     return reports
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd

from src.comparator import DocumentComparison, ItemDiscrepancy, SummaryMetrics
from src.pdf_extractor import ExtractedDocument

class EnhancedReportGenerator:
    """Generate reports in the exact format specified"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_complete_json_report(
        self, 
        comparison: DocumentComparison,
        filename: str = "discrepancy_report.json"
    ) -> str:
        """Generate the complete JSON report with all required sections"""

        # Section 1: Item-Level Comparison
        item_level_comparison = []
        for item in comparison.item_level_comparison:
            item_level_comparison.append({
                "SKU": item.item_no,
                "Description": item.description,
                "Qty_Ordered": item.po_quantity,
                "Qty_Invoiced": item.invoice_quantity,
                "Unit_Price_Ordered": round(item.po_unit_price, 2),
                "Unit_Price_Invoiced": round(item.invoice_unit_price, 2),
                "Discount_Pct_Ordered": round(item.po_discount_pct, 2),
                "Discount_Pct_Invoiced": round(item.invoice_discount_pct, 2),
                "Line_Total_Ordered": round(item.po_line_total, 2),
                "Line_Total_Invoiced": round(item.invoice_line_total, 2),
                "Quantity_Discrepancy": item.quantity_discrepancy,
                "Price_Discrepancy": item.price_discrepancy,
                "Total_Discrepancy": item.total_discrepancy,
                "Severity": item.severity,
                "Reason": item.reason
            })

        # Section 2: Summary Metrics
        metrics = comparison.summary_metrics
        summary_metrics = {
            "Subtotal": {
                "po": round(metrics.subtotal_po, 2),
                "pi": round(metrics.subtotal_pi, 2),
                "difference": round(metrics.subtotal_difference, 2)
            },
            "Discounts": {
                "po": round(metrics.discounts_po, 2),
                "pi": round(metrics.discounts_pi, 2),
                "difference": round(metrics.discounts_difference, 2)
            },
            "Taxable_Amount": {
                "po": round(metrics.taxable_amount_po, 2),
                "pi": round(metrics.taxable_amount_pi, 2),
                "difference": round(metrics.taxable_difference, 2)
            },
            "Tax": {
                "po": round(metrics.tax_po, 2),
                "pi": round(metrics.tax_pi, 2),
                "difference": round(metrics.tax_difference, 2)
            },
            "Grand_Total": {
                "po": round(metrics.grand_total_po, 2),
                "pi": round(metrics.grand_total_pi, 2),
                "difference": round(metrics.grand_total_difference, 2)
            }
        }

        # Section 3: Products with Mismatches
        products_with_mismatches = comparison.products_with_mismatches

        # Section 4: Bonus Alerts
        bonus_alerts = self._generate_bonus_alerts(comparison)

        # Complete report structure
        report = {
            "discrepancy_report": {
                "metadata": {
                    "po_id": comparison.po_doc_id,
                    "invoice_id": comparison.invoice_doc_id,
                    "generated_at": datetime.now().isoformat(),
                    "total_items_compared": len(comparison.item_level_comparison)
                },
                "item_level_comparison": item_level_comparison,
                "summary_metrics": summary_metrics,
                "products_with_mismatches": products_with_mismatches,
                "total_quantities_and_values": {
                    "total_quantity_ordered": comparison.total_quantity_ordered,
                    "total_quantity_invoiced": comparison.total_quantity_invoiced,
                    "total_value_ordered": round(comparison.total_value_ordered, 2),
                    "total_value_invoiced": round(comparison.total_value_invoiced, 2)
                }
            },
            "bonus_alerts": bonus_alerts
        }

        # Write to file
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return str(output_path)

    def _generate_bonus_alerts(self, comparison: DocumentComparison) -> List[str]:
        """Generate automated alerts and recommendations"""
        alerts = []

        metrics = comparison.summary_metrics

        # Alert 1: High-value discrepancy
        total_diff = metrics.grand_total_difference
        variance_pct = abs(total_diff / metrics.grand_total_po * 100) if metrics.grand_total_po > 0 else 0

        if abs(total_diff) > 100 or variance_pct > 3:
            alerts.append(
                f"ALERT: Significant total value discrepancy detected. "
                f"PO Total: ${metrics.grand_total_po:,.2f} vs. "
                f"PI Total: ${metrics.grand_total_pi:,.2f}. "
                f"Difference: {'+' if total_diff > 0 else ''}${total_diff:,.2f}. "
                f"Please review."
            )

        # Alert 2: Item-specific alerts
        for item in comparison.item_level_comparison:
            if not item.price_discrepancy and not item.quantity_discrepancy:
                continue

            if item.severity == "CRITICAL" or abs(item.price_diff) > 10:
                price_change = "increase" if item.price_diff > 0 else "decrease"
                alerts.append(
                    f"ALERT: SKU {item.item_no} '{item.description}' has a price {price_change} "
                    f"of ${abs(item.price_diff):.2f} per unit "
                    f"(from ${item.po_unit_price:.2f} to ${item.invoice_unit_price:.2f}). "
                    f"This changes the line total by ${abs(item.total_diff):.2f}."
                )

        # Alert 3: Calculation error warnings
        for item in comparison.item_level_comparison:
            # Check for suspicious long decimals in discount amounts
            if item.invoice_discount_amount > 0:
                decimal_str = str(item.invoice_discount_amount)
                if '.' in decimal_str and len(decimal_str.split('.')[1]) > 10:
                    alerts.append(
                        f"WARNING: The Proforma Invoice for SKU {item.item_no} '{item.description}' "
                        f"shows an extremely long decimal for Discount Amount ({item.invoice_discount_amount}). "
                        f"This may indicate a rounding or calculation error in the invoice system."
                    )

        # Alert 4: Recommendations
        critical_items = [
            item for item in comparison.item_level_comparison 
            if item.severity in ["CRITICAL", "HIGH"] and item.price_discrepancy
        ]

        if critical_items:
            sku_list = ", ".join([item.item_no for item in critical_items[:5]])
            alerts.append(
                f"RECOMMENDATION: Contact the supplier to clarify pricing discrepancies "
                f"for SKUs {sku_list} before payment. "
                f"Verify if the higher prices are intentional or errors."
            )

        # Alert 5: Missing items
        missing_items = [
            item for item in comparison.item_level_comparison 
            if item.status == "MISSING_FROM_INVOICE"
        ]

        if missing_items:
            alerts.append(
                f"CRITICAL: {len(missing_items)} item(s) from the Purchase Order are missing "
                f"in the Invoice. Review delivery documentation."
            )

        return alerts

    def generate_csv_report(
        self, 
        comparison: DocumentComparison,
        filename: str = "item_comparison.csv"
    ) -> str:
        """Generate CSV report for Excel analysis"""

        output_path = self.output_dir / filename

        with open(output_path, 'w', newline='') as f:
            fieldnames = [
                'SKU', 'Description',
                'Qty_Ordered', 'Qty_Invoiced', 'Qty_Diff',
                'Unit_Price_Ordered', 'Unit_Price_Invoiced', 'Price_Diff',
                'Discount_Pct_Ordered', 'Discount_Pct_Invoiced',
                'Line_Total_Ordered', 'Line_Total_Invoiced', 'Total_Diff',
                'Quantity_Discrepancy', 'Price_Discrepancy', 'Total_Discrepancy',
                'Severity', 'Reason'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in comparison.item_level_comparison:
                writer.writerow({
                    'SKU': item.item_no,
                    'Description': item.description,
                    'Qty_Ordered': item.po_quantity,
                    'Qty_Invoiced': item.invoice_quantity,
                    'Qty_Diff': round(item.quantity_diff, 2),
                    'Unit_Price_Ordered': round(item.po_unit_price, 2),
                    'Unit_Price_Invoiced': round(item.invoice_unit_price, 2),
                    'Price_Diff': round(item.price_diff, 2),
                    'Discount_Pct_Ordered': round(item.po_discount_pct, 2),
                    'Discount_Pct_Invoiced': round(item.invoice_discount_pct, 2),
                    'Line_Total_Ordered': round(item.po_line_total, 2),
                    'Line_Total_Invoiced': round(item.invoice_line_total, 2),
                    'Total_Diff': round(item.total_diff, 2),
                    'Quantity_Discrepancy': item.quantity_discrepancy,
                    'Price_Discrepancy': item.price_discrepancy,
                    'Total_Discrepancy': item.total_discrepancy,
                    'Severity': item.severity,
                    'Reason': item.reason
                })

        return str(output_path)

    def generate_excel_report(
        self,
        comparison: DocumentComparison,
        filename: str = "detailed_comparison.xlsx"
    ) -> str:
        """Generate Excel report with multiple sheets"""

        output_path = self.output_dir / filename

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary
            metrics = comparison.summary_metrics
            summary_data = {
                'Metric': ['Subtotal', 'Discounts', 'Taxable Amount', 'Tax', 'Grand Total'],
                'Purchase_Order': [
                    round(metrics.subtotal_po, 2),
                    round(metrics.discounts_po, 2),
                    round(metrics.taxable_amount_po, 2),
                    round(metrics.tax_po, 2),
                    round(metrics.grand_total_po, 2)
                ],
                'Proforma_Invoice': [
                    round(metrics.subtotal_pi, 2),
                    round(metrics.discounts_pi, 2),
                    round(metrics.taxable_amount_pi, 2),
                    round(metrics.tax_pi, 2),
                    round(metrics.grand_total_pi, 2)
                ],
                'Difference': [
                    round(metrics.subtotal_difference, 2),
                    round(metrics.discounts_difference, 2),
                    round(metrics.taxable_difference, 2),
                    round(metrics.tax_difference, 2),
                    round(metrics.grand_total_difference, 2)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Sheet 2: Item Comparison
            item_data = []
            for item in comparison.item_level_comparison:
                item_data.append({
                    'SKU': item.item_no,
                    'Description': item.description,
                    'PO_Qty': item.po_quantity,
                    'Invoice_Qty': item.invoice_quantity,
                    'Qty_Match': "✓" if not item.quantity_discrepancy else "✗",
                    'PO_Price': round(item.po_unit_price, 2),
                    'Invoice_Price': round(item.invoice_unit_price, 2),
                    'Price_Match': "✓" if not item.price_discrepancy else "✗",
                    'PO_Total': round(item.po_line_total, 2),
                    'Invoice_Total': round(item.invoice_line_total, 2),
                    'Total_Diff': round(item.total_diff, 2),
                    'Severity': item.severity,
                    'Status': item.reason
                })

            items_df = pd.DataFrame(item_data)
            items_df.to_excel(writer, sheet_name='Item Comparison', index=False)

            # Sheet 3: Discrepancies Only
            discrepancy_data = [
                item_dict for item_dict in item_data 
                if item_dict['Severity'] != 'NONE'
            ]

            if discrepancy_data:
                disc_df = pd.DataFrame(discrepancy_data)
                disc_df.to_excel(writer, sheet_name='Discrepancies', index=False)

        return str(output_path)

def generate_all_reports(
    comparison: DocumentComparison,
    output_dir: Path,
    po_doc: ExtractedDocument = None,
    invoice_doc: ExtractedDocument = None
) -> Dict[str, str]:
    """Generate all report formats"""

    generator = EnhancedReportGenerator(output_dir)

    reports = {
        'json': generator.generate_complete_json_report(comparison),
        'csv': generator.generate_csv_report(comparison),
        'excel': generator.generate_excel_report(comparison)
    }

    return reports
