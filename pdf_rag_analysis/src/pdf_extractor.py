# # # from pathlib import Path
# # # from typing import Dict, List, Tuple, Optional
# # # import pypdf
# # # import json
# # # import re
# # # from dataclasses import dataclass, asdict
# # # from datetime import datetime

# # # try:
# # #     import pdfplumber
# # #     HAS_PDFPLUMBER = True
# # # except ImportError:
# # #     HAS_PDFPLUMBER = False


# # # @dataclass
# # # class LineItem:
# # #     item_no: str
# # #     description: str
# # #     unit: str
# # #     quantity: float
# # #     unit_price: float
# # #     total_price: float


# # # @dataclass
# # # class DocumentMetadata:
# # #     doc_type: str
# # #     document_id: str
# # #     date: str
# # #     vendor_name: str
# # #     customer_name: str


# # # @dataclass
# # # class ExtractedDocument:
# # #     metadata: DocumentMetadata
# # #     items: List[LineItem]
# # #     subtotal: float
# # #     tax: float
# # #     total: float
# # #     notes: str
# # #     raw_text: str


# # # class PDFExtractor:
# # #     def __init__(self):
# # #         self.currency_pattern = r'\$?\s*[\d,]+\.?\d*'
# # #         self.date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
# # #         self.quantity_pattern = r'^\s*(\d+(?:\.\d+)?)\s*'
    
# # #     def extract_pdf(self, pdf_path: Path) -> ExtractedDocument:
# # #         pdf_reader = pypdf.PdfReader(str(pdf_path))
# # #         raw_text = self._extract_raw_text(pdf_reader)
        
# # #         doc_type = self._detect_document_type(raw_text)
# # #         metadata = self._extract_metadata(raw_text, doc_type)
        
# # #         items = self._extract_line_items(raw_text)
        
# # #         totals = self._extract_totals(raw_text)
# # #         notes = self._extract_notes(raw_text)
        
# # #         return ExtractedDocument(
# # #             metadata=metadata,
# # #             items=items,
# # #             subtotal=totals['subtotal'],
# # #             tax=totals['tax'],
# # #             total=totals['total'],
# # #             notes=notes,
# # #             raw_text=raw_text
# # #         )
    
# # #     def _extract_raw_text(self, pdf_reader) -> str:
# # #         text = ""
# # #         for page in pdf_reader.pages:
# # #             text += page.extract_text()
# # #         return text
    
# # #     def _extract_line_items_from_tables(self, pdf_path: Path) -> List[LineItem]:
# # #         items = []
# # #         if not HAS_PDFPLUMBER:
# # #             return items
        
# # #         try:
# # #             with pdfplumber.open(pdf_path) as pdf:
# # #                 for page in pdf.pages:
# # #                     try:
# # #                         tables = page.extract_tables(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
# # #                         if tables:
# # #                             for table in tables:
# # #                                 items.extend(self._parse_table(table))
# # #                     except Exception as e:
# # #                         print(f"Warning: Could not extract tables from page: {e}")
# # #                         continue
# # #         except Exception as e:
# # #             print(f"Warning: Error opening PDF for table extraction: {e}")
        
# # #         return items
    
# # #     def _parse_table(self, table: List[List[str]]) -> List[LineItem]:
# # #         items = []
# # #         if not table or len(table) < 2:
# # #             return items
        
# # #         header = table[0]
# # #         header_lower = [str(h).lower() for h in header]
        
# # #         sku_idx = self._find_column_index(header_lower, ['sku', 'item', 'code'])
# # #         desc_idx = self._find_column_index(header_lower, ['description', 'product', 'name'])
# # #         qty_idx = self._find_column_index(header_lower, ['qty', 'quantity', 'qry'])
# # #         price_idx = self._find_column_index(header_lower, ['unit price', 'price', 'unit_price'])
        
# # #         if sku_idx is None or qty_idx is None or price_idx is None:
# # #             return items
        
# # #         for row in table[1:]:
# # #             if not row or all(not cell or str(cell).strip() == '' for cell in row):
# # #                 continue
            
# # #             try:
# # #                 sku = str(row[sku_idx]) if sku_idx < len(row) else "UNKNOWN"
# # #                 desc = str(row[desc_idx]) if desc_idx and desc_idx < len(row) else sku
# # #                 qty = self._parse_number(str(row[qty_idx]) if qty_idx < len(row) else "0")
# # #                 unit_price = self._parse_number(str(row[price_idx]) if price_idx < len(row) else "0")
                
# # #                 if qty > 0 and unit_price >= 0:
# # #                     items.append(LineItem(
# # #                         item_no=str(sku),
# # #                         description=str(desc),
# # #                         unit="EA",
# # #                         quantity=qty,
# # #                         unit_price=unit_price,
# # #                         total_price=qty * unit_price
# # #                     ))
# # #             except Exception as e:
# # #                 continue
        
# # #         return items
    
# # #     def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
# # #         for i, header in enumerate(headers):
# # #             if any(keyword in header for keyword in keywords):
# # #                 return i
# # #         return None
    
# # #     def _parse_number(self, value: str) -> float:
# # #         if not value:
# # #             return 0.0
# # #         try:
# # #             return float(re.sub(r'[^\d.-]', '', str(value)))
# # #         except (ValueError, TypeError):
# # #             return 0.0
    
# # #     def _detect_document_type(self, text: str) -> str:
# # #         text_lower = text.lower()
# # #         if 'purchase order' in text_lower or 'po#' in text_lower:
# # #             return 'PURCHASE_ORDER'
# # #         elif 'proforma' in text_lower or 'invoice' in text_lower:
# # #             return 'PROFORMA_INVOICE'
# # #         else:
# # #             return 'UNKNOWN'
    
# # #     def _extract_metadata(self, text: str, doc_type: str) -> DocumentMetadata:
# # #         lines = text.split('\n')
        
# # #         doc_id = self._extract_id(text, doc_type)
# # #         date = self._extract_date(text)
# # #         vendor = self._extract_vendor(text)
# # #         customer = self._extract_customer(text)
        
# # #         return DocumentMetadata(
# # #             doc_type=doc_type,
# # #             document_id=doc_id,
# # #             date=date,
# # #             vendor_name=vendor,
# # #             customer_name=customer
# # #         )
    
# # #     def _extract_id(self, text: str, doc_type: str) -> str:
# # #         patterns = [
# # #             r'(?:PO|Order)\s*#?[\s:]?\s*(\d+)',
# # #             r'(?:Invoice|Proforma)\s*#?[\s:]?\s*(\d+)',
# # #             r'(?:Document|Ref)\s*#?[\s:]?\s*([A-Z0-9\-]+)',
# # #         ]
        
# # #         for pattern in patterns:
# # #             match = re.search(pattern, text, re.IGNORECASE)
# # #             if match:
# # #                 return match.group(1)
# # #         return "UNKNOWN"
    
# # #     def _extract_date(self, text: str) -> str:
# # #         match = re.search(self.date_pattern, text)
# # #         if match:
# # #             return match.group(0)
# # #         return datetime.now().strftime("%Y-%m-%d")
    
# # #     def _extract_vendor(self, text: str) -> str:
# # #         patterns = [
# # #             r'(?:From|Vendor|Supplier)[\s:\n]+([^\n]+)',
# # #             r'(?:Company|To)[\s:\n]+([^\n]+)',
# # #         ]
        
# # #         for pattern in patterns:
# # #             match = re.search(pattern, text, re.IGNORECASE)
# # #             if match:
# # #                 return match.group(1).strip()
# # #         return "Unknown Vendor"
    
# # #     def _extract_customer(self, text: str) -> str:
# # #         patterns = [
# # #             r'(?:Bill To|Ship To|Customer)[\s:\n]+([^\n]+)',
# # #             r'(?:For|Ordered By)[\s:\n]+([^\n]+)',
# # #         ]
        
# # #         for pattern in patterns:
# # #             match = re.search(pattern, text, re.IGNORECASE)
# # #             if match:
# # #                 return match.group(1).strip()
# # #         return "Unknown Customer"
    
# # #     def _extract_line_items(self, text: str) -> List[LineItem]:
# # #         items = []
# # #         lines = text.split('\n')
        
# # #         item_start = False
# # #         for i, line in enumerate(lines):
# # #             if 'item' in line.lower() and 'description' in line.lower():
# # #                 item_start = True
# # #                 continue
            
# # #             if item_start and line.strip():
# # #                 item = self._parse_line_item(line)
# # #                 if item:
# # #                     items.append(item)
            
# # #             if 'subtotal' in line.lower() or 'total' in line.lower():
# # #                 item_start = False
        
# # #         return items
    
# # #     def _parse_line_item(self, line: str) -> LineItem:
# # #         parts = line.split()
# # #         if len(parts) < 4:
# # #             return None
        
# # #         try:
# # #             item_no = parts[0] if parts[0].isdigit() else "0"
# # #             description = " ".join(parts[1:-3])
# # #             unit = parts[-3] if not self._is_number(parts[-3]) else "EA"
# # #             quantity = float(self._extract_number(parts[-2]))
# # #             unit_price = float(self._extract_number(parts[-1]))
# # #             total_price = quantity * unit_price
            
# # #             return LineItem(
# # #                 item_no=item_no,
# # #                 description=description,
# # #                 unit=unit,
# # #                 quantity=quantity,
# # #                 unit_price=unit_price,
# # #                 total_price=total_price
# # #             )
# # #         except (ValueError, IndexError):
# # #             return None
    
# # #     def _extract_totals(self, text: str) -> Dict[str, float]:
# # #         subtotal = self._extract_currency_value(text, r'(?:Subtotal|Sub-Total)[\s:]?\$?([\d,]+\.?\d*)')
# # #         tax = self._extract_currency_value(text, r'(?:Tax|VAT|GST)[\s:]?\$?([\d,]+\.?\d*)')
# # #         total = self._extract_currency_value(text, r'(?:Total|Grand Total)[\s:]?\$?([\d,]+\.?\d*)')
        
# # #         if not total and subtotal and tax:
# # #             total = subtotal + tax
        
# # #         return {
# # #             'subtotal': subtotal,
# # #             'tax': tax,
# # #             'total': total
# # #         }
    
# # #     def _extract_currency_value(self, text: str, pattern: str) -> float:
# # #         match = re.search(pattern, text, re.IGNORECASE)
# # #         if match:
# # #             value_str = match.group(1).replace(',', '')
# # #             try:
# # #                 return float(value_str)
# # #             except ValueError:
# # #                 return 0.0
# # #         return 0.0
    
# # #     def _extract_notes(self, text: str) -> str:
# # #         patterns = [
# # #             r'(?:Notes|Terms|Remarks)[\s:]*\n([\s\S]+?)(?:\n\n|\Z)',
# # #         ]
        
# # #         for pattern in patterns:
# # #             match = re.search(pattern, text, re.IGNORECASE)
# # #             if match:
# # #                 return match.group(1).strip()
# # #         return ""
    
# # #     def _is_number(self, text: str) -> bool:
# # #         try:
# # #             float(text.replace(',', ''))
# # #             return True
# # #         except ValueError:
# # #             return False
    
# # #     def _extract_number(self, text: str) -> str:
# # #         text = text.replace(',', '').strip()
# # #         match = re.search(r'[\d.]+', text)
# # #         return match.group(0) if match else "0"


# # # def extract_all_pdfs(data_dir: Path) -> Dict[str, ExtractedDocument]:
# # #     extractor = PDFExtractor()
# # #     documents = {}
    
# # #     for pdf_file in data_dir.glob("*.pdf"):
# # #         try:
# # #             print(f"Extracting: {pdf_file.name}")
# # #             doc = extractor.extract_pdf(pdf_file)
# # #             documents[pdf_file.stem] = doc
# # #         except Exception as e:
# # #             print(f"Error extracting {pdf_file.name}: {e}")
    
# # #     return documents


# # # def save_extracted_data(documents: Dict[str, ExtractedDocument], output_dir: Path):
# # #     output_dir.mkdir(parents=True, exist_ok=True)
    
# # #     for name, doc in documents.items():
# # #         output_file = output_dir / f"{name}_extracted.json"
        
# # #         doc_dict = {
# # #             'metadata': asdict(doc.metadata),
# # #             'items': [asdict(item) for item in doc.items],
# # #             'subtotal': doc.subtotal,
# # #             'tax': doc.tax,
# # #             'total': doc.total,
# # #             'notes': doc.notes
# # #         }
        
# # #         with open(output_file, 'w') as f:
# # #             json.dump(doc_dict, f, indent=2)
        
# # #         print(f"Saved: {output_file}")
# # from pathlib import Path
# # from typing import Dict, List, Tuple, Optional
# # import pypdf
# # import json
# # import re
# # from dataclasses import dataclass, asdict
# # from datetime import datetime

# # try:
# #     import pdfplumber
# #     HAS_PDFPLUMBER = True
# # except ImportError:
# #     HAS_PDFPLUMBER = False

# # @dataclass
# # class LineItem:
# #     item_no: str
# #     description: str
# #     unit: str
# #     quantity: float
# #     unit_price: float
# #     discount_pct: float = 0.0  # NEW: Capture discount percentage
# #     discount_amount: float = 0.0  # NEW: Capture discount amount
# #     taxable_amount: float = 0.0  # NEW: Amount after discount before tax
# #     total_price: float = 0.0

# #     def __post_init__(self):
# #         """Calculate derived fields"""
# #         if self.discount_amount == 0.0 and self.discount_pct > 0:
# #             self.discount_amount = (self.quantity * self.unit_price * self.discount_pct) / 100

# #         if self.taxable_amount == 0.0:
# #             self.taxable_amount = (self.quantity * self.unit_price) - self.discount_amount

# #         if self.total_price == 0.0:
# #             self.total_price = self.taxable_amount

# # @dataclass
# # class DocumentMetadata:
# #     doc_type: str
# #     document_id: str
# #     date: str
# #     vendor_name: str
# #     customer_name: str

# # @dataclass
# # class ExtractedDocument:
# #     metadata: DocumentMetadata
# #     items: List[LineItem]
# #     subtotal: float
# #     total_discount: float = 0.0  # NEW: Total discount amount
# #     taxable_amount: float = 0.0  # NEW: Amount before tax
# #     tax: float = 0.0
# #     tax_rate: float = 0.0  # NEW: Tax rate percentage
# #     total: float = 0.0
# #     notes: str = ""
# #     raw_text: str = ""

# # class PDFExtractor:
# #     def __init__(self):
# #         self.currency_pattern = r'\$?\s*[\d,]+\.?\d*'
# #         self.date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
# #         self.quantity_pattern = r'^\s*(\d+(?:\.\d+)?)\s*'

# #     def extract_pdf(self, pdf_path: Path) -> ExtractedDocument:
# #         """Extract complete document with enhanced line item parsing"""
# #         pdf_reader = pypdf.PdfReader(str(pdf_path))
# #         raw_text = self._extract_raw_text(pdf_reader)

# #         doc_type = self._detect_document_type(raw_text)
# #         metadata = self._extract_metadata(raw_text, doc_type)

# #         # Try table extraction first, fallback to text parsing
# #         items = self._extract_line_items_from_tables(pdf_path)
# #         if not items:
# #             items = self._extract_line_items(raw_text)

# #         totals = self._extract_totals(raw_text)
# #         notes = self._extract_notes(raw_text)

# #         return ExtractedDocument(
# #             metadata=metadata,
# #             items=items,
# #             subtotal=totals['subtotal'],
# #             total_discount=totals.get('discount', 0.0),
# #             taxable_amount=totals.get('taxable_amount', totals['subtotal']),
# #             tax=totals['tax'],
# #             tax_rate=totals.get('tax_rate', 7.5),
# #             total=totals['total'],
# #             notes=notes,
# #             raw_text=raw_text
# #         )

# #     def _extract_raw_text(self, pdf_reader) -> str:
# #         text = ""
# #         for page in pdf_reader.pages:
# #             text += page.extract_text()
# #         return text

# #     def _extract_line_items_from_tables(self, pdf_path: Path) -> List[LineItem]:
# #         """Enhanced table extraction with discount capture"""
# #         items = []
# #         if not HAS_PDFPLUMBER:
# #             return items

# #         try:
# #             with pdfplumber.open(pdf_path) as pdf:
# #                 for page in pdf.pages:
# #                     try:
# #                         tables = page.extract_tables()
# #                         if tables:
# #                             for table in tables:
# #                                 items.extend(self._parse_table_enhanced(table))
# #                     except Exception as e:
# #                         continue
# #         except Exception as e:
# #             print(f"Warning: Error opening PDF for table extraction: {e}")

# #         return items

# #     def _parse_table_enhanced(self, table: List[List[str]]) -> List[LineItem]:
# #         """Parse table with discount information"""
# #         items = []
# #         if not table or len(table) < 2:
# #             return items

# #         header = table[0]
# #         header_lower = [str(h).lower() if h else "" for h in header]

# #         # Find column indices
# #         sku_idx = self._find_column_index(header_lower, ['sku', 'item', 'code'])
# #         desc_idx = self._find_column_index(header_lower, ['description', 'product', 'name'])
# #         qty_idx = self._find_column_index(header_lower, ['qty', 'quantity', 'qry'])
# #         price_idx = self._find_column_index(header_lower, ['unit price', 'price', 'unit_price'])
# #         discount_pct_idx = self._find_column_index(header_lower, ['discount %', 'disc %', 'discount'])
# #         discount_amt_idx = self._find_column_index(header_lower, ['discount amount', 'disc amt'])
# #         total_idx = self._find_column_index(header_lower, ['line total', 'total', 'amount'])

# #         for row in table[1:]:
# #             if not row or all(not cell or str(cell).strip() == '' for cell in row):
# #                 continue

# #             try:
# #                 sku = str(row[sku_idx]) if sku_idx and sku_idx < len(row) else "UNKNOWN"
# #                 desc = str(row[desc_idx]) if desc_idx and desc_idx < len(row) else sku
# #                 qty = self._parse_number(str(row[qty_idx]) if qty_idx and qty_idx < len(row) else "0")
# #                 unit_price = self._parse_number(str(row[price_idx]) if price_idx and price_idx < len(row) else "0")

# #                 discount_pct = 0.0
# #                 discount_amt = 0.0

# #                 if discount_pct_idx and discount_pct_idx < len(row):
# #                     discount_pct = self._parse_number(str(row[discount_pct_idx]))

# #                 if discount_amt_idx and discount_amt_idx < len(row):
# #                     discount_amt = self._parse_number(str(row[discount_amt_idx]))

# #                 # Calculate total
# #                 if total_idx and total_idx < len(row):
# #                     total_price = self._parse_number(str(row[total_idx]))
# #                 else:
# #                     total_price = qty * unit_price - discount_amt

# #                 if qty > 0 and unit_price >= 0:
# #                     items.append(LineItem(
# #                         item_no=str(sku),
# #                         description=str(desc),
# #                         unit="EA",
# #                         quantity=qty,
# #                         unit_price=unit_price,
# #                         discount_pct=discount_pct,
# #                         discount_amount=discount_amt,
# #                         total_price=total_price
# #                     ))
# #             except Exception as e:
# #                 continue

# #         return items

# #     def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
# #         for i, header in enumerate(headers):
# #             if any(keyword in header for keyword in keywords):
# #                 return i
# #         return None

# #     def _parse_number(self, value: str) -> float:
# #         if not value:
# #             return 0.0
# #         try:
# #             # Remove currency symbols, commas, and other non-numeric characters except decimal point and minus
# #             cleaned = re.sub(r'[^\d.-]', '', str(value))
# #             return float(cleaned) if cleaned else 0.0
# #         except (ValueError, TypeError):
# #             return 0.0

# #     def _detect_document_type(self, text: str) -> str:
# #         text_lower = text.lower()
# #         if 'purchase order' in text_lower or 'po#' in text_lower:
# #             return 'PURCHASE_ORDER'
# #         elif 'proforma' in text_lower or 'invoice' in text_lower:
# #             return 'PROFORMA_INVOICE'
# #         else:
# #             return 'UNKNOWN'

# #     def _extract_metadata(self, text: str, doc_type: str) -> DocumentMetadata:
# #         doc_id = self._extract_id(text, doc_type)
# #         date = self._extract_date(text)
# #         vendor = self._extract_vendor(text)
# #         customer = self._extract_customer(text)

# #         return DocumentMetadata(
# #             doc_type=doc_type,
# #             document_id=doc_id,
# #             date=date,
# #             vendor_name=vendor,
# #             customer_name=customer
# #         )

# #     def _extract_id(self, text: str, doc_type: str) -> str:
# #         patterns = [
# #             r'(?:PO|Order)\s*#?[\s:]?\s*(\d+)',
# #             r'(?:Invoice|Proforma)\s*#?[\s:]?\s*(\d+)',
# #             r'(?:Document|Ref)\s*#?[\s:]?\s*([A-Z0-9\-]+)',
# #         ]
# #         for pattern in patterns:
# #             match = re.search(pattern, text, re.IGNORECASE)
# #             if match:
# #                 return match.group(1)
# #         return "UNKNOWN"

# #     def _extract_date(self, text: str) -> str:
# #         match = re.search(self.date_pattern, text)
# #         if match:
# #             return match.group(0)
# #         return datetime.now().strftime("%Y-%m-%d")

# #     def _extract_vendor(self, text: str) -> str:
# #         patterns = [
# #             r'(?:From|Vendor|Supplier)[\s:\n]+([^\n]+)',
# #             r'(?:Company|To)[\s:\n]+([^\n]+)',
# #         ]
# #         for pattern in patterns:
# #             match = re.search(pattern, text, re.IGNORECASE)
# #             if match:
# #                 return match.group(1).strip()
# #         return "Unknown Vendor"

# #     def _extract_customer(self, text: str) -> str:
# #         patterns = [
# #             r'(?:Bill To|Ship To|Customer)[\s:\n]+([^\n]+)',
# #             r'(?:For|Ordered By)[\s:\n]+([^\n]+)',
# #         ]
# #         for pattern in patterns:
# #             match = re.search(pattern, text, re.IGNORECASE)
# #             if match:
# #                 return match.group(1).strip()
# #         return "Unknown Customer"

# #     def _extract_line_items(self, text: str) -> List[LineItem]:
# #         """Fallback text-based extraction"""
# #         items = []
# #         lines = text.split('\n')

# #         item_start = False
# #         for i, line in enumerate(lines):
# #             if 'item' in line.lower() and 'description' in line.lower():
# #                 item_start = True
# #                 continue

# #             if item_start and line.strip():
# #                 item = self._parse_line_item(line)
# #                 if item:
# #                     items.append(item)

# #             if 'subtotal' in line.lower() or 'total' in line.lower():
# #                 item_start = False

# #         return items

# #     def _parse_line_item(self, line: str) -> Optional[LineItem]:
# #         parts = line.split()
# #         if len(parts) < 4:
# #             return None

# #         try:
# #             item_no = parts[0] if parts[0].isdigit() or parts[0].isalnum() else "0"
# #             description = " ".join(parts[1:-3])
# #             quantity = float(self._extract_number(parts[-2]))
# #             unit_price = float(self._extract_number(parts[-1]))

# #             return LineItem(
# #                 item_no=item_no,
# #                 description=description,
# #                 unit="EA",
# #                 quantity=quantity,
# #                 unit_price=unit_price,
# #                 total_price=quantity * unit_price
# #             )
# #         except (ValueError, IndexError):
# #             return None

# #     def _extract_totals(self, text: str) -> Dict[str, float]:
# #         """Extract financial totals including discount and tax"""
# #         subtotal = self._extract_currency_value(text, r'(?:Subtotal|Sub-Total)[\s:]?\$?([\d,]+\.?\d*)')
# #         discount = self._extract_currency_value(text, r'(?:Discount|Total Discount)[\s:]?\$?([\d,]+\.?\d*)')
# #         taxable = self._extract_currency_value(text, r'(?:Taxable Amount|Amount Before Tax)[\s:]?\$?([\d,]+\.?\d*)')
# #         tax = self._extract_currency_value(text, r'(?:Tax|VAT|GST)[\s:]?\$?([\d,]+\.?\d*)')
# #         total = self._extract_currency_value(text, r'(?:Grand Total|Total)[\s:]?\$?([\d,]+\.?\d*)')

# #         # Extract tax rate
# #         tax_rate_match = re.search(r'(?:Tax|VAT|GST)\s*[@]?\s*([\d.]+)%', text, re.IGNORECASE)
# #         tax_rate = float(tax_rate_match.group(1)) if tax_rate_match else 7.5

# #         # Calculate missing values
# #         if not taxable and subtotal and discount:
# #             taxable = subtotal - discount

# #         if not total and taxable and tax:
# #             total = taxable + tax

# #         return {
# #             'subtotal': subtotal,
# #             'discount': discount,
# #             'taxable_amount': taxable,
# #             'tax': tax,
# #             'tax_rate': tax_rate,
# #             'total': total
# #         }

# #     def _extract_currency_value(self, text: str, pattern: str) -> float:
# #         match = re.search(pattern, text, re.IGNORECASE)
# #         if match:
# #             value_str = match.group(1).replace(',', '')
# #             try:
# #                 return float(value_str)
# #             except ValueError:
# #                 return 0.0
# #         return 0.0

# #     def _extract_number(self, value: str) -> str:
# #         """Extract numeric value from string"""
# #         return re.sub(r'[^\d.]', '', value)

# #     def _extract_notes(self, text: str) -> str:
# #         patterns = [
# #             r'(?:Notes|Terms|Remarks)[\s:]*\n([\s\S]+?)(?:\n\n|\Z)',
# #         ]
# #         for pattern in patterns:
# #             match = re.search(pattern, text, re.IGNORECASE)
# #             if match:
# #                 return match.group(1).strip()
# #         return ""

# # def extract_all_pdfs(data_dir: Path) -> Dict[str, ExtractedDocument]:
# #     """Extract all PDFs from directory"""
# #     extractor = PDFExtractor()
# #     documents = {}

# #     for pdf_file in data_dir.glob("*.pdf"):
# #         try:
# #             doc = extractor.extract_pdf(pdf_file)
# #             documents[pdf_file.stem] = doc
# #         except Exception as e:
# #             print(f"Error extracting {pdf_file.name}: {e}")

# #     return documents
# from pathlib import Path
# from typing import Dict, List, Tuple, Optional
# import pypdf
# import json
# import re
# from dataclasses import dataclass, asdict
# from datetime import datetime

# try:
#     import pdfplumber
#     HAS_PDFPLUMBER = True
# except ImportError:
#     HAS_PDFPLUMBER = False

# @dataclass
# class LineItem:
#     item_no: str
#     description: str
#     unit: str
#     quantity: float
#     unit_price: float
#     discount_pct: float = 0.0  # NEW: Capture discount percentage
#     discount_amount: float = 0.0  # NEW: Capture discount amount
#     taxable_amount: float = 0.0  # NEW: Amount after discount before tax
#     total_price: float = 0.0

#     def __post_init__(self):
#         """Calculate derived fields"""
#         if self.discount_amount == 0.0 and self.discount_pct > 0:
#             self.discount_amount = (self.quantity * self.unit_price * self.discount_pct) / 100

#         if self.taxable_amount == 0.0:
#             self.taxable_amount = (self.quantity * self.unit_price) - self.discount_amount

#         if self.total_price == 0.0:
#             self.total_price = self.taxable_amount

# @dataclass
# class DocumentMetadata:
#     doc_type: str
#     document_id: str
#     date: str
#     vendor_name: str
#     customer_name: str

# @dataclass
# class ExtractedDocument:
#     metadata: DocumentMetadata
#     items: List[LineItem]
#     subtotal: float
#     total_discount: float = 0.0  # NEW: Total discount amount
#     taxable_amount: float = 0.0  # NEW: Amount before tax
#     tax: float = 0.0
#     tax_rate: float = 0.0  # NEW: Tax rate percentage
#     total: float = 0.0
#     notes: str = ""
#     raw_text: str = ""

# class PDFExtractor:
#     def __init__(self):
#         self.currency_pattern = r'\$?\s*[\d,]+\.?\d*'
#         self.date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
#         self.quantity_pattern = r'^\s*(\d+(?:\.\d+)?)\s*'

#     def extract_pdf(self, pdf_path: Path) -> ExtractedDocument:
#         """Extract complete document with enhanced line item parsing"""
#         pdf_reader = pypdf.PdfReader(str(pdf_path))
#         raw_text = self._extract_raw_text(pdf_reader)

#         doc_type = self._detect_document_type(raw_text)
#         metadata = self._extract_metadata(raw_text, doc_type)

#         # Try table extraction first, fallback to text parsing
#         items = self._extract_line_items_from_tables(pdf_path)
#         if not items:
#             items = self._extract_line_items(raw_text)

#         totals = self._extract_totals(raw_text)
#         notes = self._extract_notes(raw_text)

#         return ExtractedDocument(
#             metadata=metadata,
#             items=items,
#             subtotal=totals['subtotal'],
#             total_discount=totals.get('discount', 0.0),
#             taxable_amount=totals.get('taxable_amount', totals['subtotal']),
#             tax=totals['tax'],
#             tax_rate=totals.get('tax_rate', 7.5),
#             total=totals['total'],
#             notes=notes,
#             raw_text=raw_text
#         )

#     def _extract_raw_text(self, pdf_reader) -> str:
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#         return text

#     def _extract_line_items_from_tables(self, pdf_path: Path) -> List[LineItem]:
#         """Enhanced table extraction with discount capture"""
#         items = []
#         if not HAS_PDFPLUMBER:
#             return items

#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     try:
#                         tables = page.extract_tables()
#                         if tables:
#                             for table in tables:
#                                 items.extend(self._parse_table_enhanced(table))
#                     except Exception as e:
#                         continue
#         except Exception as e:
#             print(f"Warning: Error opening PDF for table extraction: {e}")

#         return items

#     def _parse_table_enhanced(self, table: List[List[str]]) -> List[LineItem]:
#         """Parse table with discount information"""
#         items = []
#         if not table or len(table) < 2:
#             return items

#         header = table[0]
#         header_lower = [str(h).lower() if h else "" for h in header]

#         # Find column indices
#         sku_idx = self._find_column_index(header_lower, ['sku', 'item', 'code'])
#         desc_idx = self._find_column_index(header_lower, ['description', 'product', 'name'])
#         qty_idx = self._find_column_index(header_lower, ['qty', 'quantity', 'qry'])
#         price_idx = self._find_column_index(header_lower, ['unit price', 'price', 'unit_price'])
#         discount_pct_idx = self._find_column_index(header_lower, ['discount %', 'disc %', 'discount'])
#         discount_amt_idx = self._find_column_index(header_lower, ['discount amount', 'disc amt'])
#         total_idx = self._find_column_index(header_lower, ['line total', 'total', 'amount'])

#         for row in table[1:]:
#             if not row or all(not cell or str(cell).strip() == '' for cell in row):
#                 continue

#             try:
#                 sku = str(row[sku_idx]) if sku_idx and sku_idx < len(row) else "UNKNOWN"
#                 desc = str(row[desc_idx]) if desc_idx and desc_idx < len(row) else sku
#                 qty = self._parse_number(str(row[qty_idx]) if qty_idx and qty_idx < len(row) else "0")
#                 unit_price = self._parse_number(str(row[price_idx]) if price_idx and price_idx < len(row) else "0")

#                 discount_pct = 0.0
#                 discount_amt = 0.0

#                 if discount_pct_idx and discount_pct_idx < len(row):
#                     discount_pct = self._parse_number(str(row[discount_pct_idx]))

#                 if discount_amt_idx and discount_amt_idx < len(row):
#                     discount_amt = self._parse_number(str(row[discount_amt_idx]))

#                 # Calculate total
#                 if total_idx and total_idx < len(row):
#                     total_price = self._parse_number(str(row[total_idx]))
#                 else:
#                     total_price = qty * unit_price - discount_amt

#                 if qty > 0 and unit_price >= 0:
#                     items.append(LineItem(
#                         item_no=str(sku),
#                         description=str(desc),
#                         unit="EA",
#                         quantity=qty,
#                         unit_price=unit_price,
#                         discount_pct=discount_pct,
#                         discount_amount=discount_amt,
#                         total_price=total_price
#                     ))
#             except Exception as e:
#                 continue

#         return items

#     def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
#         for i, header in enumerate(headers):
#             if any(keyword in header for keyword in keywords):
#                 return i
#         return None

#     def _parse_number(self, value: str) -> float:
#         if not value:
#             return 0.0
#         try:
#             # Remove currency symbols, commas, and other non-numeric characters except decimal point and minus
#             cleaned = re.sub(r'[^\d.-]', '', str(value))
#             return float(cleaned) if cleaned else 0.0
#         except (ValueError, TypeError):
#             return 0.0

#     def _detect_document_type(self, text: str) -> str:
#         text_lower = text.lower()
#         if 'purchase order' in text_lower or 'po#' in text_lower:
#             return 'PURCHASE_ORDER'
#         elif 'proforma' in text_lower or 'invoice' in text_lower:
#             return 'PROFORMA_INVOICE'
#         else:
#             return 'UNKNOWN'

#     def _extract_metadata(self, text: str, doc_type: str) -> DocumentMetadata:
#         doc_id = self._extract_id(text, doc_type)
#         date = self._extract_date(text)
#         vendor = self._extract_vendor(text)
#         customer = self._extract_customer(text)

#         return DocumentMetadata(
#             doc_type=doc_type,
#             document_id=doc_id,
#             date=date,
#             vendor_name=vendor,
#             customer_name=customer
#         )

#     def _extract_id(self, text: str, doc_type: str) -> str:
#         patterns = [
#             r'(?:PO|Order)\s*#?[\s:]?\s*(\d+)',
#             r'(?:Invoice|Proforma)\s*#?[\s:]?\s*(\d+)',
#             r'(?:Document|Ref)\s*#?[\s:]?\s*([A-Z0-9\-]+)',
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 return match.group(1)
#         return "UNKNOWN"

#     def _extract_date(self, text: str) -> str:
#         match = re.search(self.date_pattern, text)
#         if match:
#             return match.group(0)
#         return datetime.now().strftime("%Y-%m-%d")

#     def _extract_vendor(self, text: str) -> str:
#         patterns = [
#             r'(?:From|Vendor|Supplier)[\s:\n]+([^\n]+)',
#             r'(?:Company|To)[\s:\n]+([^\n]+)',
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 return match.group(1).strip()
#         return "Unknown Vendor"

#     def _extract_customer(self, text: str) -> str:
#         patterns = [
#             r'(?:Bill To|Ship To|Customer)[\s:\n]+([^\n]+)',
#             r'(?:For|Ordered By)[\s:\n]+([^\n]+)',
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 return match.group(1).strip()
#         return "Unknown Customer"

#     def _extract_line_items(self, text: str) -> List[LineItem]:
#         """Fallback text-based extraction"""
#         items = []
#         lines = text.split('\n')

#         item_start = False
#         for i, line in enumerate(lines):
#             if 'item' in line.lower() and 'description' in line.lower():
#                 item_start = True
#                 continue

#             if item_start and line.strip():
#                 item = self._parse_line_item(line)
#                 if item:
#                     items.append(item)

#             if 'subtotal' in line.lower() or 'total' in line.lower():
#                 item_start = False

#         return items

#     def _parse_line_item(self, line: str) -> Optional[LineItem]:
#         parts = line.split()
#         if len(parts) < 4:
#             return None

#         try:
#             item_no = parts[0] if parts[0].isdigit() or parts[0].isalnum() else "0"
#             description = " ".join(parts[1:-3])
#             quantity = float(self._extract_number(parts[-2]))
#             unit_price = float(self._extract_number(parts[-1]))

#             return LineItem(
#                 item_no=item_no,
#                 description=description,
#                 unit="EA",
#                 quantity=quantity,
#                 unit_price=unit_price,
#                 total_price=quantity * unit_price
#             )
#         except (ValueError, IndexError):
#             return None

#     def _extract_totals(self, text: str) -> Dict[str, float]:
#         """Extract financial totals including discount and tax"""
#         subtotal = self._extract_currency_value(text, r'(?:Subtotal|Sub-Total)[\s:]?\$?([\d,]+\.?\d*)')
#         discount = self._extract_currency_value(text, r'(?:Discount|Total Discount)[\s:]?\$?([\d,]+\.?\d*)')
#         taxable = self._extract_currency_value(text, r'(?:Taxable Amount|Amount Before Tax)[\s:]?\$?([\d,]+\.?\d*)')
#         tax = self._extract_currency_value(text, r'(?:Tax|VAT|GST)[\s:]?\$?([\d,]+\.?\d*)')
#         total = self._extract_currency_value(text, r'(?:Grand Total|Total)[\s:]?\$?([\d,]+\.?\d*)')

#         # Extract tax rate
#         tax_rate_match = re.search(r'(?:Tax|VAT|GST)\s*[@]?\s*([\d.]+)%', text, re.IGNORECASE)
#         tax_rate = float(tax_rate_match.group(1)) if tax_rate_match else 7.5

#         # Calculate missing values
#         if not taxable and subtotal and discount:
#             taxable = subtotal - discount

#         if not total and taxable and tax:
#             total = taxable + tax

#         return {
#             'subtotal': subtotal,
#             'discount': discount,
#             'taxable_amount': taxable,
#             'tax': tax,
#             'tax_rate': tax_rate,
#             'total': total
#         }

#     def _extract_currency_value(self, text: str, pattern: str) -> float:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             value_str = match.group(1).replace(',', '')
#             try:
#                 return float(value_str)
#             except ValueError:
#                 return 0.0
#         return 0.0

#     def _extract_number(self, value: str) -> str:
#         """Extract numeric value from string"""
#         return re.sub(r'[^\d.]', '', value)

#     def _extract_notes(self, text: str) -> str:
#         patterns = [
#             r'(?:Notes|Terms|Remarks)[\s:]*\n([\s\S]+?)(?:\n\n|\Z)',
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 return match.group(1).strip()
#         return ""

# def extract_all_pdfs(data_dir: Path) -> Dict[str, ExtractedDocument]:
#     """Extract all PDFs from directory"""
#     extractor = PDFExtractor()
#     documents = {}

#     for pdf_file in data_dir.glob("*.pdf"):
#         try:
#             doc = extractor.extract_pdf(pdf_file)
#             documents[pdf_file.stem] = doc
#         except Exception as e:
#             print(f"Error extracting {pdf_file.name}: {e}")

#     return documents
from pathlib import Path
from typing import Dict, List, Optional
import pypdf
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

@dataclass
class LineItem:
    item_no: str
    description: str
    unit: str
    quantity: float
    unit_price: float
    discount_pct: float = 0.0
    discount_amount: float = 0.0
    taxable_amount: float = 0.0
    total_price: float = 0.0

    def __post_init__(self):
        """Calculate derived fields"""
        if self.discount_amount == 0.0 and self.discount_pct > 0:
            self.discount_amount = (self.quantity * self.unit_price * self.discount_pct) / 100

        if self.taxable_amount == 0.0:
            self.taxable_amount = (self.quantity * self.unit_price) - self.discount_amount

        if self.total_price == 0.0:
            self.total_price = self.taxable_amount

@dataclass
class DocumentMetadata:
    doc_type: str
    document_id: str
    date: str
    vendor_name: str
    customer_name: str

@dataclass
class ExtractedDocument:
    metadata: DocumentMetadata
    items: List[LineItem]
    subtotal: float
    total_discount: float = 0.0
    taxable_amount: float = 0.0
    tax: float = 0.0
    tax_rate: float = 0.0
    total: float = 0.0
    notes: str = ""
    raw_text: str = ""

class PDFExtractor:
    def __init__(self):
        self.currency_pattern = r'\$?\s*[\d,]+\.?\d*'
        self.date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
        self.quantity_pattern = r'^\s*(\d+(?:\.\d+)?)\s*'

    def extract_pdf(self, pdf_path: Path) -> ExtractedDocument:
        """Extract complete document with enhanced line item parsing"""
        pdf_reader = pypdf.PdfReader(str(pdf_path))
        raw_text = self._extract_raw_text(pdf_reader)

        doc_type = self._detect_document_type(raw_text)
        metadata = self._extract_metadata(raw_text, doc_type)

        # Try table extraction first, fallback to text parsing
        items = self._extract_line_items_from_tables(pdf_path)
        if not items:
            print(f"⚠️  WARNING: Table extraction failed, trying text parsing...")
            items = self._extract_line_items(raw_text)

        totals = self._extract_totals_from_tables(pdf_path)
        if not totals or totals['total'] == 0.0:
            totals = self._extract_totals(raw_text)

        notes = self._extract_notes(raw_text)

        print(f"✅ Extracted {len(items)} line items from {pdf_path.name}")

        return ExtractedDocument(
            metadata=metadata,
            items=items,
            subtotal=totals['subtotal'],
            total_discount=totals.get('discount', 0.0),
            taxable_amount=totals.get('taxable_amount', totals['subtotal']),
            tax=totals['tax'],
            tax_rate=totals.get('tax_rate', 7.5),
            total=totals['total'],
            notes=notes,
            raw_text=raw_text
        )

    def _extract_raw_text(self, pdf_reader) -> str:
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def _extract_line_items_from_tables(self, pdf_path: Path) -> List[LineItem]:
        """CUSTOMIZED for your PDF format"""
        items = []
        if not HAS_PDFPLUMBER:
            print("⚠️  pdfplumber not available, skipping table extraction")
            return items

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Only process first page (line items are on page 1)
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]

                    try:
                        tables = page.extract_tables()
                        if tables and len(tables) > 0:
                            # Get the first table (line items table)
                            table = tables[0]
                            items = self._parse_table_custom(table)
                            print(f"  📊 Parsed {len(items)} items from table")
                    except Exception as e:
                        print(f"  ⚠️  Error extracting table: {e}")
        except Exception as e:
            print(f"  ⚠️  Error opening PDF: {e}")

        return items

    def _parse_table_custom(self, table: List[List[str]]) -> List[LineItem]:
        """
        CUSTOM PARSER for your exact PDF format:

        PURCHASE ORDER columns:
        ['SKU', 'Description', 'Qty', 'Unit Price', 'Discount %', 'Tax %', 
         'Line Subtotal', 'Discount Amount', 'Taxable Amount', 'Tax Amount', 'Line Total']

        PROFORMA INVOICE columns:
        ['SKU', 'Description', 'Qty', 'Unit Price (PI)', 'Discount % (PI)', 'Tax % (PI)',
         'Line Subtotal (PI)', 'Discount Amount (PI)', 'Taxable Amount (PI)', 'Tax Amount (PI)', 'Line Total (PI)']
        """
        items = []
        if not table or len(table) < 2:
            return items

        header = table[0]
        header_lower = [str(h).lower().strip() if h else "" for h in header]

        # Find column indices (works for both PO and PI formats)
        sku_idx = self._find_exact_column(header_lower, ['sku'])
        desc_idx = self._find_exact_column(header_lower, ['description'])
        qty_idx = self._find_exact_column(header_lower, ['qty'])

        # Unit price (handles both "unit price" and "unit price (pi)")
        price_idx = None
        for i, h in enumerate(header_lower):
            if 'unit price' in h:
                price_idx = i
                break

        # Discount % (handles both "discount %" and "discount % (pi)")
        discount_pct_idx = None
        for i, h in enumerate(header_lower):
            if 'discount %' in h:
                discount_pct_idx = i
                break

        # Discount Amount (handles both formats)
        discount_amt_idx = None
        for i, h in enumerate(header_lower):
            if 'discount amount' in h:
                discount_amt_idx = i
                break

        # Taxable Amount
        taxable_idx = None
        for i, h in enumerate(header_lower):
            if 'taxable amount' in h:
                taxable_idx = i
                break

        # Line Total
        total_idx = None
        for i, h in enumerate(header_lower):
            if 'line total' in h:
                total_idx = i
                break

        # Parse data rows (skip header)
        for row_num, row in enumerate(table[1:], start=1):
            if not row or all(not cell or str(cell).strip() == '' for cell in row):
                continue

            try:
                # Extract values with None checks
                sku = str(row[sku_idx]).strip() if sku_idx is not None and sku_idx < len(row) and row[sku_idx] else "UNKNOWN"
                desc = str(row[desc_idx]).strip() if desc_idx is not None and desc_idx < len(row) and row[desc_idx] else sku

                qty = self._parse_number(str(row[qty_idx])) if qty_idx is not None and qty_idx < len(row) else 0.0
                unit_price = self._parse_number(str(row[price_idx])) if price_idx is not None and price_idx < len(row) else 0.0

                discount_pct = self._parse_number(str(row[discount_pct_idx])) if discount_pct_idx is not None and discount_pct_idx < len(row) else 0.0
                discount_amt = self._parse_number(str(row[discount_amt_idx])) if discount_amt_idx is not None and discount_amt_idx < len(row) else 0.0

                taxable = self._parse_number(str(row[taxable_idx])) if taxable_idx is not None and taxable_idx < len(row) else 0.0
                total_price = self._parse_number(str(row[total_idx])) if total_idx is not None and total_idx < len(row) else 0.0

                # Only add if we have valid quantity and price
                if qty > 0 and unit_price > 0:
                    items.append(LineItem(
                        item_no=sku,
                        description=desc,
                        unit="EA",
                        quantity=qty,
                        unit_price=unit_price,
                        discount_pct=discount_pct,
                        discount_amount=discount_amt,
                        taxable_amount=taxable,
                        total_price=total_price
                    ))
            except Exception as e:
                print(f"  ⚠️  Error parsing row {row_num}: {e}")
                continue

        return items

    def _extract_totals_from_tables(self, pdf_path: Path) -> Dict[str, float]:
        """Extract totals from the summary table on page 2"""
        totals = {'subtotal': 0.0, 'discount': 0.0, 'taxable_amount': 0.0, 'tax': 0.0, 'tax_rate': 7.5, 'total': 0.0}

        if not HAS_PDFPLUMBER:
            return totals

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Page 2 has the summary table
                if len(pdf.pages) > 1:
                    page = pdf.pages[1]

                    try:
                        tables = page.extract_tables()
                        if tables and len(tables) > 0:
                            table = tables[0]

                            # Parse summary table
                            # Format: ['Metric', 'Amount']
                            for row in table[1:]:  # Skip header
                                if row and len(row) >= 2:
                                    metric = str(row[0]).strip().lower()
                                    amount = self._parse_number(str(row[1]))

                                    if 'subtotal' in metric:
                                        totals['subtotal'] = amount
                                    elif 'discount' in metric:
                                        totals['discount'] = amount
                                    elif 'taxable' in metric:
                                        totals['taxable_amount'] = amount
                                    elif 'tax' in metric and 'grand' not in metric:
                                        totals['tax'] = amount
                                    elif 'grand total' in metric or 'total' in metric:
                                        totals['total'] = amount
                    except Exception as e:
                        print(f"  ⚠️  Error extracting totals table: {e}")
        except Exception as e:
            print(f"  ⚠️  Error opening PDF for totals: {e}")

        return totals

    def _find_exact_column(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column by exact keyword match"""
        for i, header in enumerate(headers):
            if any(keyword == header for keyword in keywords):
                return i
        return None

    def _parse_number(self, value: str) -> float:
        """Parse number from string, handling various formats"""
        if not value or value == 'None':
            return 0.0
        try:
            # Remove currency symbols, commas, spaces
            cleaned = re.sub(r'[^\d.-]', '', str(value))
            return float(cleaned) if cleaned and cleaned != '-' else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _detect_document_type(self, text: str) -> str:
        text_lower = text.lower()
        if 'purchase order' in text_lower or 'po#' in text_lower:
            return 'PURCHASE_ORDER'
        elif 'proforma' in text_lower:
            return 'PROFORMA_INVOICE'
        elif 'invoice' in text_lower:
            return 'INVOICE'
        else:
            return 'UNKNOWN'

    def _extract_metadata(self, text: str, doc_type: str) -> DocumentMetadata:
        doc_id = self._extract_id(text, doc_type)
        date = self._extract_date(text)
        vendor = self._extract_vendor(text)
        customer = self._extract_customer(text)

        return DocumentMetadata(
            doc_type=doc_type,
            document_id=doc_id,
            date=date,
            vendor_name=vendor,
            customer_name=customer
        )

    def _extract_id(self, text: str, doc_type: str) -> str:
        patterns = [
            r'(?:PO|Order)\s*#?[\s:]?\s*(\d+)',
            r'(?:Invoice|Proforma)\s*#?[\s:]?\s*(\d+)',
            r'(?:Document|Ref)\s*#?[\s:]?\s*([A-Z0-9\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "UNKNOWN"

    def _extract_date(self, text: str) -> str:
        # Look for dates in filename or text
        filename_date = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if filename_date:
            return filename_date.group(1)

        match = re.search(self.date_pattern, text)
        if match:
            return match.group(0)
        return datetime.now().strftime("%Y-%m-%d")

    def _extract_vendor(self, text: str) -> str:
        # Your PDFs have "Infinity Supplies"
        if 'infinity supplies' in text.lower():
            return "Infinity Supplies"

        patterns = [
            r'(?:From|Vendor|Supplier)[\s:\n]+([^\n]+)',
            r'(?:Company|To)[\s:\n]+([^\n]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Unknown Vendor"

    def _extract_customer(self, text: str) -> str:
        patterns = [
            r'(?:Bill To|Ship To|Customer)[\s:\n]+([^\n]+)',
            r'(?:For|Ordered By)[\s:\n]+([^\n]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Unknown Customer"

    def _extract_line_items(self, text: str) -> List[LineItem]:
        """Fallback text-based extraction"""
        print("  ⚠️  Using fallback text extraction (table extraction failed)")
        return []

    def _extract_totals(self, text: str) -> Dict[str, float]:
        """Fallback totals extraction from text"""
        subtotal = self._extract_currency_value(text, r'(?:Subtotal|Sub-Total)[\s:]?\$?([\d,]+\.?\d*)')
        discount = self._extract_currency_value(text, r'(?:Discount|Total Discount)[\s:]?\$?([\d,]+\.?\d*)')
        taxable = self._extract_currency_value(text, r'(?:Taxable Amount|Amount Before Tax)[\s:]?\$?([\d,]+\.?\d*)')
        tax = self._extract_currency_value(text, r'(?:Tax|VAT|GST)[\s:]?\$?([\d,]+\.?\d*)')
        total = self._extract_currency_value(text, r'(?:Grand Total|Total)[\s:]?\$?([\d,]+\.?\d*)')

        tax_rate_match = re.search(r'(?:Tax|VAT|GST)\s*[@]?\s*([\d.]+)%', text, re.IGNORECASE)
        tax_rate = float(tax_rate_match.group(1)) if tax_rate_match else 7.5

        if not taxable and subtotal and discount:
            taxable = subtotal - discount

        if not total and taxable and tax:
            total = taxable + tax

        return {
            'subtotal': subtotal,
            'discount': discount,
            'taxable_amount': taxable,
            'tax': tax,
            'tax_rate': tax_rate,
            'total': total
        }

    def _extract_currency_value(self, text: str, pattern: str) -> float:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(',', '')
            try:
                return float(value_str)
            except ValueError:
                return 0.0
        return 0.0

    def _extract_notes(self, text: str) -> str:
        if 'confidential' in text.lower():
            return "Confidential document"
        return ""


def extract_all_pdfs(data_dir: Path) -> Dict[str, ExtractedDocument]:
    """Extract all PDFs from directory"""
    extractor = PDFExtractor()
    documents = {}

    print(f"\n{'='*80}")
    print("EXTRACTING PDFs")
    print('='*80)

    for pdf_file in data_dir.glob("*.pdf"):
        try:
            print(f"\n📄 Processing: {pdf_file.name}")
            doc = extractor.extract_pdf(pdf_file)
            documents[pdf_file.stem] = doc
            print(f"  ✅ Success: {len(doc.items)} items, Total: ${doc.total:.2f}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}\n")
    return documents
