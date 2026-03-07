# 📄 PDF to CSV Converter

**Professional-grade PDF table extraction for non-technical users.**

## [GO] What It Does

Converts tables in PDF files (invoices, reports, statements) into clean, editable CSV/Excel format instantly.

- [OK] Extracts tables from multi-page PDFs
- [OK] Handles messy formatting automatically
- [OK] Outputs clean CSV ready for Excel/Google Sheets
- [OK] No manual copy-pasting required

## 💰 Price: $9.99

Perfect for:
- Accountants processing invoices
- Researchers extracting data
- Businesses migrating legacy reports
- Anyone tired of manual data entry

## 📦 Installation

1. Install Python 3.6+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Usage

**Basic:**
```bash
python pdf_to_csv.py input.pdf
```
Creates `input.csv` in the same folder.

**Custom Output:**
```bash
python pdf_to_csv.py report.pdf cleaned_data.csv
```

## [TODO] Example

Input: `invoice.pdf` (table with 50 rows)  
Output: `invoice.csv` (ready for Excel)

```bash
$ python pdf_to_csv.py invoice.pdf
Converting invoice.pdf to invoice.csv...
[OK] Success! Converted 50 rows to invoice.csv
```

## [SEC] License

- Single User License
- Commercial use allowed
- No redistribution of the script itself

## 🆘 Troubleshooting

**"pdfplumber not installed"**  
→ Run: `pip install pdfplumber`

**"No tables found"**  
→ The PDF may contain images of tables (OCR required) or no detectable tables.

**"Error: File not found"**  
→ Ensure the PDF file exists in the current directory or provide full path.

## [MAIL] Support

Issues? Contact: pandora-support@yourdomain.com

---

**Author:** Pandora Automation  
**GitHub:** https://github.com/Pandor-jk/automation-scripts  
**Version:** 1.0
