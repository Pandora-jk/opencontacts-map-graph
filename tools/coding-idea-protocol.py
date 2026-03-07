#!/usr/bin/env python3
"""
Telegram-safe coding idea intake and Kanban staging.

Examples:
  python3 tools/coding-idea-protocol.py add \
    --project automation-scripts \
    --title "add csv schema validator" \
    --description "validate generated lead csv headers and types"

  python3 tools/coding-idea-protocol.py list --project automation-scripts
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path("/home/ubuntu/.openclaw/workspace")
KANBAN_DIR = ROOT / "departments" / "coding" / "kanban"
PRIORITY_FILE = ROOT / "memory" / "coding-priority.json"

PROJECTS = {
    "automation-scripts": "Automation scripts and micro-tools",
    "data-brokerage": "Lead/data product workflows",
    "research-reports": "Research generation and packaging",
    "workspace-core": "OpenClaw workspace/system tooling",
}

LANES = [
    "Backlog",
    "Ready",
    "In Progress",
    "Review",
    "Done",
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def board_path(project: str) -> Path:
    return KANBAN_DIR / f"{project}.md"


def ensure_board(project: str) -> None:
    KANBAN_DIR.mkdir(parents=True, exist_ok=True)
    p = board_path(project)
    if p.exists():
        return
    p.write_text(
        "\n".join(
            [
                f"# Kanban - {project}",
                "",
                f"Project scope: {PROJECTS.get(project, '')}",
                "",
                "## Backlog",
                "",
                "## Ready",
                "",
                "## In Progress",
                "",
                "## Review",
                "",
                "## Done",
                "",
            ]
        )
    )


def insert_card(text: str, lane: str, card: str) -> str:
    marker = f"## {lane}\n"
    if marker not in text:
        raise RuntimeError(f"Malformed board: missing lane '{lane}'")
    return text.replace(marker, marker + "\n" + card, 1)


def set_priority(project: str, full_card_title: str, branch: str, boosts: int = 3) -> None:
    PRIORITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project": project,
        "title": full_card_title,
        "branch": branch,
        "boosts_remaining": max(1, int(boosts)),
        "created_at_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    PRIORITY_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def infer_project(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("lead", "leads", "csv", "dataset", "brokerage", "scrape", "pipeline")):
        return "data-brokerage"
    if any(k in t for k in ("report", "research", "summary", "market", "pricing")):
        return "research-reports"
    if any(k in t for k in ("openclaw", "telegram", "workflow", "agent", "cron", "infra", "config")):
        return "workspace-core"
    return "automation-scripts"


def normalize_title(text: str) -> str:
    clean = " ".join(text.strip().split())
    clean = re.sub(r"^[\"'`]+|[\"'`]+$", "", clean)
    if len(clean) <= 90:
        return clean
    return clean[:87].rstrip() + "..."


def add_card(project: str, title: str, description: str, lane: str = "Ready", priority: bool = True) -> str:
    ensure_board(project)
    p = board_path(project)
    text = p.read_text(encoding="utf-8")
    today = dt.date.today().isoformat()
    task_slug = slugify(title)
    branch = f"feature/{project}-{task_slug}-{today}"
    full_card_title = f"**{title}** ({today})"
    card = (
        f"- [ ] {full_card_title}\n"
        f"  - branch: `{branch}`\n"
        f"  - tests: define before coding\n"
        f"  - notes: {description.strip()}\n"
    )
    new_text = insert_card(text, lane, card)
    p.write_text(new_text, encoding="utf-8")
    if priority:
        set_priority(project, full_card_title, branch)
    return branch


def list_cards(project: str) -> str:
    p = board_path(project)
    if not p.exists():
        return f"No board yet for {project}."
    return p.read_text()


def main() -> int:
    parser = argparse.ArgumentParser(description="Coding idea protocol")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add new idea as backlog card")
    p_add.add_argument("--project", required=True, choices=sorted(PROJECTS))
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--description", default="No description provided")
    p_add.add_argument("--lane", default="Ready", choices=LANES)
    p_add.add_argument("--no-priority", action="store_true")

    p_ingest = sub.add_parser("ingest", help="Ingest natural-language idea and stage in Ready")
    p_ingest.add_argument("--text", required=True)
    p_ingest.add_argument("--project", choices=sorted(PROJECTS), default=None)
    p_ingest.add_argument("--lane", default="Ready", choices=LANES)
    p_ingest.add_argument("--no-priority", action="store_true")

    p_list = sub.add_parser("list", help="Print board")
    p_list.add_argument("--project", required=True, choices=sorted(PROJECTS))

    args = parser.parse_args()
    if args.cmd == "add":
        branch = add_card(
            args.project,
            args.title,
            args.description,
            lane=args.lane,
            priority=not args.no_priority,
        )
        print("IDEA_STAGED_OK")
        print(f"project={args.project}")
        print(f"lane={args.lane}")
        print(f"branch={branch}")
        print(f"priority={'off' if args.no_priority else 'on'}")
        return 0
    if args.cmd == "ingest":
        text = args.text.strip()
        project = args.project or infer_project(text)
        title = normalize_title(text.split("\n", 1)[0])
        branch = add_card(
            project,
            title,
            text,
            lane=args.lane,
            priority=not args.no_priority,
        )
        print("IDEA_STAGED_OK")
        print(f"project={project}")
        print(f"lane={args.lane}")
        print(f"branch={branch}")
        print(f"priority={'off' if args.no_priority else 'on'}")
        return 0
    if args.cmd == "list":
        print(list_cards(args.project))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
