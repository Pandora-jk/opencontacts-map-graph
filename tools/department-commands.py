#!/usr/bin/env python3
"""
On-demand department commands for Telegram/operator usage.

Examples:
  python3 tools/department-commands.py help
  python3 tools/department-commands.py status all
  python3 tools/department-commands.py status finance
  python3 tools/department-commands.py todo coding --limit 5
  python3 tools/department-commands.py run finance
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

from coding_feedback_loop import audit_feedback_loop, build_snapshot

ROOT = Path("/home/ubuntu/.openclaw/workspace")
DEPARTMENTS = ("finance", "coding", "infra", "travel")


def todo_path(dept: str) -> Path:
    return ROOT / "departments" / dept / "TODO.md"


def parse_todo_counts(text: str) -> dict[str, int]:
    counts = {"open": 0, "done": 0, "in_progress": 0}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- [ ]"):
            counts["open"] += 1
        elif line.startswith("- [x]"):
            counts["done"] += 1
        elif line.startswith("- [~]"):
            counts["in_progress"] += 1
    return counts


def list_open_tasks(text: str, limit: int) -> list[str]:
    tasks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- [ ]"):
            task = re.sub(r"^- \[ \]\s*", "", line).strip()
            tasks.append(task)
        if len(tasks) >= limit:
            break
    return tasks


def coding_kanban_snapshot() -> str:
    base = ROOT / "departments" / "coding" / "kanban"
    if not base.exists():
        return "kanban: n/a"
    files = sorted([p for p in base.glob("*.md") if p.name != "README.md"])
    ready = 0
    in_progress = 0
    for p in files:
        txt = p.read_text(encoding="utf-8")
        m_ready = re.search(r"^## Ready\n([\s\S]*?)(?=^## |\Z)", txt, flags=re.M)
        if m_ready:
            ready += len(re.findall(r"^- \[ \]", m_ready.group(1), flags=re.M))
        m_ip = re.search(r"^## In Progress\n([\s\S]*?)(?=^## |\Z)", txt, flags=re.M)
        if m_ip:
            in_progress += len(re.findall(r"^- \[.\]", m_ip.group(1), flags=re.M))
    return f"kanban_files={len(files)} ready_cards={ready} in_progress_cards={in_progress}"


def coding_feedback_snapshot() -> str:
    _, summary = audit_feedback_loop(ROOT)
    return build_snapshot(summary)


def coding_ready_cards(limit: int) -> list[str]:
    base = ROOT / "departments" / "coding" / "kanban"
    if not base.exists():
        return []
    cards: list[str] = []
    for p in sorted([x for x in base.glob("*.md") if x.name != "README.md"]):
        txt = p.read_text(encoding="utf-8")
        m_ready = re.search(r"^## Ready\n([\s\S]*?)(?=^## |\Z)", txt, flags=re.M)
        if not m_ready:
            continue
        title = ""
        for raw in m_ready.group(1).splitlines():
            line = raw.strip()
            if line.startswith("- [ ]"):
                title = re.sub(r"^- \[ \]\s*", "", line).strip()
            elif line.startswith("- tests:") and title:
                cards.append(title)
                title = ""
            if len(cards) >= limit:
                return cards
    return cards


def last_finance_activity() -> str:
    p = ROOT / "logs" / "finance-activity.log"
    if not p.exists():
        return "none"
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return lines[-1] if lines else "none"


def status_for(dept: str) -> str:
    p = todo_path(dept)
    if not p.exists():
        return f"{dept}: TODO missing"
    txt = p.read_text(encoding="utf-8")
    c = parse_todo_counts(txt)
    extras = []
    if dept == "finance":
        extras.append(f"last_activity={last_finance_activity()}")
    if dept == "coding":
        extras.append(coding_kanban_snapshot())
        extras.append(coding_feedback_snapshot())
    extra_str = f" | {'; '.join(extras)}" if extras else ""
    return f"{dept}: open={c['open']} in_progress={c['in_progress']} done={c['done']}{extra_str}"


def run_finance() -> str:
    cmd = ["python3", str(ROOT / "tools" / "finance-autopilot.py"), "--emit-telegram"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        return f"finance run failed: {out.stderr.strip() or out.stdout.strip()}"
    return out.stdout.strip()


def run_script(script_name: str, *, emit_telegram: bool = True) -> str:
    cmd = ["python3", str(ROOT / "tools" / script_name)]
    if emit_telegram:
        cmd.append("--emit-telegram")
    out = subprocess.run(cmd, capture_output=True, text=True)
    text = (out.stdout.strip() or out.stderr.strip()).strip()
    if out.returncode == 0:
        return text or f"{script_name}: run ok"
    return f"{script_name}: run failed ({out.returncode}) {text}"


def run_night_delegate(dept: str) -> str:
    cmd = [str(ROOT / "tools" / "night-department-runner.sh"), dept]
    out = subprocess.run(cmd, capture_output=True, text=True)
    text = (out.stdout.strip() or out.stderr.strip()).strip()
    if out.returncode == 0:
        return text or f"{dept}: run ok"
    return f"{dept}: run failed ({out.returncode}) {text}"


def run_department(dept: str) -> str:
    if dept == "finance":
        return run_finance()
    if dept == "coding":
        # Daytime uses deterministic coding autopilot; night can still delegate.
        hour = int(dt.datetime.now(ZoneInfo("Australia/Sydney")).strftime("%H"))
        if 0 <= hour < 6:
            return run_night_delegate("coding")
        return run_script("coding-autopilot.py")
    if dept == "infra":
        # Refresh live status first so on-demand infra runs do not score stale artifacts.
        status_output = run_script("infra-status.py", emit_telegram=False)
        autopilot_output = run_script("infra-autopilot.py")
        if status_output.startswith("infra-status.py: run failed"):
            return f"{autopilot_output}\nStatus refresh: {status_output}"
        return autopilot_output
    if dept == "travel":
        return run_script("travel-autopilot.py")
    return f"{dept}: unsupported"


def cmd_help() -> str:
    return (
        "Department Commands\n"
        "- /dept help\n"
        "- /dept status <all|finance|coding|infra|travel>\n"
        "- /dept todo <finance|coding|infra|travel> [limit]\n"
        "- /dept run <finance|coding|infra|travel>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Department on-demand commands")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("help")
    p_status = sub.add_parser("status")
    p_status.add_argument("department", help="all or department name")

    p_todo = sub.add_parser("todo")
    p_todo.add_argument("department", choices=DEPARTMENTS)
    p_todo.add_argument("--limit", type=int, default=5)

    p_run = sub.add_parser("run")
    p_run.add_argument("department", choices=DEPARTMENTS)

    args = parser.parse_args()

    if args.cmd == "help":
        print(cmd_help())
        return 0

    if args.cmd == "status":
        d = args.department.lower()
        if d == "all":
            print("\n".join(status_for(x) for x in DEPARTMENTS))
            return 0
        if d not in DEPARTMENTS:
            print(f"Unknown department: {d}")
            return 2
        print(status_for(d))
        return 0

    if args.cmd == "todo":
        if args.department == "coding":
            cards = coding_ready_cards(max(1, args.limit))
            if not cards:
                print("coding: no Ready cards")
                return 0
            print("\n".join(f"- {c}" for c in cards))
            return 0
        txt = todo_path(args.department).read_text(encoding="utf-8")
        tasks = list_open_tasks(txt, max(1, args.limit))
        if not tasks:
            print(f"{args.department}: no open tasks")
            return 0
        print("\n".join(f"- {t}" for t in tasks))
        return 0

    if args.cmd == "run":
        print(run_department(args.department))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
