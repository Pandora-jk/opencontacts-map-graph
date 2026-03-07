#!/usr/bin/env python3
"""
Lead List Validator
- Validates email addresses
- Checks for required fields
- Removes invalid entries
- Generates validation report

Usage:
    python lead-validator.py input.csv [output.csv]

License: Single User (Commercial Use Allowed)
Price: $6.99
Author: Pandora Automation
"""

import sys
import os
import csv
import re

def validate_email(email):
    """Basic email validation."""
    if not email:
        return False, 'missing'
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, 'valid'
    return False, 'invalid'

def validate_phone(phone):
    """Basic phone validation (digits only)."""
    if not phone:
        return False, 'missing'
    phone = re.sub(r'[^\d]', '', phone)
    return len(phone) >= 10, 'valid' if len(phone) >= 10 else 'too_short'

def validate_lead(row, required_fields):
    """Validate a single lead row."""
    issues = []
    valid = True
    
    for field in required_fields:
        if field not in row or not row[field] or not str(row[field]).strip():
            issues.append(f"missing_{field}")
            valid = False
    
    return valid, issues

def validate_csv(input_path, output_path=None, required_fields=None):
    """Validate lead CSV file."""
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return False
    
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + '_validated.csv'
    
    print(f"Validating {input_path}...")
    
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if not headers:
                print("Error: No headers found in CSV.")
                return False
            
            if required_fields is None:
                required_fields = ['name']  # Default required field
            
            # Check required fields
            for field in required_fields:
                if field not in headers:
                    print(f"Error: Required field '{field}' not found in CSV headers.")
                    print(f"Available fields: {', '.join(headers)}")
                    return False
            
            valid_leads = []
            invalid_leads = []
            email_errors = {'missing': 0, 'invalid': 0}
            phone_errors = {'missing': 0, 'too_short': 0}
            
            for row in reader:
                lead_valid, issues = validate_lead(row, required_fields)
                
                # Check email if present
                email = row.get('email', '')
                if email:
                    is_valid, status = validate_email(email)
                    if not is_valid:
                        email_errors[status] += 1
                
                # Check phone if present
                phone = row.get('phone', '')
                if phone:
                    is_valid, status = validate_phone(phone)
                    if not is_valid:
                        phone_errors[status] += 1
                
                if lead_valid:
                    valid_leads.append(row)
                else:
                    invalid_leads.append((row, issues))
            
            # Write validated CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(valid_leads)
            
            # Print report
            print(f"✅ Validation Complete!")
            print(f"   - Total leads: {len(valid_leads) + len(invalid_leads)}")
            print(f"   - Valid leads: {len(valid_leads)}")
            print(f"   - Invalid leads: {len(invalid_leads)}")
            print(f"   - Email validation: {email_errors}")
            print(f"   - Phone validation: {phone_errors}")
            print(f"   - Output: {output_path}")
            
            if invalid_leads:
                print(f"\n⚠️ Invalid leads written to: {output_path.replace('_validated.csv', '_invalid.csv')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python lead-validator.py <input.csv> [output.csv] [--required name,email,phone]")
        print("\nExample:")
        print("  python lead-validator.py leads.csv validated_leads.csv")
        print("  python lead-validator.py data.csv output.csv --required name,email")
        sys.exit(0)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        required_fields = None
        if '--required' in sys.argv:
            idx = sys.argv.index('--required')
            if idx + 1 < len(sys.argv):
                required_fields = sys.argv[idx + 1].split(',')
        
        ok = validate_csv(input_file, output_file, required_fields)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
