#!/usr/bin/env python3
"""
Infra autonomous loop with concrete checks/artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from infra_disk import DISK_ALERT_THRESHOLD, DISK_CRITICAL_THRESHOLD, build_disk_usage_report

ROOT = Path('/home/ubuntu/.openclaw/workspace')
INFRA = ROOT / 'departments' / 'infra'
TODO_FILE = INFRA / 'TODO.md'
STATUS_FILE = INFRA / 'STATUS.md'
STATE_FILE = ROOT / 'memory' / 'infra-autopilot-state.json'
ACTIVITY_LOG = ROOT / 'logs' / 'infra-activity.log'
ART_DIR = INFRA / 'artifacts'
BACKUP_VERIFY_SCRIPT = ROOT / 'scripts' / 'verify-backup-integrity.sh'
EXPECTED_EXTERNAL_PORTS = {'tcp': {22}, 'udp': {68}}
AUTH_SUSPICIOUS_ALERT_THRESHOLD = 5
ARTIFACT_GLOBS = {
    'security': '*-run-security-audit-*.md',
    'disk': '*-monitor-disk-usage-*.md',
    'backup': '*-verify-backup-integrity-*.md',
    'updates': '*-check-for-system-updates-*.md',
}
STATUS_ARTIFACT_GLOB = '*-infra-status.md'


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {'runs': 0, 'cursor': 0, 'progress': {}}
    try:
        state = json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {'runs': 0, 'cursor': 0, 'progress': {}}
    state.setdefault('runs', 0)
    state.setdefault('cursor', 0)
    if not isinstance(state.get('progress'), dict):
        state['progress'] = {}
    return state


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def parse_autonomous_tasks(text: str) -> list[str]:
    section = ''
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if 'Autonomous Queue' in line:
            section = 'auto'
            continue
        if line.startswith('## '):
            section = ''
            continue
        if section == 'auto' and line.startswith('- [ ]'):
            out.append(re.sub(r'^- \[ \]\s*', '', line).strip())
    return out


def run_cmd(cmd: list[str], max_chars: int = 800) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    txt = (p.stdout or p.stderr).strip()
    return txt[:max_chars] if txt else 'n/a'


def one_line(value: str, max_len: int = 140) -> str:
    txt = re.sub(r'\s+', ' ', (value or '').strip())
    return (txt[: max_len - 1] + '…') if len(txt) > max_len else txt


def classify_external_ports(port_lines: str) -> tuple[list[str], int]:
    external: set[str] = set()
    local_only_count = 0
    for raw in port_lines.splitlines():
        parts = raw.split()
        if len(parts) != 2:
            continue
        proto, address = parts
        is_local = (
            address.startswith('127.')
            or address.startswith('[::1]')
            or address.startswith('localhost:')
            or address.startswith('127.0.0.53:')
            or address.startswith('127.0.0.54:')
        )
        if is_local:
            local_only_count += 1
            continue
        if ':' not in address:
            external.add(f'{proto.lower()}/{address}')
            continue
        port = address.rsplit(':', 1)[-1]
        if port.isdigit():
            external.add(f'{proto.lower()}/{port}')
        else:
            external.add(f'{proto.lower()}/{address}')
    return sorted(external), local_only_count


def explain_unexpected_listener(entry: str) -> str | None:
    if entry == 'udp/5353':
        return (
            'RISK: udp/5353 is mDNS/MulticastDNS; public/cloud hosts usually do not need it. '
            'Consider disabling MulticastDNS/LLMNR or blocking it with host/cloud firewall policy.'
        )
    return None


def summarize_external_ports(port_lines: str) -> str:
    if not port_lines or port_lines == 'n/a':
        return 'No externally exposed listening ports found'

    external, local_only_count = classify_external_ports(port_lines)
    if not external:
        return f'No externally exposed listening ports (local-only listeners only: {local_only_count})'

    unexpected = []
    for entry in sorted(external):
        proto, value = entry.split('/', 1)
        if value.isdigit() and int(value) in EXPECTED_EXTERNAL_PORTS.get(proto, set()):
            continue
        unexpected.append(entry)

    if unexpected:
        lines = [f"ALERT: Unexpected externally exposed listeners ({len(unexpected)}): {', '.join(unexpected[:8])}"]
        for entry in unexpected:
            hint = explain_unexpected_listener(entry)
            if hint and hint not in lines:
                lines.append(hint)
        return '\n'.join(lines)
    return f"Externally exposed listeners match allowlist ({len(external)}): {', '.join(sorted(external)[:8])}"


def check_firewall_status() -> str:
    lines: list[str] = []
    ufw = shutil.which('ufw')
    nft = shutil.which('nft')
    iptables = shutil.which('iptables')

    if ufw:
        status = run_cmd(['bash', '-lc', 'ufw status verbose 2>&1 | sed -n "1,20p"'], max_chars=1200)
        if re.search(r'^Status:\s+active\b', status, re.IGNORECASE | re.MULTILINE):
            lines.append('ufw: active')
        elif re.search(r'^Status:\s+inactive\b', status, re.IGNORECASE | re.MULTILINE):
            lines.append('ALERT: ufw installed but inactive')
        else:
            lines.append(f'ufw: {one_line(status, 180)}')
    else:
        lines.append('WARN: ufw unavailable on host')

    other_tools = [name for name, found in (('nft', nft), ('iptables', iptables)) if found]
    if other_tools:
        lines.append(f"Other firewall tooling detected: {', '.join(other_tools)}")
    elif not ufw:
        lines.append('RISK: No host firewall tool detected (ufw/nft/iptables unavailable)')

    lines.append('Note: upstream cloud firewalls/security groups are not visible from this host check')
    return '\n'.join(lines)


def get_auth_sample() -> tuple[str, str]:
    if Path('/var/log/auth.log').exists():
        return run_cmd(['bash', '-lc', 'tail -n 600 /var/log/auth.log 2>/dev/null'], max_chars=12000), 'auth.log'
    if shutil.which('journalctl'):
        return run_cmd(['bash', '-lc', "journalctl -u ssh --since '24 hours ago' --no-pager 2>/dev/null | tail -n 600"], max_chars=12000), 'journalctl -u ssh'
    return 'Auth log source unavailable', 'none'


def extract_recent_auth_findings(log_text: str) -> list[str]:
    pattern = re.compile(r'(failed|invalid user|authentication failure|accepted|error: pam|connection closed by invalid user)', re.IGNORECASE)
    return [line for line in log_text.splitlines() if pattern.search(line)][-40:]


def summarize_auth_risk(log_text: str, source: str) -> str:
    if not log_text or log_text == 'n/a' or log_text.startswith('Auth log source unavailable'):
        return 'No auth log source available'
    suspicious = sum(
        1
        for line in log_text.splitlines()
        if re.search(r'(failed|invalid user|authentication failure|error: pam)', line, re.IGNORECASE)
    )
    if suspicious >= AUTH_SUSPICIOUS_ALERT_THRESHOLD:
        return f'ALERT: {suspicious} suspicious auth lines found in sampled logs ({source})'
    if suspicious == 0:
        return f'No failed authentication attempts found in sampled logs ({source})'
    return f'{suspicious} suspicious auth lines found in sampled logs ({source})'


def summarize_backup_risk(result: str) -> str:
    if re.search(r'^(ALERT|FAIL|RISK|WARN):', result, re.MULTILINE):
        return f'ALERT: backup integrity risk detected ({result.splitlines()[0]})'
    return 'No backup integrity risk signals detected'


def task_kind(task: str) -> str:
    tl = task.lower()
    if 'ssh' in tl or 'brute-force' in tl or 'security audit' in tl:
        return 'security'
    if 'disk usage' in tl:
        return 'disk'
    if 'backup integrity' in tl:
        return 'backup'
    if 'system updates' in tl:
        return 'updates'
    return 'generic'


def latest_artifact_for_task(task: str) -> Path | None:
    pattern = ARTIFACT_GLOBS.get(task_kind(task))
    if not pattern:
        return None
    matches = sorted((ART_DIR / 'checks').glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def latest_status_artifact() -> Path | None:
    matches = sorted((ART_DIR / 'checks').glob(STATUS_ARTIFACT_GLOB), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def score_task_from_artifact(task: str, artifact: Path | None) -> tuple[int, str]:
    if artifact is None:
        return 0, 'no prior artifact; bootstrap coverage'

    text = artifact.read_text(encoding='utf-8', errors='ignore')
    reasons: list[str] = []
    score = 0

    for line in text.splitlines():
        clean = clean_text(line)
        if line.startswith('CRITICAL:'):
            score += 100
            reasons.append(clean)
        elif line.startswith('ALERT:'):
            score += 60
            reasons.append(clean)
        elif line.startswith('RISK:'):
            score += 35
            reasons.append(clean)
        elif line.startswith('WARN:'):
            score += 15
            reasons.append(clean)

    kind = task_kind(task)
    if kind == 'security' and 'udp/5353' in text:
        score += 25
        reasons.append('unexpected udp/5353 listener still exposed')
    elif kind == 'disk':
        match = re.search(r'(?:ALERT|CRITICAL): Root filesystem usage is (\d+)%', text)
        if match:
            score += max(0, int(match.group(1)) - DISK_ALERT_THRESHOLD)
    elif kind == 'updates':
        match = re.search(r'(\d+)\s+pending updates', text)
        if match and int(match.group(1)) > 0:
            score += min(40, int(match.group(1)) * 10)
            reasons.append(f"{match.group(1)} pending package updates")
        else:
            listed = len(re.findall(r'upgradable from:', text))
            if listed > 0:
                score += min(40, listed * 10)
                reasons.append(f'{listed} listed package updates')

    if not reasons:
        reasons.append(f'latest artifact {artifact.name} has no active risk markers')
    deduped = list(dict.fromkeys(reasons))
    return score, '; '.join(deduped)


def score_task_from_status(task: str, artifact: Path | None) -> tuple[int, str]:
    if artifact is None:
        return 0, 'no infra-status artifact available yet'

    text = artifact.read_text(encoding='utf-8', errors='ignore')
    reasons: list[str] = []
    score = 0
    kind = task_kind(task)

    if kind == 'disk':
        critical = re.search(r'CRITICAL: Root filesystem usage is (\d+)%', text)
        alert = re.search(r'ALERT: Root filesystem usage is (\d+)%', text)
        if critical:
            score = 240 + max(0, int(critical.group(1)) - DISK_CRITICAL_THRESHOLD)
            reasons.append(f'latest infra-status shows CRITICAL root usage {critical.group(1)}%')
        elif alert:
            score = 140 + max(0, int(alert.group(1)) - DISK_ALERT_THRESHOLD)
            reasons.append(f'latest infra-status shows ALERT root usage {alert.group(1)}%')
    elif kind == 'security':
        if 'Unexpected externally exposed listeners' in text:
            score += 80
            reasons.append('latest infra-status shows unexpected external listeners')
        if 'ufw unavailable on host' in text:
            score += 40
            reasons.append('latest infra-status shows missing ufw visibility')
        auth = re.search(r'ALERT: (\d+) suspicious auth lines found', text)
        if auth:
            score += 60
            reasons.append(f'latest infra-status shows {auth.group(1)} suspicious auth lines')
    elif kind == 'updates':
        match = re.search(r'(\d+)\s+pending updates', text)
        if match and int(match.group(1)) > 0:
            score = 20 + min(40, int(match.group(1)) * 10)
            reasons.append(f'latest infra-status shows {match.group(1)} pending updates')
    elif kind == 'backup':
        if re.search(r'^(ALERT|FAIL|RISK|WARN): .*backup', text, re.MULTILINE):
            score = 120
            reasons.append('latest infra-status shows backup risk markers')

    if score == 0:
        return 0, f'latest infra-status {artifact.name} has no active markers for {kind}'
    return score, '; '.join(reasons)


def select_task(tasks: list[str], state: dict) -> tuple[str, str]:
    status_artifact = latest_status_artifact()
    scored: list[tuple[int, int, str, str]] = []
    for index, task in enumerate(tasks):
        task_artifact = latest_artifact_for_task(task)
        artifact_score, artifact_reason = score_task_from_artifact(task, task_artifact)
        status_score, status_reason = score_task_from_status(task, status_artifact)
        if status_score >= artifact_score:
            score, reason = status_score, status_reason
        else:
            score, reason = artifact_score, artifact_reason
        scored.append((score, index, task, reason))

    scored.sort(key=lambda item: (-item[0], item[1]))
    if scored and scored[0][0] > 0:
        _, _, task, reason = scored[0]
        return task, f'risk-based priority: {reason}'

    idx = int(state.get('cursor', 0)) % len(tasks)
    return tasks[idx], 'round-robin fallback: no active risk markers in latest artifacts'


def execute_task(task: str, run_id: int) -> tuple[Path, str]:
    now = dt.datetime.now(dt.UTC)
    slug = re.sub(r'[^a-z0-9]+', '-', task.lower()).strip('-')[:56] or 'infra-task'
    rel = Path('checks') / f"{now:%Y%m%dT%H%M%SZ}-r{run_id}-{slug}.md"
    out = ART_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"# Infra Check (Run {run_id})", '', f"- Task: {task}", f"- UTC: {now.isoformat().replace('+00:00','Z')}", '']
    tl = task.lower()
    if 'disk usage' in tl:
        lines.append('## Disk Usage')
        lines.extend(build_disk_usage_report())
    elif 'system updates' in tl:
        lines.append('## Pending Updates')
        apt = shutil.which('apt')
        if apt:
            lines.append(run_cmd(['bash', '-lc', "apt list --upgradable 2>/dev/null | sed -n '1,40p'"]))
        else:
            lines.append('apt not available')
    elif 'ssh' in tl or 'brute-force' in tl or 'security audit' in tl:
        lines.append('## Open Ports')
        port_lines = run_cmd(['bash', '-lc', "ss -H -tuln 2>/dev/null | awk '{print $1, $5}' | sort -u | sed -n '1,80p' || true"])
        lines.append(port_lines)
        lines.append('')
        lines.append('## External Listener Assessment')
        lines.append(summarize_external_ports(port_lines))
        lines.append('')
        lines.append('## Firewall Status')
        lines.append(check_firewall_status())
        lines.append('')
        lines.append('## SSH Config Snapshot')
        lines.append(run_cmd([
            'bash',
            '-lc',
            "(sshd -T 2>/dev/null | grep -Ei '^(permitrootlogin|passwordauthentication|x11forwarding|maxauthtries|permitemptypasswords) ' || "
            "grep -Ei '^(PermitRootLogin|PasswordAuthentication|X11Forwarding|MaxAuthTries|PermitEmptyPasswords)\\b' /etc/ssh/sshd_config 2>/dev/null || "
            "echo 'SSH config unavailable') | sed -n '1,40p'"
        ]))
        lines.append('')
        lines.append('## Recent SSH/Auth Findings')
        auth_sample, source = get_auth_sample()
        auth_lines = extract_recent_auth_findings(auth_sample)
        lines.append('\n'.join(auth_lines) if auth_lines else 'No recent SSH/auth findings in sampled logs')
        lines.append('')
        lines.append('## Auth Risk Assessment')
        lines.append(summarize_auth_risk(auth_sample, source))
    elif 'backup integrity' in tl:
        lines.append('## Backup Integrity Check')
        if BACKUP_VERIFY_SCRIPT.exists():
            backup_output = run_cmd([
                'bash',
                '-lc',
                f"bash '{BACKUP_VERIFY_SCRIPT}' --archive /tmp/latest-workspace-backup.tar.gz --source '{ROOT / 'INCOME-ENGINE.md'}' --enforce-permissions"
            ])
            lines.append(backup_output)
        else:
            backup_output = 'FAIL: backup verification script missing'
            lines.append(backup_output)
        lines.append('')
        lines.append('## Backup Risk Assessment')
        lines.append(summarize_backup_risk(backup_output))
    else:
        lines.append('## Generic Health Snapshot')
        lines.append(run_cmd(['bash', '-lc', 'uptime && free -m | sed -n "1,3p"']))

    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    try:
        os.chmod(out, 0o600)
    except OSError:
        pass
    return out, str(rel)


def append_activity(msg: str) -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    with ACTIVITY_LOG.open('a', encoding='utf-8') as f:
        f.write(f'[{now}] {msg}\n')


def clean_text(value: str) -> str:
    txt = re.sub(r'[`*_]+', '', value or '')
    return re.sub(r'\s+', ' ', txt).strip()


def build_status(state: dict, task: str, rel: str, queue: int, reason: str) -> tuple[str, str]:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')
    count = int(state.get('progress', {}).get(task, 0)) if task else 0
    task_clean = clean_text(task or 'none')
    reason_clean = clean_text(reason or 'n/a')
    md = [
        '# Infra Status',
        '',
        f'- Last run (UTC): {now}',
        f"- Run count: {state.get('runs',0)}",
        f'- Active task: {task or "none"}',
        f'- Selection reason: {reason or "n/a"}',
        f'- Task progress count: {count}',
        f'- Last artifact: {"departments/infra/artifacts/" + rel if rel else "none"}',
        f'- Autonomous open queue: {queue}',
        '',
    ]
    tg = [
        '[INFRA UPDATE]',
        f'Time (UTC): {now}',
        f'Run: {state.get("runs",0)}',
        f'Task: {task_clean}',
        f'Reason: {one_line(reason_clean, 180)}',
        f'Progress: {count}',
        f'Queue: {queue}',
        f'Artifact: {("departments/infra/artifacts/" + rel) if rel else "none"}',
    ]
    return '\n'.join(md) + '\n', '\n'.join(tg)


def main() -> int:
    parser = argparse.ArgumentParser(description='Infra autopilot')
    parser.add_argument('--emit-telegram', action='store_true')
    args = parser.parse_args()

    todo = TODO_FILE.read_text(encoding='utf-8') if TODO_FILE.exists() else ''
    tasks = parse_autonomous_tasks(todo)
    state = load_state()
    state['runs'] = int(state.get('runs', 0)) + 1

    task = ''
    rel = ''
    reason = ''
    if tasks:
        task, reason = select_task(tasks, state)
        idx = tasks.index(task)
        state['cursor'] = idx + 1
        _, rel = execute_task(task, int(state['runs']))
        prog = state.setdefault('progress', {})
        prog[task] = int(prog.get(task, 0)) + 1
        append_activity(
            f"run={state['runs']} task='{task}' reason='{clean_text(reason)}' "
            f"artifact='departments/infra/artifacts/{rel}' queue={len(tasks)}"
        )
    else:
        append_activity(f"run={state['runs']} task='none' queue=0")

    status_text, telegram_text = build_status(state, task, rel, len(tasks), reason)
    STATUS_FILE.write_text(status_text, encoding='utf-8')
    save_state(state)
    if args.emit_telegram:
        print(telegram_text)
    else:
        print(status_text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
