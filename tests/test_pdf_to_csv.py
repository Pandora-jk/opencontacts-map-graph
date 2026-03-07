import importlib.util
import os
import sys
import tempfile
import types
import unittest
from unittest import mock
import io
import runpy


def load_pdf_to_csv_module():
    module_name = "pdf_to_csv_under_test"
    module_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", "pdf_to_csv.py"
    )
    fake_pdfplumber = types.SimpleNamespace(open=lambda *_args, **_kwargs: None)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, {"pdfplumber": fake_pdfplumber}):
        spec.loader.exec_module(module)
    return module


class _FakePage:
    def __init__(self, table):
        self._table = table

    def extract_table(self):
        return self._table


class _FakePdf:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class PdfToCsvTests(unittest.TestCase):
    def setUp(self):
        self.module = load_pdf_to_csv_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.pdf_path = os.path.join(self.tempdir.name, "input.pdf")
        with open(self.pdf_path, "wb") as f:
            f.write(b"%PDF-1.4")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_happy_path_writes_csv(self):
        output_csv = os.path.join(self.tempdir.name, "out.csv")
        fake_pdf = _FakePdf(
            pages=[
                _FakePage([["h1", "h2"], ["v1", None]]),
                _FakePage([["v2", "v3"]]),
            ]
        )
        with mock.patch.object(self.module.pdfplumber, "open", return_value=fake_pdf):
            ok = self.module.convert_pdf_to_csv(self.pdf_path, output_csv)

        self.assertTrue(ok)
        with open(output_csv, "r", encoding="utf-8") as f:
            content = f.read().strip().splitlines()
        self.assertEqual(content, ["h1,h2", "v1,", "v2,v3"])

    def test_corrupted_pdf_returns_false(self):
        with mock.patch.object(
            self.module.pdfplumber, "open", side_effect=ValueError("corrupted PDF")
        ):
            ok = self.module.convert_pdf_to_csv(self.pdf_path)
        self.assertFalse(ok)

    def test_empty_pdf_returns_false(self):
        fake_pdf = _FakePdf(pages=[_FakePage(None), _FakePage([])])
        with mock.patch.object(self.module.pdfplumber, "open", return_value=fake_pdf):
            ok = self.module.convert_pdf_to_csv(self.pdf_path)
        self.assertFalse(ok)

    def test_unsupported_encoding_returns_false(self):
        output_csv = os.path.join(self.tempdir.name, "bad.csv")
        fake_pdf = _FakePdf(pages=[_FakePage([["ok", "\udcff"]])])
        with mock.patch.object(self.module.pdfplumber, "open", return_value=fake_pdf):
            ok = self.module.convert_pdf_to_csv(self.pdf_path, output_csv)
        self.assertFalse(ok)

    def test_non_existent_pdf_returns_false(self):
        non_existent_path = os.path.join(self.tempdir.name, "non_existent.pdf")
        ok = self.module.convert_pdf_to_csv(non_existent_path)
        self.assertFalse(ok)



class PdfToCsvTests(unittest.TestCase):
    def setUp(self):
        self.module = load_pdf_to_csv_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.pdf_path = os.path.join(self.tempdir.name, "input.pdf")
        with open(self.pdf_path, "wb") as f:
            f.write(b"%PDF-1.4")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_happy_path_writes_csv(self):
        output_csv = os.path.join(self.tempdir.name, "out.csv")
        fake_pdf = _FakePdf(
            pages=[
                _FakePage([["h1", "h2"], ["v1", None]]),
                _FakePage([["v2", "v3"]]),
            ]
        )
        with mock.patch.object(self.module.pdfplumber, "open", return_value=fake_pdf):
            ok = self.module.convert_pdf_to_csv(self.pdf_path, output_csv)

        self.assertTrue(ok)
        with open(output_csv, "r", encoding="utf-8") as f:
            content = f.read().strip().splitlines()
        self.assertEqual(content, ["h1,h2", "v1,", "v2,v3"])

    def test_corrupted_pdf_returns_false(self):
        with mock.patch.object(
            self.module.pdfplumber, "open", side_effect=ValueError("corrupted PDF")
        ):
            ok = self.module.convert_pdf_to_csv(self.pdf_path)
        self.assertFalse(ok)

    def test_empty_pdf_returns_false(self):
        fake_pdf = _FakePdf(pages=[_FakePage(None), _FakePage([])])
        with mock.patch.object(self.module.pdfplumber, "open", return_value=fake_pdf):
            ok = self.module.convert_pdf_to_csv(self.pdf_path)
        self.assertFalse(ok)

    def test_unsupported_encoding_returns_false(self):
        output_csv = os.path.join(self.tempdir.name, "bad.csv")
        fake_pdf = _FakePdf(pages=[_FakePage([["ok", "\udcff"]])])
        with mock.patch.object(self.module.pdfplumber, "open", return_value=fake_pdf):
            ok = self.module.convert_pdf_to_csv(self.pdf_path, output_csv)
        self.assertFalse(ok)

    def test_non_existent_pdf_returns_false(self):
        non_existent_path = os.path.join(self.tempdir.name, "non_existent.pdf")
        ok = self.module.convert_pdf_to_csv(non_existent_path)
        self.assertFalse(ok)


class TestCliIntegration(unittest.TestCase):
    def setUp(self):
        self.module = load_pdf_to_csv_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.pdf_path = os.path.join(self.tempdir.name, "input.pdf")
        with open(self.pdf_path, "wb") as f:
            f.write(b"%PDF-1.4")

    def tearDown(self):
        self.tempdir.cleanup()

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("sys.argv", ["pdf_to_csv.py"])
    def test_main_no_args_prints_usage(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            self.module.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("Usage: python pdf_to_csv.py <input.pdf> [output.csv]", mock_stdout.getvalue())

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("sys.argv", ["pdf_to_csv.py", "input.pdf"])
    @mock.patch("pdf_to_csv_under_test.convert_pdf_to_csv", return_value=True)
    def test_main_one_arg_calls_convert(self, mock_convert, mock_stdout):
        import runpy
        with self.assertRaises(SystemExit) as cm:
            runpy.run_module('pdf_to_csv_under_test', run_name='__main__')
        mock_convert.assert_called_once_with("input.pdf", None)
        self.assertEqual(cm.exception.code, 0)

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("sys.argv", ["pdf_to_csv.py", "input.pdf", "output.csv"])
    @mock.patch("pdf_to_csv_under_test.convert_pdf_to_csv", return_value=True)
    def test_main_two_args_calls_convert(self, mock_convert, mock_stdout):
        import runpy
        with self.assertRaises(SystemExit) as cm:
            runpy.run_module('pdf_to_csv_under_test', run_name='__main__')
        mock_convert.assert_called_once_with("input.pdf", "output.csv")
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
