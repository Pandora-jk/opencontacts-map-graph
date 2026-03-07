#!/usr/bin/env python3
"""
Deterministic config protocol for Telegram-safe changes.

Usage examples:
  python3 tools/config-protocol.py plan --from-text 'CONFIG_PLAN\nset agents.defaults.model.primary = "groq/llama-3.3-70b-versatile"'
  python3 tools/config-protocol.py plan --from-text 'CONFIG_PLAN\nset cron.jobs["Coding Day Loop"].schedule.expr = "*/10 6-23 * * *"'
  python3 tools/config-protocol.py apply
  python3 tools/config-protocol.py status
  python3 tools/config-protocol.py clear
"""

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Tuple

STATE_FILE = Path(
    os.environ.get(
        "CONFIG_PROTOCOL_STATE_FILE",
        "/home/ubuntu/.openclaw/workspace/.config_plan_state.json",
    )
)
RUNTIME_CONFIG = Path(
    os.environ.get(
        "OPENCLAW_RUNTIME_CONFIG",
        str(Path.home() / ".openclaw" / "openclaw.json"),
    )
)
CRON_JOBS = Path(
    os.environ.get(
        "OPENCLAW_CRON_JOBS",
        str(Path.home() / ".openclaw" / "cron" / "jobs.json"),
    )
)
OPENCLAW_BIN = os.environ.get("OPENCLAW_BIN", "openclaw")
DEFAULT_RESTART_MODE = os.environ.get("CONFIG_PROTOCOL_RESTART_MODE", "defer")
DEFAULT_RESTART_DELAY = int(os.environ.get("CONFIG_PROTOCOL_RESTART_DELAY", "3"))
CRON_SEGMENT_RE = re.compile(r"^([A-Za-z0-9_-]+)(?:\[(\d+)\])?$")
CRON_NAMED_SEGMENT_RE = re.compile(r"^([A-Za-z0-9_-]+)\[([\"'])(.+)\2\]$")


@dataclass
class Change:
    path: str
    value_raw: str
    value_obj: Any
    target: str
    resolved_path: str


def run_cmd(args: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def parse_value(raw: str) -> Any:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def resolve_target(path: str) -> Tuple[str, str]:
    text = path.strip()
    if text.startswith("cron "):
        resolved = text[len("cron "):].strip()
        if not resolved:
            raise ValueError(f"Missing cron path in line: {path}")
        return "cron", resolved
    if text.startswith("cron."):
        resolved = text[len("cron."):]
        if not resolved:
            raise ValueError(f"Missing cron path in line: {path}")
        return "cron", resolved
    return "config", text


def parse_change_line(line: str) -> Change:
    text = line.strip()
    if text.lower().startswith("set "):
        text = text[4:].strip()

    if " path=" in f" {text}" and " value=" in text:
        # Format: path=<dot.path> value=<json-or-string>
        tokens = shlex.split(text)
        path = None
        value_raw = None
        for tok in tokens:
            if tok.startswith("path="):
                path = tok[len("path="):].strip()
            elif tok.startswith("value="):
                value_raw = tok[len("value="):]
        if not path or value_raw is None:
            raise ValueError(f"Invalid path/value format: {line}")
        target, resolved_path = resolve_target(path)
        return Change(
            path=path,
            value_raw=value_raw,
            value_obj=parse_value(value_raw),
            target=target,
            resolved_path=resolved_path,
        )

    if "=" in text:
        path, value_raw = text.split("=", 1)
        path = path.strip()
        value_raw = value_raw.strip()
        if not path:
            raise ValueError(f"Missing path in line: {line}")
        target, resolved_path = resolve_target(path)
        return Change(
            path=path,
            value_raw=value_raw,
            value_obj=parse_value(value_raw),
            target=target,
            resolved_path=resolved_path,
        )

    raise ValueError(f"Unsupported change line: {line}")


def parse_plan_text(text: str) -> List[Change]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("Empty plan text")

    first = lines[0].upper()
    if first.startswith("CONFIG_PLAN"):
        lines = lines[1:]
    elif first.startswith("CONFIG_APPLY"):
        raise ValueError("Use 'apply' command for CONFIG_APPLY")

    changes: List[Change] = []
    for line in lines:
        if line.startswith("#"):
            continue
        changes.append(parse_change_line(line))

    if not changes:
        raise ValueError("No changes found. Add lines like: set a.b.c = \"value\"")
    return changes


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json_file(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def path_segments(path: str) -> list[tuple[str, int | str | None]]:
    segments: list[tuple[str, int | str | None]] = []
    for raw in path.split("."):
        raw = raw.strip()
        if not raw:
            raise ValueError(f"Invalid empty segment in path: {path}")
        named_match = CRON_NAMED_SEGMENT_RE.match(raw)
        if named_match:
            segments.append((named_match.group(1), named_match.group(3)))
            continue
        match = CRON_SEGMENT_RE.match(raw)
        if not match:
            raise ValueError(
                f"Unsupported cron path segment '{raw}' in '{path}'. "
                "Use dot paths with numeric indexes or quoted names like "
                'jobs[9].schedule.expr or jobs["Coding Day Loop"].schedule.expr.'
            )
        key = match.group(1)
        idx = match.group(2)
        segments.append((key, int(idx) if idx is not None else None))
    return segments


def get_json_path(data: Any, path: str) -> Any:
    cur = data
    for key, idx in path_segments(path):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
        if idx is not None:
            if not isinstance(cur, list):
                return None
            if isinstance(idx, int):
                if idx < 0 or idx >= len(cur):
                    return None
                cur = cur[idx]
            else:
                cur = next(
                    (
                        item
                        for item in cur
                        if isinstance(item, dict) and item.get("name") == idx
                    ),
                    None,
                )
                if cur is None:
                    return None
    return cur


def set_json_path(data: Any, path: str, value: Any) -> None:
    cur = data
    segments = path_segments(path)
    for key, idx in segments[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(path)
        cur = cur[key]
        if idx is not None:
            if not isinstance(cur, list):
                raise KeyError(path)
            if isinstance(idx, int):
                if idx < 0 or idx >= len(cur):
                    raise KeyError(path)
                cur = cur[idx]
            else:
                match = next(
                    (
                        item
                        for item in cur
                        if isinstance(item, dict) and item.get("name") == idx
                    ),
                    None,
                )
                if match is None:
                    raise KeyError(path)
                cur = match

    last_key, last_idx = segments[-1]
    if not isinstance(cur, dict) or last_key not in cur:
        raise KeyError(path)
    if last_idx is None:
        cur[last_key] = value
        return
    target = cur[last_key]
    if not isinstance(target, list):
        raise KeyError(path)
    if isinstance(last_idx, int):
        if last_idx < 0 or last_idx >= len(target):
            raise KeyError(path)
        target[last_idx] = value
        return
    for i, item in enumerate(target):
        if isinstance(item, dict) and item.get("name") == last_idx:
            target[i] = value
            return
    raise KeyError(path)


def file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_current_value(change: Change) -> Any:
    if change.target == "cron":
        if not CRON_JOBS.exists():
            raise RuntimeError(f"cron jobs file missing: {CRON_JOBS}")
        return get_json_path(read_json_file(CRON_JOBS), change.resolved_path)

    rc, out, err = run_cmd([OPENCLAW_BIN, "config", "get", change.resolved_path])
    if rc != 0:
        msg = err or out
        if "Config path not found" in msg:
            return None
        raise RuntimeError(f"config get failed for {change.resolved_path}: {msg}")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out.strip()


def set_config_value(path: str, value_obj: Any) -> None:
    value_json = json.dumps(value_obj, separators=(",", ":"))
    rc, out, err = run_cmd([OPENCLAW_BIN, "config", "set", path, value_json])
    if rc != 0:
        raise RuntimeError(f"config set failed for {path}: {err or out}")


def set_value(change: Change) -> None:
    if change.target == "cron":
        data = read_json_file(CRON_JOBS)
        try:
            set_json_path(data, change.resolved_path, change.value_obj)
        except KeyError as exc:
            raise RuntimeError(f"cron path not found: {change.resolved_path}") from exc
        write_json_file(CRON_JOBS, data)
        return
    set_config_value(change.resolved_path, change.value_obj)


def verify_change(change: Change, expected: Any) -> bool:
    current = get_current_value(change)
    return current == expected


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def format_plan(changes: List[Change]) -> str:
    lines = []
    lines.append("CONFIG_PLAN_READY")
    for idx, ch in enumerate(changes, start=1):
        lines.append(f"{idx}. {ch.path} = {json.dumps(ch.value_obj, ensure_ascii=False)}")
    lines.append("Reply with CONFIG_APPLY to execute, or CONFIG_CLEAR to discard.")
    return "\n".join(lines)


def cmd_plan(text: str) -> int:
    try:
        changes = parse_plan_text(text)
    except ValueError as e:
        print(f"CONFIG_PLAN_ERROR: {e}")
        return 2

    now = int(time.time())
    before_hashes = {
        "config": file_hash(RUNTIME_CONFIG),
        "cron": file_hash(CRON_JOBS),
    }
    before_values = {}
    for ch in changes:
        try:
            before_values[ch.path] = get_current_value(ch)
        except Exception as e:
            print(f"CONFIG_PLAN_ERROR: failed to read current value for {ch.path}: {e}")
            return 2

    payload = {
        "created_at": now,
        "expires_at": now + 1800,
        "before_hashes": before_hashes,
        "changes": [
            {
                "path": ch.path,
                "target": ch.target,
                "resolved_path": ch.resolved_path,
                "value": ch.value_obj,
                "before": before_values[ch.path],
            }
            for ch in changes
        ],
    }
    payload["plan_id"] = hashlib.sha256(
        json.dumps(payload["changes"], sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]
    save_state(payload)
    print(format_plan(changes))
    print(f"Plan ID: {payload['plan_id']} (valid ~30 min)")
    return 0


def restart_gateway_now() -> None:
    # Try systemd first, then fallback to direct process restart.
    rc, _, _ = run_cmd(["systemctl", "--user", "restart", "openclaw-gateway"])
    if rc == 0:
        return
    run_cmd(["pkill", "-f", "openclaw-gateway"])
    subprocess.Popen(
        ["bash", "-lc", "nohup openclaw gateway >/tmp/openclaw-gateway.log 2>&1 &"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def schedule_gateway_restart(delay_seconds: int) -> None:
    script = (
        f"sleep {max(0, delay_seconds)}; "
        "systemctl --user restart openclaw-gateway >/dev/null 2>&1 || "
        "{ pkill -f openclaw-gateway >/dev/null 2>&1; "
        "nohup openclaw gateway >/tmp/openclaw-gateway.log 2>&1 & }"
    )
    subprocess.Popen(
        ["bash", "-lc", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def wait_for_health(timeout_seconds: int = 20) -> Tuple[bool, str]:
    deadline = time.time() + timeout_seconds
    last = ""
    while time.time() < deadline:
        rc, out, err = run_cmd([OPENCLAW_BIN, "health"])
        if rc == 0:
            return True, out
        last = err or out
        time.sleep(1)
    return False, last


def restore_backup(path: Path, target_path: Path) -> None:
    if path.exists():
        path.replace(target_path)


def change_from_state(item: dict[str, Any]) -> Change:
    return Change(
        path=item["path"],
        value_raw=json.dumps(item["value"], ensure_ascii=False),
        value_obj=item["value"],
        target=item.get("target", "config"),
        resolved_path=item.get("resolved_path", item["path"]),
    )


def cmd_apply(restart_mode: str, restart_delay: int) -> int:
    state = load_state()
    if not state:
        print("CONFIG_APPLY_ERROR: no pending plan. Use CONFIG_PLAN first.")
        return 2

    now = int(time.time())
    if now > int(state.get("expires_at", 0)):
        print("CONFIG_APPLY_ERROR: plan expired. Send CONFIG_PLAN again.")
        return 2

    backups: dict[str, tuple[Path, Path]] = {}
    targets = {item.get("target", "config") for item in state["changes"]}
    if "config" in targets and RUNTIME_CONFIG.exists():
        backup = RUNTIME_CONFIG.with_name(f"openclaw.json.bak-config-apply-{now}")
        backup.write_bytes(RUNTIME_CONFIG.read_bytes())
        backups["config"] = (backup, RUNTIME_CONFIG)
    if "cron" in targets and CRON_JOBS.exists():
        backup = CRON_JOBS.with_name(f"jobs.json.bak-config-apply-{now}")
        backup.write_bytes(CRON_JOBS.read_bytes())
        backups["cron"] = (backup, CRON_JOBS)

    applied = []
    try:
        for item in state["changes"]:
            change = change_from_state(item)
            set_value(change)
            if not verify_change(change, item["value"]):
                raise RuntimeError(f"verification failed for {item['path']}")
            applied.append(item["path"])

        if restart_mode == "now":
            restart_gateway_now()
            ok, detail = wait_for_health()
            if not ok:
                raise RuntimeError(f"health check failed: {detail}")
        elif restart_mode == "defer":
            schedule_gateway_restart(restart_delay)

        print("CONFIG_APPLY_OK")
        print(f"Applied {len(applied)} changes.")
        for p in applied:
            print(f"- {p}")
        if restart_mode == "defer":
            print(f"Gateway restart scheduled in {restart_delay}s.")
        elif restart_mode == "none":
            print("Gateway restart skipped.")
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        return 0
    except Exception as e:
        for backup, target_path in backups.values():
            restore_backup(backup, target_path)
        if restart_mode == "now":
            restart_gateway_now()
        elif restart_mode == "defer":
            schedule_gateway_restart(restart_delay)
        print(f"CONFIG_APPLY_ROLLBACK: {e}")
        return 1


def cmd_status() -> int:
    state = load_state()
    if not state:
        print("CONFIG_STATUS: no pending plan")
        return 0
    now = int(time.time())
    ttl = max(0, int(state.get("expires_at", 0)) - now)
    print("CONFIG_STATUS: pending plan")
    print(f"Plan ID: {state.get('plan_id', 'unknown')}")
    print(f"Expires in: {ttl}s")
    for item in state.get("changes", []):
        print(f"- {item['path']} => {json.dumps(item['value'], ensure_ascii=False)}")
    return 0


def cmd_clear() -> int:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    print("CONFIG_CLEAR_OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Config protocol helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("--from-text", required=True, help="Raw CONFIG_PLAN text")
    p_apply = sub.add_parser("apply")
    p_apply.add_argument(
        "--restart",
        choices=("defer", "now", "none"),
        default=DEFAULT_RESTART_MODE,
        help="Gateway restart strategy after applying changes (default: defer).",
    )
    p_apply.add_argument(
        "--restart-delay",
        type=int,
        default=DEFAULT_RESTART_DELAY,
        help="Delay in seconds before deferred restart (default: 3).",
    )
    sub.add_parser("status")
    sub.add_parser("clear")

    args = parser.parse_args()
    if args.cmd == "plan":
        return cmd_plan(args.from_text)
    if args.cmd == "apply":
        return cmd_apply(args.restart, args.restart_delay)
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "clear":
        return cmd_clear()
    return 1


if __name__ == "__main__":
    sys.exit(main())
