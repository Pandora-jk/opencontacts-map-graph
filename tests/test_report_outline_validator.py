import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from report_outline_validator import validate_outline


class ReportOutlineValidatorTests(unittest.TestCase):
    def test_validate_outline_accepts_template_complete_outline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "template.md"
            outline = root / "outline.md"

            template.write_text(
                "# Template\n\n"
                "## Working Title\n"
                "## Target Reader\n"
                "## Commercial Promise\n",
                encoding="utf-8",
            )
            outline.write_text(
                "# Outline\n\n"
                "## Working Title\n"
                "Draft\n\n"
                "## Target Reader\n"
                "Founder\n\n"
                "## Commercial Promise\n"
                "Decision clarity\n",
                encoding="utf-8",
            )

            self.assertEqual(validate_outline(outline, template), [])

    def test_validate_outline_reports_missing_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "template.md"
            outline = root / "outline.md"

            template.write_text(
                "# Template\n\n"
                "## Working Title\n"
                "## Pricing and Packaging\n",
                encoding="utf-8",
            )
            outline.write_text(
                "# Outline\n\n"
                "## Working Title\n"
                "Draft\n",
                encoding="utf-8",
            )

            self.assertEqual(validate_outline(outline, template), ["Pricing and Packaging"])


if __name__ == "__main__":
    unittest.main()
