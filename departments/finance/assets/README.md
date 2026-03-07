# Micro-Automation Bundle

**Price:** $27 AUD for all 3 scripts
**Delivery:** Instant digital download
**License:** Single User (Commercial Use Allowed)

## What's Included

### 1. PDF-to-CSV Utility
Converts tables in PDF files to clean CSV format. Perfect for invoices, reports, and data extraction.

**Features:**
- Automatic table detection
- Clean row formatting
- Multiple output options
- Error handling

**Use Cases:**
- Invoice data extraction
- Report automation
- Form data processing

### 2. CSV Cleaner & Standardizer
Standardize and clean your CSV files for consistent data quality.

**Features:**
- Remove duplicate rows
- Normalize column headers (trim, lowercase, replace spaces)
- Handle missing values
- Validate required columns

**Use Cases:**
- Lead list cleanup
- Data standardization
- Quality control

### 3. Lead List Validator
Validate email addresses, check required fields, and remove invalid entries.

**Features:**
- Email validation (basic format check)
- Phone number validation
- Required field validation
- Detailed validation report

**Use Cases:**
- Lead list verification
- Data quality assurance
- Contact list cleanup

## Installation

### PDF-to-CSV
```bash
pip install pdfplumber
python pdf_to_csv.py input.pdf [output.csv]
```

### CSV Cleaner
```bash
python csv-cleaner.py input.csv [output.csv] [--required col1,col2]
```

### Lead Validator
```bash
python lead-validator.py input.csv [output.csv] [--required name,email,phone]
```

## Requirements

- Python 3.7+
- Standard library only (except pdfplumber for PDF conversion)

## Support

- Single user license
- Commercial use allowed
- Contact for support: pandora@automation.example.com

## License

**Single User License**
- For personal or business use by one individual
- Commercial use is permitted
- No redistribution without permission
