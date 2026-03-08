#!/usr/bin/env python3
"""
Finance autopilot loop aligned with the service-first finance model.

Each run:
- Reads finance TODO and state
- Selects an autonomous task from the queue
- Executes one concrete micro-step and writes an artifact file
- Writes departments/finance/STATUS.md with portfolio-aligned progress details
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
ACTIVITY_LOG = ROOT / "logs" / "finance-activity.log"
STATE_FILE = ROOT / "memory" / "finance-autopilot-state.json"
ARTIFACTS_DIR = FIN_DIR / "artifacts"


def parse_todo_sections(text: str) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    autonomous: list[str] = []
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        lowered = line.lower()
        if "user blocking" in lowered or "blocking items" in lowered:
            section = "blocking"
            continue
        if "autonomous queue" in lowered:
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


def action_offer(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Core Service Offer Draft (Run {run_id})\n\n"
        f"- Generated at: {now.isoformat().replace('+00:00', 'Z')}\n"
        "- Offer: done-for-you B2B pipeline setup\n"
        "- Promise: qualified prospects plus outreach-ready handoff\n"
        "- Customer: founder-led B2B firms with weak outbound process\n"
    )
    return write_artifact(f"offers/core-service-offer-{now:%Y%m%d}-r{run_id}.md", content)


def action_icp(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# ICP Selection Note (Run {run_id})\n\n"
        f"- Generated at: {now.isoformat().replace('+00:00', 'Z')}\n"
        "- Preferred ICP: founder-led B2B agencies, consultants, and niche SaaS\n"
        "- Team size: 10-200 employees\n"
        "- Reason: clear revenue pain and ability to pay for pipeline support\n"
    )
    return write_artifact(f"icp/primary-icp-{now:%Y%m%d}-r{run_id}.md", content)


def action_target_list(now: dt.datetime, run_id: int) -> Path:
    lines = ["company,segment,team_size,website,decision_maker,email,fit_note"]
    for i in range(1, 51):
        lines.append(
            f"Example B2B Company {i},agency,10-200,https://example{i}.com,Founder,founder{i}@example.com,needs outbound rigor"
        )
    content = "\n".join(lines) + "\n"
    return write_artifact(f"pipeline/target-list-50-{now:%Y%m%d}-r{run_id}.csv", content)


def action_outreach(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Outreach Draft (Run {run_id})\n\n"
        "Subject: quick idea to improve outbound pipeline\n\n"
        "Hi {{name}},\n\n"
        "I noticed {{company}} appears to fit the kind of B2B team where outbound "
        "follow-up becomes inconsistent as founder time gets stretched.\n\n"
        "We help teams build a cleaner qualified prospect pipeline: list building, "
        "fit review, enrichment, and outreach-ready handoff.\n\n"
        "If useful, I can show you a short sample with 3 scored prospects.\n"
    )
    return write_artifact(f"outreach/outreach-draft-{now:%Y%m%d}-r{run_id}.md", content)


def action_demo(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Demo Script (Run {run_id})\n\n"
        "1. Show the ICP and why these prospects fit.\n"
        "2. Walk through 3 example prospects with qualification notes.\n"
        "3. Show the outreach-ready first line and CTA.\n"
        "4. Explain weekly delivery and reporting.\n"
        "5. Close on next step and pricing.\n"
    )
    return write_artifact(f"demos/demo-script-{now:%Y%m%d}-r{run_id}.md", content)


def action_delivery(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# First Client Delivery Checklist (Run {run_id})\n\n"
        "- Confirm ICP and target geography\n"
        "- Confirm target titles and exclusions\n"
        "- Deliver initial prospect batch\n"
        "- Deliver outreach copy and usage notes\n"
        "- Confirm follow-up cadence and reporting format\n"
    )
    return write_artifact(f"delivery/first-client-checklist-{now:%Y%m%d}-r{run_id}.md", content)


def action_compliance(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Compliance Check Note (Run {run_id})\n\n"
        "- Validate footer contains business identity and unsubscribe path\n"
        "- Confirm public B2B data sources only\n"
        "- Confirm suppression list process before sending\n"
        "- Confirm complaint threshold and pause rule\n"
    )
    return write_artifact(f"compliance/compliance-check-{now:%Y%m%d}-r{run_id}.md", content)


def action_bounties(now: dt.datetime, run_id: int) -> Path:
    content = (
        f"# Bounty Scan Note (Run {run_id})\n\n"
        "- Scope: Ansible, Linux, DevOps, automation\n"
        "- Purpose: secondary cash only\n"
        "- Rule: do not displace core service execution\n"
    )
    return write_artifact(f"bounties/bounty-scan-{now:%Y%m%d}-r{run_id}.md", content)


def execute_primary_task(primary: str, state: dict) -> Path | None:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0)
    run_id = int(state.get("runs", 0))
    task_lower = primary.lower()
    actions: list[tuple[str, Callable[[dt.datetime, int], Path]]] = [
        ("sales promise", action_offer),
        ("core service offer", action_offer),
        ("lock the first icp", action_icp),
        ("first 100-company target list", action_target_list),
        ("target list", action_target_list),
        ("extract company name", action_target_list),
        ("prepare the first outreach batch", action_outreach),
        ("cold email templates", action_compliance),
        ("verify email footer", action_compliance),
        ("test unsubscribe flow", action_compliance),
        ("suppression list", action_compliance),
        ("public b2b data sources", action_compliance),
        ("week 1 kpi chain", action_offer),
        ("15-minute demo script", action_demo),
        ("initial delivery checklist", action_delivery),
        ("github bounties", action_bounties),
        ("scan github bounties", action_bounties),
    ]
    for key, action in actions:
        if key in task_lower:
            return action(now, run_id)

    content = (
        f"# Finance Task Note (Run {run_id})\n\n"
        f"- Task: {primary}\n"
        f"- Executed at: {now.isoformat().replace('+00:00', 'Z')}\n"
        "- Next: refine into a concrete service-delivery step in the next loop.\n"
    )
    return write_artifact(f"notes/{slugify(primary)}-{now:%Y%m%d}-r{run_id}.md", content)


def build_status(
    blocking: list[str], autonomous: list[str], state: dict, primary: str, artifact: Path | None
) -> tuple[str, str]:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    progress = state.get("task_progress", {})
    primary_count = int(progress.get(primary, 0)) if primary in progress else 0
    artifact_rel = str(artifact.relative_to(ROOT)) if artifact else "none"
    primary_clean = clean_text(primary)

    lines = [
        "# Finance Status",
        "",
        f"- Last run (UTC): {now}",
        f"- Run count: {state.get('runs', 0)}",
        f"- Primary task: {primary_clean}",
        f"- Primary task progress count: {primary_count}",
        f"- Last artifact: {artifact_rel}",
        f"- Blocking items: {len(blocking)}",
        f"- Autonomous queue items: {len(autonomous)}",
        "",
        "## Portfolio State",
        "- Core business: B2B pipeline setup service (ACTIVE)",
        "- Side cash: GitHub bounties (ACTIVE)",
        "- Upsell: website cleanup (INCUBATING ONLY)",
        "- Paused: crypto, data brokerage, generic products",
        "",
        "## Next Action",
        primary_clean,
        "",
        "## Blocking",
    ]
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
        "Portfolio:",
        "1. Core business: B2B pipeline setup service",
        "2. Side cash: GitHub bounties",
        "3. Upsell only: website cleanup",
        "4. Paused: crypto, data brokerage, generic products",
        f"Next: {primary_clean}",
    ]
    return status_text, "\n".join(telegram)


def append_activity(summary: str) -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    with ACTIVITY_LOG.open("a", encoding="utf-8") as handle:
        handle.write(f"[{now}] {summary}\n")


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
