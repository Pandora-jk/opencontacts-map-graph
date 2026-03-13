#!/usr/bin/env python3
"""
Emit one concise proactive digest for Jim or NO_REPLY.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path("/home/ubuntu/.openclaw/workspace")
HOME = Path.home()
CRON_JOBS = HOME / ".openclaw" / "cron" / "jobs.json"
OPENCLAW_CONFIG = HOME / ".openclaw" / "openclaw.json"
ACTION_ITEMS = ROOT / "docs" / "openclaw-setup-action-items-2026-03-07.md"
INFRA_CHECKS = ROOT / "departments" / "infra" / "artifacts" / "checks"
STATE_FILE = ROOT / "memory" / "proactive-pulse-state.json"
SYDNEY_TZ = ZoneInfo("Australia/Sydney")
DIGEST_MAX_ITEMS = 2
DIGEST_SLOTS = (
    {"name": "morning", "label": "Morning update", "start_hour": 8, "end_hour": 12},
    {"name": "evening", "label": "Evening update", "start_hour": 18, "end_hour": 23},
)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def sydney_now() -> dt.datetime:
    return utc_now().astimezone(SYDNEY_TZ)


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def load_state() -> dict:
    data = load_json(STATE_FILE, {})
    return data if isinstance(data, dict) else {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def newest_path(pattern: str) -> Path | None:
    matches = sorted(INFRA_CHECKS.glob(pattern))
    return matches[-1] if matches else None


def ensure_sentence(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped
    if stripped[-1] in ".!?":
        return stripped
    return f"{stripped}."


def current_digest_slot(now: dt.datetime | None = None) -> dict | None:
    local = (now or sydney_now()).astimezone(SYDNEY_TZ)
    for slot in DIGEST_SLOTS:
        if slot["start_hour"] <= local.hour < slot["end_hour"]:
            return slot
    return None


def digest_slot_key(now: dt.datetime | None = None) -> str | None:
    local = (now or sydney_now()).astimezone(SYDNEY_TZ)
    slot = current_digest_slot(local)
    if slot is None:
        return None
    return f"{local.date().isoformat()}:{slot['name']}"


def top_candidates(candidates: list[dict], limit: int = DIGEST_MAX_ITEMS) -> list[dict]:
    material = [item for item in candidates if item]
    material.sort(key=lambda item: (-int(item["priority"]), str(item["kind"])))
    return material[:limit]


def find_cron_failures() -> list[dict]:
    jobs = load_json(CRON_JOBS, {}).get("jobs", [])
    failures: list[dict] = []
    now_ms = int(utc_now().timestamp() * 1000)
    for job in jobs:
        if not isinstance(job, dict) or job.get("enabled") is False:
            continue
        name = str(job.get("name") or "").strip()
        if not name or name == "Proactive Pulse":
            continue
        state = job.get("state") or {}
        status = state.get("lastStatus") or state.get("lastRunStatus")
        consecutive = int(state.get("consecutiveErrors") or 0)
        running_at = state.get("runningAtMs")
        if status == "error" or consecutive > 0:
            failures.append(
                {
                    "name": name,
                    "kind": "error",
                    "last_error": state.get("lastError"),
                }
            )
            continue
        if isinstance(running_at, int) and now_ms - running_at > 2 * 60 * 60 * 1000:
            failures.append(
                {
                    "name": name,
                    "kind": "stuck",
                    "last_error": "job still marked running after >2h",
                }
            )
    return failures


def cron_failure_candidate() -> dict | None:
    failures = find_cron_failures()
    if not failures:
        return None
    names = ", ".join(item["name"] for item in failures[:2])
    if len(failures) > 2:
        names += f" (+{len(failures) - 2} more)"
    return {
        "kind": "cron_failure",
        "priority": 100,
        "fingerprint": f"cron:{'|'.join(sorted(item['name'] for item in failures))}",
        "headline": f"Automation issue: {names} failing",
        "todo": "inspect the latest cron run before changing more config",
        "human_action": False,
    }


def latest_infra_status_text() -> str:
    path = newest_path("*infra-status.md")
    if path is None:
        path = newest_path("*monitor-disk-usage*.md")
    return load_text(path) if path else ""


def disk_pressure_candidate() -> dict | None:
    text = latest_infra_status_text()
    if not text:
        return None
    usage = re.search(r"Root usage: /: (\d+)% used.*?avail ([^)]+)\)", text)
    if not usage:
        return None
    pct = int(usage.group(1))
    avail = usage.group(2).strip()
    if pct < 90:
        return None
    stale = re.search(
        r"^- ([0-9.]+[KMG]?) \d{4}-\d{2}-\d{2} [0-9:]{8} (\S+)$",
        text,
        flags=re.M,
    )
    if stale:
        size, path = stale.groups()
        todo = f"clear stale temp data at {path} ({size}) and rerun infra status"
        fingerprint = f"disk:{pct}:{path}:{size}"
    else:
        reclaim = re.search(r"^- ([0-9.]+[KMG]?) (\S+)$", text, flags=re.M)
        if reclaim:
            size, path = reclaim.groups()
            todo = f"review {path} ({size}) for safe cleanup and rerun infra status"
            fingerprint = f"disk:{pct}:{path}:{size}"
        else:
            todo = "reclaim disk space and rerun infra status"
            fingerprint = f"disk:{pct}:{avail}"
    return {
        "kind": "disk_pressure",
        "priority": 95,
        "fingerprint": fingerprint,
        "headline": f"Host risk: root disk is {pct}% full ({avail} free)",
        "todo": todo,
        "human_action": False,
    }


def network_exposure_candidate() -> dict | None:
    text = latest_infra_status_text()
    if "Unexpected externally exposed listeners" not in text:
        return None
    listener = re.search(r"Unexpected externally exposed listeners \(\d+\): ([^\n]+)", text)
    exposed = listener.group(1).strip() if listener else "unexpected listeners"
    return {
        "kind": "network_exposure",
        "priority": 80,
        "fingerprint": f"network:{exposed}",
        "headline": f"Infra risk: {exposed} still externally exposed",
        "todo": "disable MulticastDNS/LLMNR or block it in host and cloud firewall policy",
        "human_action": False,
    }


def coding_blocker_candidate() -> dict | None:
    text = load_text(ACTION_ITEMS)
    if not re.search(
        r"^- \[ \] Fix the coding-day-loop blocker caused by GitHub secret scanning\.",
        text,
        flags=re.M,
    ):
        return None
    return {
        "kind": "coding_blocker",
        "priority": 90,
        "fingerprint": "coding:secret-scanning-blocker",
        "headline": "Coding autonomy still blocked by GitHub secret-scanning history",
        "todo": "rewrite or remove the exposed secrets from push history",
        "human_action": False,
    }


def provider_cleanup_candidate() -> dict | None:
    text = load_text(ACTION_ITEMS)
    if not re.search(
        r"^- \[ \] Resolve the recurring OpenRouter `HTTP 401` noise\.",
        text,
        flags=re.M,
    ):
        return None
    config = load_json(OPENCLAW_CONFIG, {})
    profiles = (((config.get("auth") or {}).get("profiles")) or {})
    if "openrouter:default" not in profiles:
        return None
    return {
        "kind": "provider_cleanup",
        "priority": 35,
        "fingerprint": "provider:openrouter-cleanup",
        "headline": "Config cleanup pending: legacy OpenRouter auth still present",
        "todo": "remove or repair the stale OpenRouter profile",
        "human_action": False,
    }


def browser_review_candidate() -> dict | None:
    text = load_text(ACTION_ITEMS)
    if not re.search(
        r"^- \[ \] Review whether browser control should stay enabled for the main assistant\.",
        text,
        flags=re.M,
    ):
        return None
    config = load_json(OPENCLAW_CONFIG, {})
    browser_enabled = bool(((config.get("browser") or {}).get("enabled")))
    if not browser_enabled:
        return None
    return {
        "kind": "browser_review",
        "priority": 20,
        "fingerprint": "security:browser-enabled",
        "headline": "Browser control is still enabled for main",
        "todo": "decide whether to keep browser control enabled",
        "human_action": True,
    }


def collect_candidates() -> list[dict]:
    return [
        item
        for item in [
            cron_failure_candidate(),
            disk_pressure_candidate(),
            coding_blocker_candidate(),
            network_exposure_candidate(),
            provider_cleanup_candidate(),
            browser_review_candidate(),
        ]
        if item
    ]


def build_digest_message(candidates: list[dict], slot: dict) -> str:
    chosen = top_candidates(candidates)
    label = str(slot["label"])
    if not chosen:
        return "NO_REPLY"

    human_item = next((item for item in chosen if item.get("human_action")), None)
    lines: list[str] = [f"IMPORTANT: {label}" if human_item else label]
    if human_item:
        lines.append(f"TODO: {ensure_sentence(str(human_item['todo']))}")
    for item in chosen:
        lines.append(ensure_sentence(str(item["headline"])))
    return "\n".join(lines)


def already_sent_for_slot(state: dict, slot_key: str | None) -> bool:
    return bool(slot_key and state.get("last_slot_key") == slot_key)


def record_check(
    state: dict,
    *,
    slot_key: str | None,
    candidate_kinds: list[str],
    sent: bool,
    message: str | None,
) -> dict:
    updated = dict(state)
    now = utc_now().isoformat().replace("+00:00", "Z")
    updated["last_checked_at"] = now
    updated["last_candidate_kinds"] = candidate_kinds
    if sent:
        updated["last_sent_at"] = now
        updated["last_slot_key"] = slot_key
        updated["last_message"] = message
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit one proactive digest or NO_REPLY")
    parser.add_argument("--dry-run", action="store_true", help="Do not update state")
    parser.add_argument("--debug", action="store_true", help="Print candidate metadata to stderr")
    args = parser.parse_args()

    state = load_state()
    slot = current_digest_slot()
    slot_key = digest_slot_key()
    candidates = collect_candidates()

    if args.debug:
        debug = {
            "slot": slot,
            "slot_key": slot_key,
            "candidates": candidates,
            "state": state,
        }
        print(json.dumps(debug, indent=2), file=sys.stderr)

    if slot is None or (not args.dry_run and already_sent_for_slot(state, slot_key)):
        if not args.dry_run:
            save_state(
                record_check(
                    state,
                    slot_key=slot_key,
                    candidate_kinds=[str(item["kind"]) for item in top_candidates(candidates)],
                    sent=False,
                    message=None,
                )
            )
        print("NO_REPLY")
        return 0

    output = build_digest_message(candidates, slot)
    print(output)
    if output == "NO_REPLY":
        if not args.dry_run:
            save_state(
                record_check(
                    state,
                    slot_key=slot_key,
                    candidate_kinds=[],
                    sent=False,
                    message=None,
                )
            )
        return 0
    if not args.dry_run:
        save_state(
            record_check(
                state,
                slot_key=slot_key,
                candidate_kinds=[str(item["kind"]) for item in top_candidates(candidates)],
                sent=True,
                message=output,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
