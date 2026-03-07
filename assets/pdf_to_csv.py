#!/usr/bin/env python3
"""
PDF to CSV Converter
Converts tables in PDF files to clean CSV format.
Perfect for invoices, reports, and data extraction.

Usage:
    python pdf_to_csv.py input.pdf [output.csv]

License: Single User (Commercial Use Allowed)
Price: $9.99
Author: Pandora Automation (https://github.com/Pandor-jk)
"""

import sys
import os
import csv

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed.")
    print("Run: pip install pdfplumber")
    sys.exit(1)

def convert_pdf_to_csv(pdf_path, output_csv=None):
    """Convert PDF tables to CSV."""
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return False
    
    if output_csv is None:
        output_csv = os.path.splitext(pdf_path)[0] + '.csv'
    
    print(f"Converting {pdf_path} to {output_csv}...")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_rows = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    for row in table:
                        # Clean None values
                        cleaned_row = [cell if cell else '' for cell in row]
                        all_rows.append(cleaned_row)
        
        if all_rows:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(all_rows)
            print(f"✅ Success! Converted {len(all_rows)} rows to {output_csv}")
            return True
        else:
            print("⚠️ No tables found in PDF.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_csv.py <input.pdf> [output.csv]")
        print("\nExample:")
        print("  python pdf_to_csv.py invoice.pdf")
        print("  python pdf_to_csv.py report.pdf report_cleaned.csv")
        sys.exit(0)
    else:
        pdf_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        ok = convert_pdf_to_csv(pdf_file, output_file)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
