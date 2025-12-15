"""
PDF Table Extraction Diagnostic Tool
================================================================================
This script analyzes your PDF files to show:
- What tables are being detected
- Column headers in each table
- Sample data rows
- Why extraction might be failing

Run this and share the OUTPUT with me!
================================================================================
"""

from pathlib import Path
import sys

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("❌ ERROR: pdfplumber not installed!")
    print("   Install it with: pip install pdfplumber")
    sys.exit(1)

def diagnose_pdf_extraction(pdf_path: Path):
    """Diagnose PDF table extraction for a single PDF file"""
    print(f"\n{'='*80}")
    print(f"DIAGNOSTIC REPORT: {pdf_path.name}")
    print('='*80)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"\n📄 Total pages: {len(pdf.pages)}")

            for page_num, page in enumerate(pdf.pages, 1):
                print(f"\n{'─'*80}")
                print(f"PAGE {page_num}")
                print('─'*80)

                # Extract text sample
                text = page.extract_text()
                if text:
                    print(f"\n📝 Text sample (first 500 characters):")
                    print("-" * 40)
                    print(text[:500])
                    print("...")
                    print("-" * 40)
                else:
                    print("\n⚠️  No text extracted from this page")

                # Try different table extraction strategies
                print(f"\n🔍 TABLE EXTRACTION ATTEMPTS:")

                # Strategy 1: Default extraction
                try:
                    tables = page.extract_tables()
                    print(f"\n  Strategy 1 (Default):")
                    print(f"    Tables found: {len(tables) if tables else 0}")

                    if tables:
                        for table_num, table in enumerate(tables, 1):
                            print(f"\n    ┌─ TABLE {table_num} ─┐")
                            print(f"    │ Rows: {len(table)}")
                            print(f"    │ Columns: {len(table[0]) if table else 0}")
                            print(f"    └─────────────┘")

                            if table and len(table) > 0:
                                print(f"\n    📋 Header row (index 0):")
                                print(f"       {table[0]}")

                                if len(table) > 1:
                                    print(f"\n    📊 First data row (index 1):")
                                    print(f"       {table[1]}")

                                if len(table) > 2:
                                    print(f"\n    📊 Second data row (index 2):")
                                    print(f"       {table[2]}")

                                # Show all rows (limited to first 10)
                                print(f"\n    📊 All rows (max 10):")
                                for i, row in enumerate(table[:10]):
                                    print(f"       Row {i}: {row}")
                    else:
                        print("    ❌ NO TABLES DETECTED with default strategy")

                except Exception as e:
                    print(f"    ❌ Error with default extraction: {e}")

                # Strategy 2: With explicit settings
                try:
                    table_settings = {
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                    }
                    tables = page.extract_tables(table_settings=table_settings)
                    print(f"\n  Strategy 2 (Lines-based):")
                    print(f"    Tables found: {len(tables) if tables else 0}")

                    if tables and not page.extract_tables():
                        # Only show if different from default
                        for table_num, table in enumerate(tables, 1):
                            print(f"    TABLE {table_num}: {len(table)} rows, {len(table[0]) if table else 0} cols")

                except Exception as e:
                    print(f"    ❌ Error with lines-based extraction: {e}")

                # Strategy 3: Text-based
                try:
                    table_settings = {
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }
                    tables = page.extract_tables(table_settings=table_settings)
                    print(f"\n  Strategy 3 (Text-based):")
                    print(f"    Tables found: {len(tables) if tables else 0}")

                except Exception as e:
                    print(f"    ❌ Error with text-based extraction: {e}")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR opening PDF: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}\n")


def main():
    """Main diagnostic function"""
    print("\n" + "="*80)
    print("PDF TABLE EXTRACTION DIAGNOSTIC TOOL")
    print("="*80)

    # Try to find PDFs in common locations
    possible_dirs = [
        Path("data"),
        Path("Data"),
        Path("."),
        Path("../data"),
    ]

    data_dir = None
    for dir_path in possible_dirs:
        if dir_path.exists():
            pdf_files = list(dir_path.glob("*.pdf"))
            if pdf_files:
                data_dir = dir_path
                break

    if not data_dir:
        print("\n❌ NO PDF FILES FOUND!")
        print(f"\n   Searched in:")
        for dir_path in possible_dirs:
            print(f"     - {dir_path.absolute()}")
        print("\n   Please:")
        print("     1. Place your PDF files in a 'data' folder")
        print("     2. Or run this script from the directory containing PDFs")
        print("     3. Run: python diagnose_extraction.py")
        return

    pdf_files = list(data_dir.glob("*.pdf"))

    print(f"\n✅ Found {len(pdf_files)} PDF file(s)")
    print(f"   📁 Directory: {data_dir.absolute()}")
    print(f"\n   Files:")
    for pdf in pdf_files:
        print(f"     - {pdf.name}")

    # Diagnose each PDF
    for pdf_path in pdf_files:
        diagnose_pdf_extraction(pdf_path)

    # Summary
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE - NEXT STEPS")
    print("="*80)
    print("\n✅ What to do now:")
    print("   1. Review the output above carefully")
    print("   2. Look for 'Tables found: X' - should be > 0")
    print("   3. Check the Header row - these are your column names")
    print("   4. COPY ALL OUTPUT from 'DIAGNOSTIC REPORT' to end")
    print("   5. PASTE it to me so I can fix the extraction pattern")
    print("\n❌ If 'Tables found: 0':")
    print("   - Your PDFs might not have proper table structure")
    print("   - We'll need to use text-based extraction instead")
    print("   - Share the 'Text sample' with me")
    print("\n✅ If tables ARE found:")
    print("   - I'll customize the column mapping")
    print("   - Your system will extract all items correctly")
    print("   - The item_level_comparison will populate!")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
