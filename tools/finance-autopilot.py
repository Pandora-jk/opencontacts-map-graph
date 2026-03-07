#!/usr/bin/env python3
"""
Finance autopilot loop with concrete execution artifacts.

Each run:
- Reads finance TODO and state
- Selects an autonomous task (round-robin)
- Executes one concrete micro-step and writes an artifact file
- Writes departments/finance/STATUS.md with progress details
- Appends logs/finance-activity.log
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Callable

ROOT = Path("/home/ubuntu/.openclaw/workspace")
FIN_DIR = ROOT / "departments" / "finance"
TODO_FILE = FIN_DIR / "TODO.md"
STATUS_FILE = FIN_DIR / "STATUS.md"
INCOME_FILE = ROOT / "INCOME-ENGINE.md"
ACTIVITY_LOG = ROOT / "logs" / "finance-activity.log"
STATE_FILE = ROOT / "memory" / "finance-autopilot-state.json"
ARTIFACTS_DIR = FIN_DIR / "artifacts"


def parse_todo_sections(text: str) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    autonomous: list[str] = []
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if "User Blocking" in line:
            section = "blocking"
            continue
        if "Autonomous Queue" in line:
            section = "autonomous"
            continue
        if line.startswith("## "):
            section = ""
            continue
        if line.startswith("- [ ]"):
            task = re.sub(r"^- \[ \]\s*", "", line).strip()
            if section == "blocking":
                blocking.append(task)
            elif section == "autonomous":
                autonomous.append(task)
    return blocking, autonomous


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"runs": 0, "last_primary_task": "", "task_cursor": 0, "task_progress": {}}
    try:
        state = json.loads(STATE_FILE.read_text())
        if "task_progress" not in state or not isinstance(state["task_progress"], dict):
            state["task_progress"] = {}
        if "task_cursor" not in state or not isinstance(state["task_cursor"], int):
            state["task_cursor"] = 0
        if "runs" not in state:
            state["runs"] = 0
        if "last_primary_task" not in state:
            state["last_primary_task"] = ""
        return state
    except json.JSONDecodeError:
        return {"runs": 0, "last_primary_task": "", "task_cursor": 0, "task_progress": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def opportunity_candidates() -> list[dict]:
    return [
        {
            "idea": "Local lead pack subscription (weekly niche CSV refresh)",
            "speed": 4,
            "effort": 3,
            "risk": 2,
            "upside": 4,
            "first_action": "Build a 50-row sample + weekly update offer page",
        },
        {
            "idea": "Micro-automation gig bundle (PDF/CSV + cleanup scripts)",
            "speed": 5,
            "effort": 2,
            "risk": 1,
            "upside": 3,
            "first_action": "Package 3 scripts with fixed-price tiers",
        },
        {
            "idea": "Niche outreach templates pack (AU local trades)",
            "speed": 4,
            "effort": 2,
            "risk": 1,
            "upside": 3,
            "first_action": "Create 10 templates + sample personalization guide",
        },
        {
            "idea": "Monthly data maintenance retainer",
            "speed": 2,
            "effort": 4,
            "risk": 2,
            "upside": 5,
            "first_action": "Draft recurring scope + SLA pricing sheet",
        },
        {
            "idea": "Affiliate layer for currently shipped tooling",
            "speed": 3,
            "effort": 2,
            "risk": 1,
            "upside": 3,
            "first_action": "Add recommended tools section to product README pages",
        },
    ]


def score(idea: dict) -> int:
    # Higher is better: speed/upside positive, effort/risk negative.
    return (idea["speed"] * 3) + (idea["upside"] * 3) - (idea["effort"] * 2) - (idea["risk"] * 2)


def slugify(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out[:64] or "task"


def clean_text(value: str) -> str:
    txt = re.sub(r"[*_`]+", "", value or "")
    return re.sub(r"\s+", " ", txt).strip()


def pick_primary_task(autonomous: list[str], state: dict) -> tuple[str, int]:
    if not autonomous:
        return "No autonomous task queued", 0
    idx = int(state.get("task_cursor", 0)) % len(autonomous)
    return autonomous[idx], idx


def write_artifact(rel_path: str, content: str) -> Path:
    artifact = ARTIFACTS_DIR / rel_path
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(content, encoding="utf-8")
    return artifact


def action_daily_cash(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Short-Cycle Offer Draft (Run {run_id})\n\n"
        f"- Generated at: {now.isoformat().replace('+00:00', 'Z')}\n"
        "- Offer: Script-fix sprint (24h delivery)\n"
        "- Price anchor: AUD 49 (basic), AUD 99 (priority)\n"
        "- CTA: Reply with repo link + issue list\n"
    )
    return write_artifact(f"offers/short-cycle-offer-{now:%Y%m%d}-r{run_id}.md", content)


def action_recurring(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Monthly Retainer Offer (Run {run_id})\n\n"
        f"- Generated at: {now.isoformat().replace('+00:00', 'Z')}\n"
        "- Package: Weekly data refresh + QA + delivery\n"
        "- SLA: 48h turnaround\n"
        "- Pricing: AUD 299 / month starter tier\n"
    )
    return write_artifact(f"retainers/monthly-retainer-{now:%Y%m%d}-r{run_id}.md", content)


def action_pipeline(now: dt.datetime, run_id: int) -> Path:
    lines = ["name,city,state,category,contact_hint"]
    for i in range(1, 51):
        lines.append(f"Solar Wholesaler {i},Melbourne,VIC,solar,info{i}@example.com")
    content = "\n".join(lines) + "\n"
    return write_artifact(f"pipeline/solar-wholesalers-50-{now:%Y%m%d}-r{run_id}.csv", content)


def action_outreach_templates(now: dt.datetime, run_id: int) -> Path:
    blocks = [f"# Outreach Templates (Run {run_id})", ""]
    for i in range(1, 6):
        blocks.extend(
            [
                f"## Template {i}",
                "Subject: Quick fix to reduce admin time this week",
                "Body: Hi {{name}}, we can automate your recurring admin task in 24h. "
                "Want a fixed-price scope?",
                "",
            ]
        )
    return write_artifact(f"templates/plumbing-melbourne-5-{now:%Y%m%d}-r{run_id}.md", "\n".join(blocks))


def action_opportunity_scan(now: dt.datetime, run_id: int) -> Path:
    ranked = sorted(opportunity_candidates(), key=score, reverse=True)[:3]
    lines = [f"# Opportunity Scan (Run {run_id})", ""]
    for i, item in enumerate(ranked, start=1):
        lines.append(f"{i}. {item['idea']} | score={score(item)} | next={item['first_action']}")
    lines.append("")
    return write_artifact(f"scans/opportunity-scan-{now:%Y%m%d}-r{run_id}.md", "\n".join(lines))


def action_asset_inventory(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Asset Inventory (Run {run_id})\n\n"
        "| SKU | Asset | Price (AUD) | Delivery |\n"
        "|---|---|---:|---|\n"
        "| SKU-001 | PDF-to-CSV utility | 29 | digital download |\n"
        "| SKU-002 | Solar leads starter pack | 49 | CSV file |\n"
        "| SKU-003 | Outreach template bundle | 19 | markdown pack |\n"
        f"\nGenerated: {now.isoformat().replace('+00:00', 'Z')}\n"
    )
    return write_artifact(f"inventory/sku-inventory-{now:%Y%m%d}-r{run_id}.md", content)


def execute_primary_task(primary: str, state: dict) -> Path | None:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0)
    run_id = int(state.get("runs", 0))
    task_lower = primary.lower()
    actions: list[tuple[str, Callable[[dt.datetime, int], Path]]] = [
        ("daily cash task", action_daily_cash),
        ("recurring income task", action_recurring),
        ("pipeline expansion", action_pipeline),
        ("offer testing", action_outreach_templates),
        ("opportunity scan", action_opportunity_scan),
        ("build asset inventory", action_asset_inventory),
    ]
    for key, action in actions:
        if key in task_lower:
            return action(now, run_id)
    # Fallback: generic artifact if task wording changes.
    content = (
        f"# Finance Task Note (Run {run_id})\n\n"
        f"- Task: {primary}\n"
        f"- Executed at: {now.isoformat().replace('+00:00', 'Z')}\n"
        "- Next: refine into concrete offer/listing in next loop.\n"
    )
    return write_artifact(f"notes/{slugify(primary)}-{now:%Y%m%d}-r{run_id}.md", content)


def build_status(
    blocking: list[str], autonomous: list[str], state: dict, primary: str, artifact: Path | None
) -> tuple[str, str]:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    ranked = sorted(opportunity_candidates(), key=score, reverse=True)[:3]
    top = ranked[0] if ranked else None
    progress = state.get("task_progress", {})
    primary_count = int(progress.get(primary, 0)) if primary in progress else 0
    artifact_rel = str(artifact.relative_to(ROOT)) if artifact else "none"
    primary_clean = clean_text(primary)

    lines = [
        "# Finance Status",
        "",
        f"- Last run (UTC): {now}",
        f"- Run count: {state.get('runs', 0)}",
        f"- Primary task: {primary}",
        f"- Primary task progress count: {primary_count}",
        f"- Last artifact: {artifact_rel}",
        f"- Blocking items: {len(blocking)}",
        f"- Autonomous queue items: {len(autonomous)}",
        "",
        "## Top Opportunities (scored)",
    ]
    for i, item in enumerate(ranked, start=1):
        lines.append(
            f"{i}. {item['idea']} | score={score(item)} | speed={item['speed']} effort={item['effort']} risk={item['risk']} upside={item['upside']}"
        )
    lines.extend(
        [
            "",
            "## Next Action",
            top["first_action"] if top else "No opportunity available",
            "",
            "## Blocking",
        ]
    )
    if blocking:
        lines.extend([f"- {b}" for b in blocking])
    else:
        lines.append("- None")

    status_text = "\n".join(lines) + "\n"

    telegram = [
        "[FINANCE UPDATE]",
        f"Time (UTC): {now}",
        f"Run: {state.get('runs', 0)}",
        f"Primary Task: {primary_clean}",
        f"Progress: {primary_count}",
        f"Queue: {len(autonomous)}",
        f"Blocking: {len(blocking)}",
        f"Artifact: {artifact_rel}",
        "Top Opportunities:",
    ]
    for i, item in enumerate(ranked, start=1):
        telegram.append(f"{i}. {clean_text(item['idea'])} (score {score(item)})")
    telegram.append(f"Next: {clean_text(top['first_action']) if top else 'No next action'}")
    return status_text, "\n".join(telegram)


def append_activity(summary: str) -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    with ACTIVITY_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{now}] {summary}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Finance autopilot loop")
    parser.add_argument("--emit-telegram", action="store_true", help="Print Telegram-formatted summary to stdout")
    args = parser.parse_args()

    if not TODO_FILE.exists():
        print("Finance TODO not found.")
        return 1

    todo = TODO_FILE.read_text(encoding="utf-8")
    blocking, autonomous = parse_todo_sections(todo)

    state = load_state()
    state["runs"] = int(state.get("runs", 0)) + 1
    primary, idx = pick_primary_task(autonomous, state)
    state["last_primary_task"] = primary if autonomous else ""
    state["task_cursor"] = (idx + 1) if autonomous else 0
    artifact = execute_primary_task(primary, state)
    progress = state.setdefault("task_progress", {})
    progress[primary] = int(progress.get(primary, 0)) + (1 if autonomous else 0)
    save_state(state)

    status_text, telegram_text = build_status(blocking, autonomous, state, primary, artifact)
    STATUS_FILE.write_text(status_text, encoding="utf-8")
    artifact_rel = str(artifact.relative_to(ROOT)) if artifact else "none"
    append_activity(
        f"run={state['runs']} primary='{state['last_primary_task']}' artifact='{artifact_rel}' "
        f"blocking={len(blocking)} queue={len(autonomous)}"
    )

    if args.emit_telegram:
        print(telegram_text)
    else:
        print(status_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
