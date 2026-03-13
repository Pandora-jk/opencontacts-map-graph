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
import json
import re
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

from coding_feedback_loop import audit_feedback_loop, build_snapshot

ROOT = Path("/home/ubuntu/.openclaw/workspace")
CRON_JOBS_PATH = Path("/home/ubuntu/.openclaw/cron/jobs.json")
DEPARTMENTS = ("finance", "coding", "infra", "travel")
REMINDER_PREFIX = "Reminder: "


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


def run_cli(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def reminder_name(text: str) -> str:
    clean = " ".join(text.split()).strip()
    return f"{REMINDER_PREFIX}{clean}"


def parse_json_output(output: str) -> dict:
    text = output.strip()
    if not text:
        raise ValueError("empty JSON output")
    return json.loads(text)


def reminder_matches(job: dict) -> bool:
    payload = job.get("payload") or {}
    schedule = job.get("schedule") or {}
    delivery = job.get("delivery") or {}
    name = (job.get("name") or "").strip()
    message = (payload.get("message") or "").strip()
    return (
        job.get("sessionTarget") == "isolated"
        and payload.get("kind") == "agentTurn"
        and schedule.get("kind") == "at"
        and delivery.get("channel") == "telegram"
        and (name.startswith(REMINDER_PREFIX) or REMINDER_PREFIX in message)
    )


def extract_reminder_text(job: dict) -> str:
    payload = job.get("payload") or {}
    message = (payload.get("message") or "").strip()
    m = re.search(r"Return exactly:\s*Reminder:\s*(.+)$", message, flags=re.S)
    if m:
        return m.group(1).strip()
    name = (job.get("name") or "").strip()
    if name.startswith(REMINDER_PREFIX):
        return name[len(REMINDER_PREFIX) :].strip()
    return name or message


def default_telegram_target() -> str:
    payload = parse_json_output(CRON_JOBS_PATH.read_text(encoding="utf-8"))
    for job in payload.get("jobs") or []:
        delivery = job.get("delivery") or {}
        target = (delivery.get("to") or "").strip()
        if delivery.get("channel") == "telegram" and target:
            return target
    raise ValueError("no Telegram delivery target found in cron jobs")


def list_reminder_jobs() -> list[dict]:
    out = run_cli(["openclaw", "cron", "list", "--json"])
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip() or "openclaw cron list failed")
    payload = parse_json_output(out.stdout)
    jobs = payload.get("jobs") or []
    reminders = [job for job in jobs if reminder_matches(job)]
    reminders.sort(key=lambda job: ((job.get("schedule") or {}).get("at") or "", job.get("id") or ""))
    return reminders


def add_reminder(when: str, text: str) -> str:
    clean_text = " ".join(text.split()).strip()
    if not clean_text:
        raise ValueError("reminder text cannot be empty")
    out = run_cli(
        [
            "openclaw",
            "cron",
            "add",
            "--name",
            reminder_name(clean_text),
            "--at",
            when.strip(),
            "--session",
            "isolated",
            "--message",
            f"Return exactly: {reminder_name(clean_text)}",
            "--announce",
            "--channel",
            "telegram",
            "--to",
            default_telegram_target(),
            "--model",
            "nvidia/qwen/qwen3.5-397b-a17b",
            "--delete-after-run",
            "--json",
        ]
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip() or "openclaw cron add failed")
    payload = parse_json_output(out.stdout)
    job = payload.get("job") or payload
    schedule = job.get("schedule") or {}
    created_at = job.get("createdAtMs")
    created_at_utc = (
        dt.datetime.fromtimestamp(created_at / 1000, tz=dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if isinstance(created_at, (int, float))
        else ""
    )
    lines = [f"reminder created: id={job.get('id', '')}", f"scheduled={when.strip()}"]
    if created_at_utc:
        lines.append(f"created_at_utc={created_at_utc}")
    if schedule.get("at"):
        lines.append(f"next_run={schedule['at']}")
    return "\n".join(lines)


def format_reminder_list(reminders: list[dict]) -> str:
    if not reminders:
        return "no reminders"
    blocks = []
    for job in reminders:
        schedule = job.get("schedule") or {}
        blocks.append(
            "\n".join(
                [
                    f"id={job.get('id', '')}",
                    f"scheduled={schedule.get('at', '')}",
                    f"text={extract_reminder_text(job)}",
                ]
            )
        )
    return "\n\n".join(blocks)


def remove_reminder(job_id: str) -> str:
    out = run_cli(["openclaw", "cron", "rm", job_id, "--json"])
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip() or "openclaw cron rm failed")
    return f"reminder removed: id={job_id}"


def cmd_help() -> str:
    return (
        "Department Commands\n"
        "- /dept help\n"
        "- /dept status <all|finance|coding|infra|travel>\n"
        "- /dept todo <finance|coding|infra|travel> [limit]\n"
        "- /dept run <finance|coding|infra|travel>\n"
        "- /remind add --in <duration> --text <text>\n"
        "- /remind add --at <iso|duration> --text <text>\n"
        "- /remind list\n"
        "- /remind remove <job-id>\n"
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

    p_remind = sub.add_parser("remind")
    remind_sub = p_remind.add_subparsers(dest="remind_cmd", required=True)

    p_remind_add = remind_sub.add_parser("add")
    when_group = p_remind_add.add_mutually_exclusive_group(required=True)
    when_group.add_argument("--in", dest="in_time", help="Relative time such as 20m or 2h")
    when_group.add_argument("--at", dest="at_time", help="ISO time or relative duration such as 20m")
    p_remind_add.add_argument("--text", required=True, help="Reminder text")

    remind_sub.add_parser("list")

    p_remind_remove = remind_sub.add_parser("remove")
    p_remind_remove.add_argument("job_id")

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

    if args.cmd == "remind":
        try:
            if args.remind_cmd == "add":
                when = args.in_time or args.at_time
                print(add_reminder(when, args.text))
                return 0
            if args.remind_cmd == "list":
                print(format_reminder_list(list_reminder_jobs()))
                return 0
            if args.remind_cmd == "remove":
                print(remove_reminder(args.job_id))
                return 0
        except (RuntimeError, ValueError) as exc:
            print(f"reminder error: {exc}")
            return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
