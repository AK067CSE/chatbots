# # # from dataclasses import dataclass, asdict
# # # from typing import Dict, List, Tuple
# # # from src.pdf_extractor import ExtractedDocument, LineItem
# # # import json


# # # @dataclass
# # # class ItemDiscrepancy:
# # #     item_no: str
# # #     description: str
# # #     po_quantity: float
# # #     invoice_quantity: float
# # #     quantity_diff: float
# # #     quantity_variance_pct: float
# # #     po_unit_price: float
# # #     invoice_unit_price: float
# # #     price_diff: float
# # #     price_variance_pct: float
# # #     po_total: float
# # #     invoice_total: float
# # #     total_diff: float
# # #     status: str


# # # @dataclass
# # # class DocumentComparison:
# # #     po_doc_id: str
# # #     invoice_doc_id: str
# # #     total_items_po: int
# # #     total_items_invoice: int
# # #     matching_items: int
# # #     discrepant_items: int
# # #     po_subtotal: float
# # #     invoice_subtotal: float
# # #     subtotal_diff: float
# # #     subtotal_variance_pct: float
# # #     po_total: float
# # #     invoice_total: float
# # #     grand_total_diff: float
# # #     grand_total_variance_pct: float
# # #     discrepancies: List[ItemDiscrepancy]
# # #     summary: str


# # # class DocumentComparator:
# # #     def __init__(self, quantity_tolerance: float = 0.0, price_tolerance: float = 0.0):
# # #         self.quantity_tolerance = quantity_tolerance
# # #         self.price_tolerance = price_tolerance
    
# # #     def compare(self, po_doc: ExtractedDocument, invoice_doc: ExtractedDocument) -> DocumentComparison:
# # #         discrepancies = self._compare_items(po_doc.items, invoice_doc.items)
        
# # #         subtotal_diff = po_doc.subtotal - invoice_doc.subtotal
# # #         subtotal_variance = (subtotal_diff / po_doc.subtotal * 100) if po_doc.subtotal > 0 else 0
        
# # #         total_diff = po_doc.total - invoice_doc.total
# # #         total_variance = (total_diff / po_doc.total * 100) if po_doc.total > 0 else 0
        
# # #         summary = self._generate_summary(discrepancies, subtotal_diff, total_diff)
        
# # #         return DocumentComparison(
# # #             po_doc_id=po_doc.metadata.document_id,
# # #             invoice_doc_id=invoice_doc.metadata.document_id,
# # #             total_items_po=len(po_doc.items),
# # #             total_items_invoice=len(invoice_doc.items),
# # #             matching_items=len(po_doc.items) - len(discrepancies),
# # #             discrepant_items=len(discrepancies),
# # #             po_subtotal=po_doc.subtotal,
# # #             invoice_subtotal=invoice_doc.subtotal,
# # #             subtotal_diff=subtotal_diff,
# # #             subtotal_variance_pct=subtotal_variance,
# # #             po_total=po_doc.total,
# # #             invoice_total=invoice_doc.total,
# # #             grand_total_diff=total_diff,
# # #             grand_total_variance_pct=total_variance,
# # #             discrepancies=discrepancies,
# # #             summary=summary
# # #         )
    
# # #     def _compare_items(self, po_items: List[LineItem], invoice_items: List[LineItem]) -> List[ItemDiscrepancy]:
# # #         discrepancies = []
        
# # #         invoice_map = {item.description.lower(): item for item in invoice_items}
        
# # #         for po_item in po_items:
# # #             invoice_item = invoice_map.get(po_item.description.lower())
            
# # #             if not invoice_item:
# # #                 discrepancies.append(ItemDiscrepancy(
# # #                     item_no=po_item.item_no,
# # #                     description=po_item.description,
# # #                     po_quantity=po_item.quantity,
# # #                     invoice_quantity=0,
# # #                     quantity_diff=po_item.quantity,
# # #                     quantity_variance_pct=100.0,
# # #                     po_unit_price=po_item.unit_price,
# # #                     invoice_unit_price=0,
# # #                     price_diff=po_item.unit_price,
# # #                     price_variance_pct=100.0,
# # #                     po_total=po_item.total_price,
# # #                     invoice_total=0,
# # #                     total_diff=po_item.total_price,
# # #                     status="MISSING_FROM_INVOICE"
# # #                 ))
# # #                 continue
            
# # #             qty_diff = po_item.quantity - invoice_item.quantity
# # #             qty_variance = (qty_diff / po_item.quantity * 100) if po_item.quantity > 0 else 0
            
# # #             price_diff = po_item.unit_price - invoice_item.unit_price
# # #             price_variance = (price_diff / po_item.unit_price * 100) if po_item.unit_price > 0 else 0
            
# # #             total_diff = po_item.total_price - invoice_item.total_price
            
# # #             if abs(qty_variance) > self.quantity_tolerance or abs(price_variance) > self.price_tolerance:
# # #                 status = self._determine_status(qty_variance, price_variance)
                
# # #                 discrepancies.append(ItemDiscrepancy(
# # #                     item_no=po_item.item_no,
# # #                     description=po_item.description,
# # #                     po_quantity=po_item.quantity,
# # #                     invoice_quantity=invoice_item.quantity,
# # #                     quantity_diff=qty_diff,
# # #                     quantity_variance_pct=qty_variance,
# # #                     po_unit_price=po_item.unit_price,
# # #                     invoice_unit_price=invoice_item.unit_price,
# # #                     price_diff=price_diff,
# # #                     price_variance_pct=price_variance,
# # #                     po_total=po_item.total_price,
# # #                     invoice_total=invoice_item.total_price,
# # #                     total_diff=total_diff,
# # #                     status=status
# # #                 ))
        
# # #         for invoice_item in invoice_items:
# # #             if invoice_item.description.lower() not in invoice_map:
# # #                 discrepancies.append(ItemDiscrepancy(
# # #                     item_no="N/A",
# # #                     description=invoice_item.description,
# # #                     po_quantity=0,
# # #                     invoice_quantity=invoice_item.quantity,
# # #                     quantity_diff=-invoice_item.quantity,
# # #                     quantity_variance_pct=-100.0,
# # #                     po_unit_price=0,
# # #                     invoice_unit_price=invoice_item.unit_price,
# # #                     price_diff=-invoice_item.unit_price,
# # #                     price_variance_pct=-100.0,
# # #                     po_total=0,
# # #                     invoice_total=invoice_item.total_price,
# # #                     total_diff=-invoice_item.total_price,
# # #                     status="EXTRA_IN_INVOICE"
# # #                 ))
        
# # #         return discrepancies
    
# # #     def _determine_status(self, qty_variance: float, price_variance: float) -> str:
# # #         if qty_variance != 0 and price_variance != 0:
# # #             return "QUANTITY_AND_PRICE_MISMATCH"
# # #         elif qty_variance != 0:
# # #             return "QUANTITY_MISMATCH"
# # #         elif price_variance != 0:
# # #             return "PRICE_MISMATCH"
# # #         else:
# # #             return "VERIFIED"
    
# # #     def _generate_summary(self, discrepancies: List[ItemDiscrepancy], subtotal_diff: float, total_diff: float) -> str:
# # #         qty_mismatches = [d for d in discrepancies if "QUANTITY" in d.status]
# # #         price_mismatches = [d for d in discrepancies if "PRICE" in d.status]
# # #         missing_items = [d for d in discrepancies if d.status == "MISSING_FROM_INVOICE"]
# # #         extra_items = [d for d in discrepancies if d.status == "EXTRA_IN_INVOICE"]
        
# # #         summary = f"""
# # # COMPARISON SUMMARY:
# # # - Total Discrepancies Found: {len(discrepancies)}
# # # - Quantity Mismatches: {len(qty_mismatches)}
# # # - Price Mismatches: {len(price_mismatches)}
# # # - Items Missing from Invoice: {len(missing_items)}
# # # - Extra Items in Invoice: {len(extra_items)}
# # # - Subtotal Difference: ${subtotal_diff:.2f}
# # # - Grand Total Difference: ${total_diff:.2f}
# # # """
# # #         return summary.strip()


# # # def compare_po_with_invoice(po_doc: ExtractedDocument, invoice_doc: ExtractedDocument) -> DocumentComparison:
# # #     comparator = DocumentComparator()
# # #     return comparator.compare(po_doc, invoice_doc)


# # # def export_comparison_report(comparison: DocumentComparison, output_path: str):
# # #     report = {
# # #         'metadata': {
# # #             'po_doc_id': comparison.po_doc_id,
# # #             'invoice_doc_id': comparison.invoice_doc_id,
# # #             'comparison_timestamp': json.dumps(str(__import__('datetime').datetime.now()), default=str)
# # #         },
# # #         'summary': {
# # #             'total_items_po': comparison.total_items_po,
# # #             'total_items_invoice': comparison.total_items_invoice,
# # #             'matching_items': comparison.matching_items,
# # #             'discrepant_items': comparison.discrepant_items,
# # #             'po_subtotal': comparison.po_subtotal,
# # #             'invoice_subtotal': comparison.invoice_subtotal,
# # #             'subtotal_variance_pct': comparison.subtotal_variance_pct,
# # #             'po_total': comparison.po_total,
# # #             'invoice_total': comparison.invoice_total,
# # #             'grand_total_variance_pct': comparison.grand_total_variance_pct,
# # #         },
# # #         'discrepancies': [asdict(d) for d in comparison.discrepancies],
# # #         'summary_text': comparison.summary
# # #     }
    
# # #     with open(output_path, 'w') as f:
# # #         json.dump(report, f, indent=2)
    
# # #     return report
# # from dataclasses import dataclass, asdict
# # from typing import Dict, List, Optional
# # from src.pdf_extractor import ExtractedDocument, LineItem
# # import json


# # @dataclass
# # class ItemDiscrepancy:
# #     item_no: str
# #     description: str
# #     po_quantity: float
# #     invoice_quantity: float
# #     quantity_diff: float
# #     quantity_variance_pct: float
# #     po_unit_price: float
# #     invoice_unit_price: float
# #     price_diff: float
# #     price_variance_pct: float
# #     po_total: float
# #     invoice_total: float
# #     total_diff: float
# #     status: str


# # @dataclass
# # class DocumentComparison:
# #     po_doc_id: str
# #     invoice_doc_id: str
# #     total_items_po: int
# #     total_items_invoice: int
# #     matching_items: int
# #     discrepant_items: int
# #     po_subtotal: float
# #     invoice_subtotal: float
# #     subtotal_diff: float
# #     subtotal_variance_pct: float
# #     po_total: float
# #     invoice_total: float
# #     grand_total_diff: float
# #     grand_total_variance_pct: float
# #     discrepancies: List[ItemDiscrepancy]
# #     summary: str


# # class DocumentComparator:
# #     def __init__(self, quantity_tolerance: float = 0.0, price_tolerance: float = 0.0):
# #         self.quantity_tolerance = quantity_tolerance
# #         self.price_tolerance = price_tolerance

# #     def compare(self, po_doc: ExtractedDocument, invoice_doc: ExtractedDocument) -> DocumentComparison:
# #         discrepancies = self._compare_items(po_doc.items, invoice_doc.items)

# #         # ✅ CORRECTED: Use invoice - PO for consistency with alerts & downstream expectations
# #         subtotal_diff = invoice_doc.subtotal - po_doc.subtotal
# #         subtotal_variance = (
# #             (subtotal_diff / po_doc.subtotal * 100) if abs(po_doc.subtotal) > 1e-6 else 0.0
# #         )

# #         total_diff = invoice_doc.total - po_doc.total
# #         total_variance = (
# #             (total_diff / po_doc.total * 100) if abs(po_doc.total) > 1e-6 else 0.0
# #         )

# #         summary = self._generate_summary(discrepancies, subtotal_diff, total_diff)

# #         # Compute matching items correctly
# #         missing_count = sum(1 for d in discrepancies if d.status == "MISSING_FROM_INVOICE")
# #         extra_count = sum(1 for d in discrepancies if d.status == "EXTRA_IN_INVOICE")
# #         mismatch_count = len(discrepancies) - missing_count - extra_count
# #         matching_items = len(po_doc.items) - missing_count - mismatch_count

# #         return DocumentComparison(
# #             po_doc_id=po_doc.metadata.document_id,
# #             invoice_doc_id=invoice_doc.metadata.document_id,
# #             total_items_po=len(po_doc.items),
# #             total_items_invoice=len(invoice_doc.items),
# #             matching_items=matching_items,
# #             discrepant_items=len(discrepancies),
# #             po_subtotal=po_doc.subtotal,
# #             invoice_subtotal=invoice_doc.subtotal,
# #             subtotal_diff=subtotal_diff,
# #             subtotal_variance_pct=subtotal_variance,
# #             po_total=po_doc.total,
# #             invoice_total=invoice_doc.total,
# #             grand_total_diff=total_diff,
# #             grand_total_variance_pct=total_variance,
# #             discrepancies=discrepancies,
# #             summary=summary
# #         )

# #     def _normalize_key(self, s: str) -> str:
# #         """Normalize SKU/description for robust matching."""
# #         if not s:
# #             return ""
# #         s = s.strip().upper()
# #         # Remove common separators
# #         for c in "-_ .":
# #             s = s.replace(c, "")
# #         return s

# #     def _compare_items(self, po_items: List[LineItem], invoice_items: List[LineItem]) -> List[ItemDiscrepancy]:
# #         discrepancies = []

# #         # Build maps: prefer SKU; fallback to description if SKU missing/ambiguous
# #         def build_keyed_map(items: List[LineItem]) -> Dict[str, LineItem]:
# #             mapping = {}
# #             for item in items:
# #                 key = self._normalize_key(item.item_no)
# #                 # Fallback to description if SKU is empty or duplicate
# #                 if not key or key in mapping:
# #                     key = self._normalize_key(item.description)
# #                 mapping[key] = item
# #             return mapping

# #         po_map = build_keyed_map(po_items)
# #         inv_map = build_keyed_map(invoice_items)
# #         all_keys = set(po_map.keys()) | set(inv_map.keys())

# #         matched_po_keys = set()
# #         matched_inv_keys = set()

# #         for key in sorted(all_keys):
# #             po_item = po_map.get(key)
# #             inv_item = inv_map.get(key)

# #             # ✅ ROUND before comparison to avoid floating noise
# #             po_qty = round(po_item.quantity, 2) if po_item else 0.0
# #             inv_qty = round(inv_item.quantity, 2) if inv_item else 0.0
# #             po_price = round(po_item.unit_price, 2) if po_item else 0.0
# #             inv_price = round(inv_item.unit_price, 2) if inv_item else 0.0
# #             po_total = round(po_item.total_price, 2) if po_item else 0.0
# #             inv_total = round(inv_item.total_price, 2) if inv_item else 0.0

# #             qty_diff = inv_qty - po_qty
# #             price_diff = inv_price - po_price
# #             total_diff = inv_total - po_total

# #             # ✅ SAFE VARIANCE: avoid division by zero
# #             qty_var = (
# #                 (qty_diff / po_qty * 100) if abs(po_qty) > 1e-6 else (float("inf") if abs(qty_diff) > 1e-6 else 0.0)
# #             )
# #             price_var = (
# #                 (price_diff / po_price * 100) if abs(po_price) > 1e-6 else (float("inf") if abs(price_diff) > 1e-6 else 0.0)
# #             )

# #             status = None
# #             item_no = "N/A"
# #             description = "Unknown"

# #             if po_item and inv_item:
# #                 # Both exist — check for mismatch
# #                 matched_po_keys.add(key)
# #                 matched_inv_keys.add(key)
# #                 item_no = po_item.item_no
# #                 description = po_item.description

# #                 # ✅ Use tolerance in variance check
# #                 qty_mismatch = abs(qty_var) > self.quantity_tolerance
# #                 price_mismatch = abs(price_var) > self.price_tolerance

# #                 if qty_mismatch and price_mismatch:
# #                     status = "QUANTITY_AND_PRICE_MISMATCH"
# #                 elif qty_mismatch:
# #                     status = "QUANTITY_MISMATCH"
# #                 elif price_mismatch:
# #                     status = "PRICE_MISMATCH"
# #                 else:
# #                     continue  # No discrepancy → skip

# #             elif po_item and not inv_item:
# #                 # Missing in invoice
# #                 item_no = po_item.item_no
# #                 description = po_item.description
# #                 matched_po_keys.add(key)
# #                 status = "MISSING_FROM_INVOICE"

# #             elif inv_item and not po_item:
# #                 # Extra in invoice
# #                 item_no = inv_item.item_no
# #                 description = inv_item.description
# #                 matched_inv_keys.add(key)
# #                 status = "EXTRA_IN_INVOICE"

# #             # Append discrepancy
# #             discrepancies.append(
# #                 ItemDiscrepancy(
# #                     item_no=item_no,
# #                     description=description,
# #                     po_quantity=po_qty,
# #                     invoice_quantity=inv_qty,
# #                     quantity_diff=qty_diff,
# #                     quantity_variance_pct=qty_var,
# #                     po_unit_price=po_price,
# #                     invoice_unit_price=inv_price,
# #                     price_diff=price_diff,
# #                     price_variance_pct=price_var,
# #                     po_total=po_total,
# #                     invoice_total=inv_total,
# #                     total_diff=total_diff,
# #                     status=status,
# #                 )
# #             )

# #         # ✅ Extra items: detect invoice items not matched
# #         for key, inv_item in inv_map.items():
# #             if key not in matched_inv_keys:
# #                 inv_qty = round(inv_item.quantity, 2)
# #                 inv_price = round(inv_item.unit_price, 2)
# #                 inv_total = round(inv_item.total_price, 2)
# #                 discrepancies.append(
# #                     ItemDiscrepancy(
# #                         item_no=inv_item.item_no,
# #                         description=inv_item.description,
# #                         po_quantity=0.0,
# #                         invoice_quantity=inv_qty,
# #                         quantity_diff=inv_qty,
# #                         quantity_variance_pct=float("inf"),
# #                         po_unit_price=0.0,
# #                         invoice_unit_price=inv_price,
# #                         price_diff=inv_price,
# #                         price_variance_pct=float("inf"),
# #                         po_total=0.0,
# #                         invoice_total=inv_total,
# #                         total_diff=inv_total,
# #                         status="EXTRA_IN_INVOICE",
# #                     )
# #                 )

# #         return discrepancies

# #     def _determine_status(self, qty_variance: float, price_variance: float) -> str:
# #         # Not used anymore — inline logic is more robust
# #         if qty_variance != 0 and price_variance != 0:
# #             return "QUANTITY_AND_PRICE_MISMATCH"
# #         elif qty_variance != 0:
# #             return "QUANTITY_MISMATCH"
# #         elif price_variance != 0:
# #             return "PRICE_MISMATCH"
# #         else:
# #             return "VERIFIED"

# #     def _generate_summary(self, discrepancies: List[ItemDiscrepancy], subtotal_diff: float, total_diff: float) -> str:
# #         qty_mismatches = [d for d in discrepancies if "QUANTITY" in d.status]
# #         price_mismatches = [d for d in discrepancies if "PRICE" in d.status]
# #         missing_items = [d for d in discrepancies if d.status == "MISSING_FROM_INVOICE"]
# #         extra_items = [d for d in discrepancies if d.status == "EXTRA_IN_INVOICE"]

# #         summary = f"""COMPARISON SUMMARY:
# # - Total Discrepancies Found: {len(discrepancies)}
# # - Quantity Mismatches: {len(qty_mismatches)}
# # - Price Mismatches: {len(price_mismatches)}
# # - Items Missing from Invoice: {len(missing_items)}
# # - Extra Items in Invoice: {len(extra_items)}
# # - Subtotal Difference: ${subtotal_diff:.2f}
# # - Grand Total Difference: ${total_diff:.2f}"""
# #         return summary.strip()


# # def compare_po_with_invoice(po_doc: ExtractedDocument, invoice_doc: ExtractedDocument) -> DocumentComparison:
# #     comparator = DocumentComparator(
# #         quantity_tolerance=0.01,  # Allow 0.01 unit tolerance (e.g., rounding)
# #         price_tolerance=0.01,     # Allow $0.01 price tolerance
# #     )
# #     return comparator.compare(po_doc, invoice_doc)


# # def export_comparison_report(comparison: DocumentComparison, output_path: str):
# #     report = {
# #         "metadata": {
# #             "po_doc_id": comparison.po_doc_id,
# #             "invoice_doc_id": comparison.invoice_doc_id,
# #             "comparison_timestamp": json.dumps(str(__import__("datetime").datetime.now()), default=str),
# #         },
# #         "summary": {
# #             "total_items_po": comparison.total_items_po,
# #             "total_items_invoice": comparison.total_items_invoice,
# #             "matching_items": comparison.matching_items,
# #             "discrepant_items": comparison.discrepant_items,
# #             "po_subtotal": round(comparison.po_subtotal, 2),
# #             "invoice_subtotal": round(comparison.invoice_subtotal, 2),
# #             "subtotal_variance_pct": round(comparison.subtotal_variance_pct, 2),
# #             "po_total": round(comparison.po_total, 2),
# #             "invoice_total": round(comparison.invoice_total, 2),
# #             "grand_total_variance_pct": round(comparison.grand_total_variance_pct, 2),
# #         },
# #         "discrepancies": [asdict(d) for d in comparison.discrepancies],
# #         "summary_text": comparison.summary,
# #     }

# #     with open(output_path, "w") as f:
# #         json.dump(report, f, indent=2)

# #     return report
# from dataclasses import dataclass, asdict
# from typing import Dict, List, Tuple, Optional
# import json

# # Import from enhanced extractor
# from src.pdf_extractor import ExtractedDocument, LineItem

# @dataclass
# class ItemDiscrepancy:
#     """Enhanced discrepancy model with boolean flags"""
#     item_no: str
#     description: str

#     # Purchase Order values
#     po_quantity: float
#     po_unit_price: float
#     po_discount_pct: float
#     po_discount_amount: float
#     po_line_total: float

#     # Invoice values
#     invoice_quantity: float
#     invoice_unit_price: float
#     invoice_discount_pct: float
#     invoice_discount_amount: float
#     invoice_line_total: float

#     # Discrepancy flags (boolean)
#     quantity_discrepancy: bool
#     price_discrepancy: bool
#     total_discrepancy: bool
#     discount_discrepancy: bool = False

#     # Variance details
#     quantity_diff: float = 0.0
#     quantity_variance_pct: float = 0.0
#     price_diff: float = 0.0
#     price_variance_pct: float = 0.0
#     total_diff: float = 0.0
#     discount_diff: float = 0.0

#     # Status and severity
#     status: str = "MATCH"
#     severity: str = "NONE"
#     reason: str = ""

# @dataclass
# class SummaryMetrics:
#     """Summary comparison metrics"""
#     subtotal_po: float
#     subtotal_pi: float
#     subtotal_difference: float

#     discounts_po: float
#     discounts_pi: float
#     discounts_difference: float

#     taxable_amount_po: float
#     taxable_amount_pi: float
#     taxable_difference: float

#     tax_po: float
#     tax_pi: float
#     tax_difference: float

#     grand_total_po: float
#     grand_total_pi: float
#     grand_total_difference: float

# @dataclass
# class DocumentComparison:
#     """Complete comparison result"""
#     po_doc_id: str
#     invoice_doc_id: str

#     # Item counts
#     total_items_po: int
#     total_items_invoice: int
#     matching_items: int
#     discrepant_items: int

#     # Summary metrics
#     summary_metrics: SummaryMetrics

#     # Detailed item comparison
#     item_level_comparison: List[ItemDiscrepancy]

#     # Products with mismatches
#     products_with_mismatches: List[Dict[str, str]]

#     # Total quantities
#     total_quantity_ordered: int
#     total_quantity_invoiced: int

#     # Total values
#     total_value_ordered: float
#     total_value_invoiced: float

#     # Text summary
#     summary_text: str = ""

# class EnhancedDocumentComparator:
#     """Enhanced comparator that generates detailed output"""

#     def __init__(self, quantity_tolerance: float = 0.01, price_tolerance: float = 0.01):
#         self.quantity_tolerance = quantity_tolerance
#         self.price_tolerance = price_tolerance

#     def compare(self, po_doc: ExtractedDocument, invoice_doc: ExtractedDocument) -> DocumentComparison:
#         """Generate comprehensive comparison"""

#         # Create item maps
#         po_items_map = {item.description.lower(): item for item in po_doc.items}
#         invoice_items_map = {item.description.lower(): item for item in invoice_doc.items}

#         # Get all unique items
#         all_items = set(po_items_map.keys()) | set(invoice_items_map.keys())

#         # Compare items
#         item_comparisons = []
#         products_with_mismatches = []
#         matching_count = 0

#         for item_key in sorted(all_items):
#             po_item = po_items_map.get(item_key)
#             invoice_item = invoice_items_map.get(item_key)

#             comparison = self._compare_single_item(po_item, invoice_item, item_key)
#             item_comparisons.append(comparison)

#             # Track matching vs discrepant
#             if comparison.status == "MATCH":
#                 matching_count += 1
#             else:
#                 products_with_mismatches.append({
#                     "SKU": comparison.item_no,
#                     "Description": comparison.description,
#                     "Reason": comparison.reason
#                 })

#         # Calculate summary metrics
#         summary_metrics = self._calculate_summary_metrics(po_doc, invoice_doc)

#         # Calculate totals
#         total_qty_po = sum(item.quantity for item in po_doc.items)
#         total_qty_invoice = sum(item.quantity for item in invoice_doc.items)

#         # Generate text summary
#         summary_text = self._generate_summary_text(
#             len(item_comparisons),
#             matching_count,
#             len(products_with_mismatches),
#             summary_metrics
#         )

#         return DocumentComparison(
#             po_doc_id=po_doc.metadata.document_id,
#             invoice_doc_id=invoice_doc.metadata.document_id,
#             total_items_po=len(po_doc.items),
#             total_items_invoice=len(invoice_doc.items),
#             matching_items=matching_count,
#             discrepant_items=len(products_with_mismatches),
#             summary_metrics=summary_metrics,
#             item_level_comparison=item_comparisons,
#             products_with_mismatches=products_with_mismatches,
#             total_quantity_ordered=int(total_qty_po),
#             total_quantity_invoiced=int(total_qty_invoice),
#             total_value_ordered=po_doc.total,
#             total_value_invoiced=invoice_doc.total,
#             summary_text=summary_text
#         )

#     def _compare_single_item(
#         self, 
#         po_item: Optional[LineItem], 
#         invoice_item: Optional[LineItem],
#         item_key: str
#     ) -> ItemDiscrepancy:
#         """Compare a single line item"""

#         # Handle missing items
#         if not po_item:
#             return ItemDiscrepancy(
#                 item_no=invoice_item.item_no,
#                 description=invoice_item.description,
#                 po_quantity=0,
#                 po_unit_price=0,
#                 po_discount_pct=0,
#                 po_discount_amount=0,
#                 po_line_total=0,
#                 invoice_quantity=invoice_item.quantity,
#                 invoice_unit_price=invoice_item.unit_price,
#                 invoice_discount_pct=invoice_item.discount_pct,
#                 invoice_discount_amount=invoice_item.discount_amount,
#                 invoice_line_total=invoice_item.total_price,
#                 quantity_discrepancy=True,
#                 price_discrepancy=True,
#                 total_discrepancy=True,
#                 status="EXTRA_IN_INVOICE",
#                 severity="HIGH",
#                 reason="Item not in Purchase Order"
#             )

#         if not invoice_item:
#             return ItemDiscrepancy(
#                 item_no=po_item.item_no,
#                 description=po_item.description,
#                 po_quantity=po_item.quantity,
#                 po_unit_price=po_item.unit_price,
#                 po_discount_pct=po_item.discount_pct,
#                 po_discount_amount=po_item.discount_amount,
#                 po_line_total=po_item.total_price,
#                 invoice_quantity=0,
#                 invoice_unit_price=0,
#                 invoice_discount_pct=0,
#                 invoice_discount_amount=0,
#                 invoice_line_total=0,
#                 quantity_discrepancy=True,
#                 price_discrepancy=True,
#                 total_discrepancy=True,
#                 status="MISSING_FROM_INVOICE",
#                 severity="CRITICAL",
#                 reason="Item missing from Invoice"
#             )

#         # Both items exist - compare them
#         qty_diff = invoice_item.quantity - po_item.quantity
#         qty_variance = (qty_diff / po_item.quantity * 100) if po_item.quantity > 0 else 0

#         price_diff = invoice_item.unit_price - po_item.unit_price
#         price_variance = (price_diff / po_item.unit_price * 100) if po_item.unit_price > 0 else 0

#         total_diff = invoice_item.total_price - po_item.total_price
#         discount_diff = invoice_item.discount_amount - po_item.discount_amount

#         # Determine discrepancies (boolean flags)
#         qty_discrepancy = abs(qty_variance) > self.quantity_tolerance
#         price_discrepancy = abs(price_variance) > self.price_tolerance
#         total_discrepancy = abs(total_diff) > 0.01
#         discount_discrepancy = abs(discount_diff) > 0.01 or abs(invoice_item.discount_pct - po_item.discount_pct) > 0.01

#         # Determine status and reason
#         if not qty_discrepancy and not price_discrepancy and not total_discrepancy:
#             status = "MATCH"
#             reason = "Perfect match"
#             severity = "NONE"
#         else:
#             reasons = []
#             if qty_discrepancy:
#                 reasons.append("Quantity mismatch")
#             if price_discrepancy:
#                 reasons.append("Unit price mismatch")
#             if discount_discrepancy:
#                 reasons.append("Discount percentage mismatch leading to different line total")

#             reason = ", ".join(reasons) if reasons else "Line total mismatch"

#             if price_discrepancy:
#                 status = "PRICE_MISMATCH"
#             elif qty_discrepancy:
#                 status = "QUANTITY_MISMATCH"
#             else:
#                 status = "TOTAL_MISMATCH"

#             # Determine severity
#             if abs(qty_variance) > 20 or abs(price_variance) > 20:
#                 severity = "CRITICAL"
#             elif abs(qty_variance) > 10 or abs(price_variance) > 10:
#                 severity = "HIGH"
#             else:
#                 severity = "MEDIUM"

#         return ItemDiscrepancy(
#             item_no=po_item.item_no,
#             description=po_item.description,
#             po_quantity=po_item.quantity,
#             po_unit_price=po_item.unit_price,
#             po_discount_pct=po_item.discount_pct,
#             po_discount_amount=po_item.discount_amount,
#             po_line_total=po_item.total_price,
#             invoice_quantity=invoice_item.quantity,
#             invoice_unit_price=invoice_item.unit_price,
#             invoice_discount_pct=invoice_item.discount_pct,
#             invoice_discount_amount=invoice_item.discount_amount,
#             invoice_line_total=invoice_item.total_price,
#             quantity_discrepancy=qty_discrepancy,
#             price_discrepancy=price_discrepancy,
#             total_discrepancy=total_discrepancy,
#             discount_discrepancy=discount_discrepancy,
#             quantity_diff=qty_diff,
#             quantity_variance_pct=qty_variance,
#             price_diff=price_diff,
#             price_variance_pct=price_variance,
#             total_diff=total_diff,
#             discount_diff=discount_diff,
#             status=status,
#             severity=severity,
#             reason=reason
#         )

#     def _calculate_summary_metrics(
#         self, 
#         po_doc: ExtractedDocument, 
#         invoice_doc: ExtractedDocument
#     ) -> SummaryMetrics:
#         """Calculate summary metrics table"""

#         return SummaryMetrics(
#             subtotal_po=po_doc.subtotal,
#             subtotal_pi=invoice_doc.subtotal,
#             subtotal_difference=invoice_doc.subtotal - po_doc.subtotal,
#             discounts_po=po_doc.total_discount,
#             discounts_pi=invoice_doc.total_discount,
#             discounts_difference=invoice_doc.total_discount - po_doc.total_discount,
#             taxable_amount_po=po_doc.taxable_amount,
#             taxable_amount_pi=invoice_doc.taxable_amount,
#             taxable_difference=invoice_doc.taxable_amount - po_doc.taxable_amount,
#             tax_po=po_doc.tax,
#             tax_pi=invoice_doc.tax,
#             tax_difference=invoice_doc.tax - po_doc.tax,
#             grand_total_po=po_doc.total,
#             grand_total_pi=invoice_doc.total,
#             grand_total_difference=invoice_doc.total - po_doc.total
#         )

#     def _generate_summary_text(
#         self, 
#         total_items: int, 
#         matching: int, 
#         discrepant: int,
#         metrics: SummaryMetrics
#     ) -> str:
#         """Generate human-readable summary"""

#         return f"""
# COMPARISON SUMMARY:
# ==================
# Total Items Compared: {total_items}
# Matching Items: {matching}
# Discrepant Items: {discrepant}

# FINANCIAL SUMMARY:
# -----------------
# Subtotal Difference: ${metrics.subtotal_difference:.2f}
# Discount Difference: ${metrics.discounts_difference:.2f}
# Taxable Amount Difference: ${metrics.taxable_difference:.2f}
# Tax Difference: ${metrics.tax_difference:.2f}
# Grand Total Difference: ${metrics.grand_total_difference:.2f}

# PO Total: ${metrics.grand_total_po:.2f}
# Invoice Total: ${metrics.grand_total_pi:.2f}
# Net Difference: ${metrics.grand_total_difference:.2f}
# """

# def compare_po_with_invoice(
#     po_doc: ExtractedDocument, 
#     invoice_doc: ExtractedDocument
# ) -> DocumentComparison:
#     """Main comparison function"""
#     comparator = EnhancedDocumentComparator()
#     return comparator.compare(po_doc, invoice_doc)
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import json

# Import from enhanced extractor
from src.pdf_extractor import ExtractedDocument, LineItem

@dataclass
class ItemDiscrepancy:
    """Enhanced discrepancy model with boolean flags"""
    item_no: str
    description: str

    # Purchase Order values
    po_quantity: float
    po_unit_price: float
    po_discount_pct: float
    po_discount_amount: float
    po_line_total: float

    # Invoice values
    invoice_quantity: float
    invoice_unit_price: float
    invoice_discount_pct: float
    invoice_discount_amount: float
    invoice_line_total: float

    # Discrepancy flags (boolean)
    quantity_discrepancy: bool
    price_discrepancy: bool
    total_discrepancy: bool
    discount_discrepancy: bool = False

    # Variance details
    quantity_diff: float = 0.0
    quantity_variance_pct: float = 0.0
    price_diff: float = 0.0
    price_variance_pct: float = 0.0
    total_diff: float = 0.0
    discount_diff: float = 0.0

    # Status and severity
    status: str = "MATCH"
    severity: str = "NONE"
    reason: str = ""

@dataclass
class SummaryMetrics:
    """Summary comparison metrics"""
    subtotal_po: float
    subtotal_pi: float
    subtotal_difference: float

    discounts_po: float
    discounts_pi: float
    discounts_difference: float

    taxable_amount_po: float
    taxable_amount_pi: float
    taxable_difference: float

    tax_po: float
    tax_pi: float
    tax_difference: float

    grand_total_po: float
    grand_total_pi: float
    grand_total_difference: float

@dataclass
class DocumentComparison:
    """Complete comparison result"""
    po_doc_id: str
    invoice_doc_id: str

    # Item counts
    total_items_po: int
    total_items_invoice: int
    matching_items: int
    discrepant_items: int

    # Summary metrics
    summary_metrics: SummaryMetrics

    # Detailed item comparison
    item_level_comparison: List[ItemDiscrepancy]

    # Products with mismatches
    products_with_mismatches: List[Dict[str, str]]

    # Total quantities
    total_quantity_ordered: int
    total_quantity_invoiced: int

    # Total values
    total_value_ordered: float
    total_value_invoiced: float

    # Text summary
    summary_text: str = ""

class EnhancedDocumentComparator:
    """Enhanced comparator that generates detailed output"""

    def __init__(self, quantity_tolerance: float = 0.01, price_tolerance: float = 0.01):
        self.quantity_tolerance = quantity_tolerance
        self.price_tolerance = price_tolerance

    def compare(self, po_doc: ExtractedDocument, invoice_doc: ExtractedDocument) -> DocumentComparison:
        """Generate comprehensive comparison"""

        # Create item maps
        po_items_map = {item.description.lower(): item for item in po_doc.items}
        invoice_items_map = {item.description.lower(): item for item in invoice_doc.items}

        # Get all unique items
        all_items = set(po_items_map.keys()) | set(invoice_items_map.keys())

        # Compare items
        item_comparisons = []
        products_with_mismatches = []
        matching_count = 0

        for item_key in sorted(all_items):
            po_item = po_items_map.get(item_key)
            invoice_item = invoice_items_map.get(item_key)

            comparison = self._compare_single_item(po_item, invoice_item, item_key)
            item_comparisons.append(comparison)

            # Track matching vs discrepant
            if comparison.status == "MATCH":
                matching_count += 1
            else:
                products_with_mismatches.append({
                    "SKU": comparison.item_no,
                    "Description": comparison.description,
                    "Reason": comparison.reason
                })

        # Calculate summary metrics
        summary_metrics = self._calculate_summary_metrics(po_doc, invoice_doc)

        # Calculate totals
        total_qty_po = sum(item.quantity for item in po_doc.items)
        total_qty_invoice = sum(item.quantity for item in invoice_doc.items)

        # Generate text summary
        summary_text = self._generate_summary_text(
            len(item_comparisons),
            matching_count,
            len(products_with_mismatches),
            summary_metrics
        )

        return DocumentComparison(
            po_doc_id=po_doc.metadata.document_id,
            invoice_doc_id=invoice_doc.metadata.document_id,
            total_items_po=len(po_doc.items),
            total_items_invoice=len(invoice_doc.items),
            matching_items=matching_count,
            discrepant_items=len(products_with_mismatches),
            summary_metrics=summary_metrics,
            item_level_comparison=item_comparisons,
            products_with_mismatches=products_with_mismatches,
            total_quantity_ordered=int(total_qty_po),
            total_quantity_invoiced=int(total_qty_invoice),
            total_value_ordered=po_doc.total,
            total_value_invoiced=invoice_doc.total,
            summary_text=summary_text
        )

    def _compare_single_item(
        self, 
        po_item: Optional[LineItem], 
        invoice_item: Optional[LineItem],
        item_key: str
    ) -> ItemDiscrepancy:
        """Compare a single line item"""

        # Handle missing items
        if not po_item:
            return ItemDiscrepancy(
                item_no=invoice_item.item_no,
                description=invoice_item.description,
                po_quantity=0,
                po_unit_price=0,
                po_discount_pct=0,
                po_discount_amount=0,
                po_line_total=0,
                invoice_quantity=invoice_item.quantity,
                invoice_unit_price=invoice_item.unit_price,
                invoice_discount_pct=invoice_item.discount_pct,
                invoice_discount_amount=invoice_item.discount_amount,
                invoice_line_total=invoice_item.total_price,
                quantity_discrepancy=True,
                price_discrepancy=True,
                total_discrepancy=True,
                status="EXTRA_IN_INVOICE",
                severity="HIGH",
                reason="Item not in Purchase Order"
            )

        if not invoice_item:
            return ItemDiscrepancy(
                item_no=po_item.item_no,
                description=po_item.description,
                po_quantity=po_item.quantity,
                po_unit_price=po_item.unit_price,
                po_discount_pct=po_item.discount_pct,
                po_discount_amount=po_item.discount_amount,
                po_line_total=po_item.total_price,
                invoice_quantity=0,
                invoice_unit_price=0,
                invoice_discount_pct=0,
                invoice_discount_amount=0,
                invoice_line_total=0,
                quantity_discrepancy=True,
                price_discrepancy=True,
                total_discrepancy=True,
                status="MISSING_FROM_INVOICE",
                severity="CRITICAL",
                reason="Item missing from Invoice"
            )

        # Both items exist - compare them
        qty_diff = invoice_item.quantity - po_item.quantity
        qty_variance = (qty_diff / po_item.quantity * 100) if po_item.quantity > 0 else 0

        price_diff = invoice_item.unit_price - po_item.unit_price
        price_variance = (price_diff / po_item.unit_price * 100) if po_item.unit_price > 0 else 0

        total_diff = invoice_item.total_price - po_item.total_price
        discount_diff = invoice_item.discount_amount - po_item.discount_amount

        # Determine discrepancies (boolean flags)
        qty_discrepancy = abs(qty_variance) > self.quantity_tolerance
        price_discrepancy = abs(price_variance) > self.price_tolerance
        total_discrepancy = abs(total_diff) > 0.01
        discount_discrepancy = abs(discount_diff) > 0.01 or abs(invoice_item.discount_pct - po_item.discount_pct) > 0.01

        # Determine status and reason
        if not qty_discrepancy and not price_discrepancy and not total_discrepancy:
            status = "MATCH"
            reason = "Perfect match"
            severity = "NONE"
        else:
            reasons = []
            if qty_discrepancy:
                reasons.append("Quantity mismatch")
            if price_discrepancy:
                reasons.append("Unit price mismatch")
            if discount_discrepancy:
                reasons.append("Discount percentage mismatch leading to different line total")

            reason = ", ".join(reasons) if reasons else "Line total mismatch"

            if price_discrepancy:
                status = "PRICE_MISMATCH"
            elif qty_discrepancy:
                status = "QUANTITY_MISMATCH"
            else:
                status = "TOTAL_MISMATCH"

            # Determine severity
            if abs(qty_variance) > 20 or abs(price_variance) > 20:
                severity = "CRITICAL"
            elif abs(qty_variance) > 10 or abs(price_variance) > 10:
                severity = "HIGH"
            else:
                severity = "MEDIUM"

        return ItemDiscrepancy(
            item_no=po_item.item_no,
            description=po_item.description,
            po_quantity=po_item.quantity,
            po_unit_price=po_item.unit_price,
            po_discount_pct=po_item.discount_pct,
            po_discount_amount=po_item.discount_amount,
            po_line_total=po_item.total_price,
            invoice_quantity=invoice_item.quantity,
            invoice_unit_price=invoice_item.unit_price,
            invoice_discount_pct=invoice_item.discount_pct,
            invoice_discount_amount=invoice_item.discount_amount,
            invoice_line_total=invoice_item.total_price,
            quantity_discrepancy=qty_discrepancy,
            price_discrepancy=price_discrepancy,
            total_discrepancy=total_discrepancy,
            discount_discrepancy=discount_discrepancy,
            quantity_diff=qty_diff,
            quantity_variance_pct=qty_variance,
            price_diff=price_diff,
            price_variance_pct=price_variance,
            total_diff=total_diff,
            discount_diff=discount_diff,
            status=status,
            severity=severity,
            reason=reason
        )

    def _calculate_summary_metrics(
        self, 
        po_doc: ExtractedDocument, 
        invoice_doc: ExtractedDocument
    ) -> SummaryMetrics:
        """Calculate summary metrics table"""

        return SummaryMetrics(
            subtotal_po=po_doc.subtotal,
            subtotal_pi=invoice_doc.subtotal,
            subtotal_difference=invoice_doc.subtotal - po_doc.subtotal,
            discounts_po=po_doc.total_discount,
            discounts_pi=invoice_doc.total_discount,
            discounts_difference=invoice_doc.total_discount - po_doc.total_discount,
            taxable_amount_po=po_doc.taxable_amount,
            taxable_amount_pi=invoice_doc.taxable_amount,
            taxable_difference=invoice_doc.taxable_amount - po_doc.taxable_amount,
            tax_po=po_doc.tax,
            tax_pi=invoice_doc.tax,
            tax_difference=invoice_doc.tax - po_doc.tax,
            grand_total_po=po_doc.total,
            grand_total_pi=invoice_doc.total,
            grand_total_difference=invoice_doc.total - po_doc.total
        )

    def _generate_summary_text(
        self, 
        total_items: int, 
        matching: int, 
        discrepant: int,
        metrics: SummaryMetrics
    ) -> str:
        """Generate human-readable summary"""

        return f"""
COMPARISON SUMMARY:
==================
Total Items Compared: {total_items}
Matching Items: {matching}
Discrepant Items: {discrepant}

FINANCIAL SUMMARY:
-----------------
Subtotal Difference: ${metrics.subtotal_difference:.2f}
Discount Difference: ${metrics.discounts_difference:.2f}
Taxable Amount Difference: ${metrics.taxable_difference:.2f}
Tax Difference: ${metrics.tax_difference:.2f}
Grand Total Difference: ${metrics.grand_total_difference:.2f}

PO Total: ${metrics.grand_total_po:.2f}
Invoice Total: ${metrics.grand_total_pi:.2f}
Net Difference: ${metrics.grand_total_difference:.2f}
"""

def compare_po_with_invoice(
    po_doc: ExtractedDocument, 
    invoice_doc: ExtractedDocument
) -> DocumentComparison:
    """Main comparison function"""
    comparator = EnhancedDocumentComparator()
    return comparator.compare(po_doc, invoice_doc)
