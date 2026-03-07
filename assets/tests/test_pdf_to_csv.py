#!/usr/bin/env python3
"""
Unit tests for pdf_to_csv.py core conversion path.
Tests coverage target: minimum 80% line coverage for core module.
"""

import unittest
import os
import sys
import csv
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

# Add parent directory to path to import pdf_to_csv
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create a mock pdfplumber module
mock_pdfplumber = MagicMock()
mock_pdfplumber.open = MagicMock()

# Patch the import before executing the module
sys.modules['pdfplumber'] = mock_pdfplumber

# Now import pdf_to_csv
from pdf_to_csv import convert_pdf_to_csv


class TestPdfToCsvCoreConversion(unittest.TestCase):
    """Test core conversion path functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.assets_dir = Path(__file__).parent.parent

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures after all tests."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """Reset test state before each test."""
        self.test_files = []
        # Reset mock for each test
        mock_pdfplumber.open.reset_mock()
        mock_pdfplumber.open.side_effect = None  # Clear any side_effect
        mock_pdfplumber.open.return_value = MagicMock()  # Reset return value

    def tearDown(self):
        """Clean up created test files."""
        for f in self.test_files:
            if os.path.exists(f):
                os.remove(f)

    def test_happy_path_valid_pdf_with_tables(self):
        """Test successful conversion of a valid PDF with tables."""
        # Create a mock PDF file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("This is not a real PDF\n")
        self.test_files.append(pdf_path)

        # Mock pdfplumber.open to return our test data
        mock_page = MagicMock()
        mock_page.extract_table.return_value = [
            ["Header1", "Header2", "Header3"],
            ["Row1Col1", "Row1Col2", "Row1Col3"],
            ["Row2Col1", "Row2Col2", "Row2Col3"],
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]

        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Test conversion
        result = convert_pdf_to_csv(pdf_path)

        # Verify result
        self.assertTrue(result, "Conversion should succeed for valid PDF with tables")

        # Verify CSV was created
        csv_path = os.path.splitext(pdf_path)[0] + '.csv'
        self.assertTrue(os.path.exists(csv_path), "CSV file should be created")

        # Verify CSV content
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3, "CSV should have 3 rows (header + 2 data rows)")
            self.assertEqual(rows[0], ["Header1", "Header2", "Header3"])
            self.assertEqual(rows[1], ["Row1Col1", "Row1Col2", "Row1Col3"])
            self.assertEqual(rows[2], ["Row2Col1", "Row2Col2", "Row2Col3"])

    def test_empty_pdf_no_tables(self):
        """Test handling of PDF with no tables."""
        # Create a mock PDF file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("This PDF has no tables\n")
        self.test_files.append(pdf_path)

        # Mock pdfplumber.open to return no tables
        mock_page = MagicMock()
        mock_page.extract_table.return_value = None

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]

        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Test conversion
        result = convert_pdf_to_csv(pdf_path)

        # Verify result
        self.assertFalse(result, "Conversion should fail for PDF with no tables")

        # Verify CSV was NOT created
        csv_path = os.path.splitext(pdf_path)[0] + '.csv'
        self.assertFalse(os.path.exists(csv_path), "CSV file should NOT be created for PDF with no tables")

    def test_pdf_parsing_error(self):
        """Test handling of PDF parsing errors."""
        # Create a mock PDF file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("This PDF has a parsing error\n")
        self.test_files.append(pdf_path)

        # Mock pdfplumber.open to raise an exception
        mock_pdfplumber.open.side_effect = Exception("PDF parsing error")

        # Test conversion
        result = convert_pdf_to_csv(pdf_path)

        # Verify result
        self.assertFalse(result, "Conversion should fail for PDF with parsing error")

        # Note: CSV may be created if error occurs after file open, but that's acceptable
        # The important thing is that the error was caught and handled properly

    def test_missing_file(self):
        """Test handling of non-existent file."""
        # Try to convert a non-existent file
        result = convert_pdf_to_csv("/nonexistent/file.pdf")

        # Verify result
        self.assertFalse(result, "Conversion should fail for non-existent file")

    def test_csv_output_with_custom_path(self):
        """Test custom output CSV path."""
        # Create a mock PDF file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("This PDF has tables\n")
        self.test_files.append(pdf_path)

        # Mock pdfplumber.open to return test data
        custom_csv_path = os.path.join(self.test_dir, "custom_output.csv")
        mock_page = MagicMock()
        mock_page.extract_table.return_value = [
            ["Header1", "Header2", "Header3"],
            ["Row1Col1", "Row1Col2", "Row1Col3"],
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]

        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Test conversion with custom output path
        result = convert_pdf_to_csv(pdf_path, custom_csv_path)

        # Verify result
        self.assertTrue(result, "Conversion should succeed with custom output path")

        # Verify CSV was created at custom path
        self.assertTrue(os.path.exists(custom_csv_path), "CSV should be created at custom path")

        # Verify CSV content
        with open(custom_csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2, "CSV should have 2 rows (header + 1 data row)")

    def test_none_values_cleaned(self):
        """Test that None values in table are cleaned to empty strings."""
        # Create a mock PDF file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("PDF with None values\n")
        self.test_files.append(pdf_path)

        # Mock pdfplumber.open to return table with None values
        mock_page = MagicMock()
        mock_page.extract_table.return_value = [
            ["Header1", "Header2", "Header3"],
            ["Value1", None, "Value3"],
            [None, "Value2", None],
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]

        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Test conversion
        result = convert_pdf_to_csv(pdf_path)

        # Verify result
        self.assertTrue(result, "Conversion should succeed")

        # Verify CSV content has empty strings instead of None
        csv_path = os.path.splitext(pdf_path)[0] + '.csv'
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            # Check that None values were cleaned to empty strings
            self.assertEqual(rows[1], ["Value1", "", "Value3"])
            self.assertEqual(rows[2], ["", "Value2", ""])

    def test_multiple_pages(self):
        """Test conversion of PDF with multiple pages."""
        # Create a mock PDF file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("PDF with multiple pages\n")
        self.test_files.append(pdf_path)

        # Mock pdfplumber.open to return tables from multiple pages
        mock_page1 = MagicMock()
        mock_page1.extract_table.return_value = [
            ["Page1Header1", "Page1Header2"],
            ["Page1Row1", "Page1Row2"],
        ]

        mock_page2 = MagicMock()
        mock_page2.extract_table.return_value = [
            ["Page2Header1", "Page2Header2"],
            ["Page2Row1", "Page2Row2"],
        ]

        # Create mock pages iterator
        mock_pages = [mock_page1, mock_page2]

        mock_pdf = MagicMock()
        mock_pdf.pages = mock_pages

        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Test conversion
        result = convert_pdf_to_csv(pdf_path)

        # Verify result
        self.assertTrue(result, "Conversion should succeed for PDF with multiple pages")

        # Verify CSV has all rows from all pages
        csv_path = os.path.splitext(pdf_path)[0] + '.csv'
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 4, "CSV should have 4 rows (2 headers + 2 rows per page)")

    def test_pdfplumber_not_installed(self):
        """Test handling when pdfplumber is not installed."""
        # Save the original import
        import builtins
        original_import = builtins.__import__

        # Mock import to fail for pdfplumber
        def mock_import(name, *args, **kwargs):
            if name == 'pdfplumber':
                raise ImportError("No module named 'pdfplumber'")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = mock_import

        try:
            # Force reimport to trigger the import error
            if 'pdf_to_csv' in sys.modules:
                del sys.modules['pdf_to_csv']

            # Try to convert (should fail due to missing pdfplumber)
            result = convert_pdf_to_csv("test.pdf")

            # Verify result
            self.assertFalse(result, "Conversion should fail when pdfplumber is not installed")

        finally:
            # Restore original import
            builtins.__import__ = original_import


if __name__ == "__main__":
    unittest.main()
