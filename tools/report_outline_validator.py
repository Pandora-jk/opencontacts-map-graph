#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = WORKSPACE_ROOT / "research-reports" / "report-outline-template.md"


def _normalize_heading(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extract_required_headings(path: Path) -> list[str]:
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(##)\s+(.+?)\s*$", line)
        if not match:
            continue
        headings.append(match.group(2).strip())
    return headings


def extract_present_headings(path: Path) -> set[str]:
    headings: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(##)\s+(.+?)\s*$", line)
        if not match:
            continue
        headings.add(_normalize_heading(match.group(2)))
    return headings


def validate_outline(outline_path: Path, template_path: Path = DEFAULT_TEMPLATE) -> list[str]:
    required = extract_required_headings(template_path)
    present = extract_present_headings(outline_path)
    return [heading for heading in required if _normalize_heading(heading) not in present]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a report outline against the template headings")
    parser.add_argument("outline", help="Path to the outline markdown file")
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="Path to the template markdown file",
    )
    args = parser.parse_args()

    outline_path = Path(args.outline)
    template_path = Path(args.template)

    missing = validate_outline(outline_path=outline_path, template_path=template_path)
    if missing:
        print("REPORT_OUTLINE_INVALID")
        for heading in missing:
            print(f"- missing section: {heading}")
        return 1

    print("REPORT_OUTLINE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
