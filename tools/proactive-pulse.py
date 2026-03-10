#!/usr/bin/env python3
"""
Emit one proactive, state-aware suggestion for Jim or NO_REPLY.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/ubuntu/.openclaw/workspace")
HOME = Path.home()
CRON_JOBS = HOME / ".openclaw" / "cron" / "jobs.json"
OPENCLAW_CONFIG = HOME / ".openclaw" / "openclaw.json"
ACTION_ITEMS = ROOT / "docs" / "openclaw-setup-action-items-2026-03-07.md"
INFRA_CHECKS = ROOT / "departments" / "infra" / "artifacts" / "checks"
STATE_FILE = ROOT / "memory" / "proactive-pulse-state.json"

SUPPRESS_HOURS = {
    "cron_failure": 2,
    "disk_pressure": 12,
    "coding_blocker": 12,
    "network_exposure": 12,
    "provider_cleanup": 72,
    "browser_review": 72,
}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


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
        "message": (
            f"[PROACTIVE] Automation issue: {names} need attention. "
            "Next step: inspect the latest cron run before changing more config."
        ),
        "details": failures,
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
        next_step = f"clear stale temp data at {path} ({size}) and rerun infra status"
        fingerprint = f"disk:{pct}:{path}:{size}"
    else:
        reclaim = re.search(r"^- ([0-9.]+[KMG]?) (\S+)$", text, flags=re.M)
        if reclaim:
            size, path = reclaim.groups()
            next_step = f"review {path} ({size}) for safe cleanup and rerun infra status"
            fingerprint = f"disk:{pct}:{path}:{size}"
        else:
            next_step = "reclaim disk space and rerun infra status"
            fingerprint = f"disk:{pct}:{avail}"
    return {
        "kind": "disk_pressure",
        "priority": 95,
        "fingerprint": fingerprint,
        "message": (
            f"[PROACTIVE] Host risk: root disk is {pct}% full ({avail} free). "
            f"Next step: {next_step}."
        ),
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
        "message": (
            f"[PROACTIVE] Infra risk: {exposed} is still externally exposed. "
            "Next step: disable MulticastDNS/LLMNR or block it in host/cloud firewall policy."
        ),
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
        "message": (
            "[PROACTIVE] Coding autonomy is still blocked by GitHub secret scanning on push history. "
            "Next step: remove or rewrite the exposed secrets so Coding Day Loop can push unattended."
        ),
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
        "message": (
            "[PROACTIVE] Config cleanup remains: legacy OpenRouter auth is still present. "
            "Next step: remove or repair that profile so runtime provider config matches reality."
        ),
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
        "message": (
            "[PROACTIVE] Attack-surface review: browser control is still enabled for main. "
            "Next step: disable it unless you actively use browser automation."
        ),
    }


def choose_candidate() -> dict | None:
    candidates = [
        cron_failure_candidate(),
        disk_pressure_candidate(),
        coding_blocker_candidate(),
        network_exposure_candidate(),
        provider_cleanup_candidate(),
        browser_review_candidate(),
    ]
    material = [item for item in candidates if item]
    if not material:
        return None
    material.sort(key=lambda item: (-int(item["priority"]), str(item["kind"])))
    return material[0]


def is_suppressed(candidate: dict, state: dict) -> bool:
    last_fingerprint = state.get("last_fingerprint")
    last_sent_at = state.get("last_sent_at")
    if last_fingerprint != candidate["fingerprint"] or not isinstance(last_sent_at, str):
        return False
    try:
        sent_at = dt.datetime.fromisoformat(last_sent_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    suppress_for = SUPPRESS_HOURS.get(candidate["kind"], 12)
    return utc_now() - sent_at < dt.timedelta(hours=suppress_for)


def record_check(state: dict, candidate: dict | None, sent: bool) -> dict:
    updated = dict(state)
    now = utc_now().isoformat().replace("+00:00", "Z")
    updated["last_checked_at"] = now
    updated["last_candidate"] = candidate["kind"] if candidate else None
    updated["last_candidate_fingerprint"] = candidate["fingerprint"] if candidate else None
    if sent and candidate:
        updated["last_fingerprint"] = candidate["fingerprint"]
        updated["last_kind"] = candidate["kind"]
        updated["last_sent_at"] = now
        updated["last_message"] = candidate["message"]
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit one proactive suggestion or NO_REPLY")
    parser.add_argument("--dry-run", action="store_true", help="Do not update state")
    parser.add_argument("--debug", action="store_true", help="Print candidate metadata to stderr")
    parser.add_argument("--deliver", action="store_true", help="Deliver via Telegram if there's something to report")
    args = parser.parse_args()

    state = load_state()
    candidate = choose_candidate()
    suppressed = bool(candidate and is_suppressed(candidate, state))

    if args.debug:
        debug = {
            "candidate": candidate,
            "suppressed": suppressed,
            "state": state,
        }
        print(json.dumps(debug, indent=2), file=sys.stderr)

    if candidate is None or suppressed:
        if not args.dry_run:
            save_state(record_check(state, candidate, sent=False))
        print("NO_REPLY")
        return 0

    if not args.dry_run:
        save_state(record_check(state, candidate, sent=True))
    output = candidate["message"]
    print(output)
    if args.deliver:
        try:
            import subprocess
            subprocess.run(["python3", "/home/ubuntu/.openclaw/workspace/tools/send-telegram.py", "--to", "156480904", "--text", output], cwd=str(ROOT))
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
