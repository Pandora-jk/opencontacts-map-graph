#!/usr/bin/env python3
"""
CSV Cleaner & Standardizer
- Removes duplicate rows
- Normalizes column headers (trim, lowercase, replace spaces)
- Handles missing values
- Validates required columns

Usage:
    python csv-cleaner.py input.csv [output.csv]

License: Single User (Commercial Use Allowed)
Price: $7.99
Author: Pandora Automation
"""

import sys
import os
import csv
import re

def normalize_header(header):
    """Normalize column header: lowercase, trim, replace spaces."""
    if not header:
        return 'unnamed_column'
    header = header.strip()
    header = header.lower()
    header = re.sub(r'[_\s]+', '_', header)
    header = re.sub(r'[^\w]', '', header)
    return header

def clean_row(row, headers):
    """Clean a single row: fill missing values, trim strings."""
    cleaned = []
    for i, value in enumerate(row):
        if value is None:
            value = ''
        else:
            value = str(value).strip()
        cleaned.append(value)
    return cleaned

def clean_csv(input_path, output_path=None, required_columns=None):
    """Clean and standardize CSV file."""
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return False
    
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + '_cleaned.csv'
    
    print(f"Cleaning {input_path}...")
    
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = [normalize_header(h) for h in next(reader)]
            
            # Validate required columns
            if required_columns:
                for col in required_columns:
                    if col not in headers:
                        print(f"Warning: Required column '{col}' not found.")
            
            all_rows = []
            seen = set()
            duplicate_count = 0
            
            for row in reader:
                cleaned_row = clean_row(row, headers)
                row_key = tuple(cleaned_row)
                
                if row_key not in seen:
                    seen.add(row_key)
                    all_rows.append(cleaned_row)
                else:
                    duplicate_count += 1
            
            # Write cleaned CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(headers)
                writer.writerows(all_rows)
            
            print(f"✅ Success!")
            print(f"   - Rows processed: {len(all_rows) + duplicate_count}")
            print(f"   - Unique rows: {len(all_rows)}")
            print(f"   - Duplicates removed: {duplicate_count}")
            print(f"   - Output: {output_path}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python csv-cleaner.py <input.csv> [output.csv] [--required col1,col2]")
        print("\nExample:")
        print("  python csv-cleaner.py leads.csv cleaned_leads.csv")
        print("  python csv-cleaner.py data.csv output.csv --required name,email")
        sys.exit(0)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        required_cols = None
        if '--required' in sys.argv:
            idx = sys.argv.index('--required')
            if idx + 1 < len(sys.argv):
                required_cols = sys.argv[idx + 1].split(',')
        
        ok = clean_csv(input_file, output_file, required_cols)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
