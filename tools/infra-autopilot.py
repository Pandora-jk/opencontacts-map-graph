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
from infra_network import inspect_mdns_exposure
from infra_audit_common import (
    AUTH_LOG_SAMPLE_LIMIT,
    AUTH_LOG_SAMPLE_MAX_CHARS,
    auth_log_tail_command,
    check_firewall_status as common_check_firewall_status,
    journalctl_ssh_tail_command,
    summarize_external_ports as common_summarize_external_ports,
)

ROOT = Path('/home/ubuntu/.openclaw/workspace')
INFRA = ROOT / 'departments' / 'infra'
TODO_FILE = INFRA / 'TODO.md'
STATUS_FILE = INFRA / 'STATUS.md'
STATE_FILE = ROOT / 'memory' / 'infra-autopilot-state.json'
ACTIVITY_LOG = ROOT / 'logs' / 'infra-activity.log'
ART_DIR = INFRA / 'artifacts'
BACKUP_VERIFY_SCRIPT = ROOT / 'scripts' / 'verify-backup-integrity.sh'
AUTH_SUSPICIOUS_ALERT_THRESHOLD = 5
AUTH_SIGNAL_PATTERN = re.compile(
    r'(failed|invalid user|authentication failure|accepted|error: pam|connection closed by invalid user)',
    re.IGNORECASE,
)
AUTH_SUSPICIOUS_PATTERN = re.compile(r'(failed|invalid user|authentication failure|error: pam)', re.IGNORECASE)
ARTIFACT_GLOBS = {
    'security': '*-run-security-audit-*.md',
    'disk': '*-monitor-disk-usage-*.md',
    'backup': '*-verify-backup-integrity-*.md',
    'updates': '*-check-for-system-updates-*.md',
}
STATUS_ARTIFACT_GLOB = '*-infra-status.md'
STATUS_ARTIFACT_MAX_AGE = dt.timedelta(hours=6)


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
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        txt = (p.stdout or p.stderr).strip()
        return txt[:max_chars] if txt else 'n/a'
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return f'Error: {str(exc)[:200]}'


def one_line(value: str, max_len: int = 140) -> str:
    txt = re.sub(r'\s+', ' ', (value or '').strip())
    return (txt[: max_len - 1] + '…') if len(txt) > max_len else txt


def summarize_external_ports(port_lines: str) -> str:
    return common_summarize_external_ports(port_lines)


def check_firewall_status() -> str:
    return common_check_firewall_status(run_cmd, which=shutil.which, render_one_line=one_line)


def get_auth_sample() -> tuple[str, str]:
    if Path('/var/log/auth.log').exists():
        return run_cmd(auth_log_tail_command(AUTH_LOG_SAMPLE_LIMIT), max_chars=AUTH_LOG_SAMPLE_MAX_CHARS), 'auth.log'
    if shutil.which('journalctl'):
        return run_cmd(journalctl_ssh_tail_command(AUTH_LOG_SAMPLE_LIMIT), max_chars=AUTH_LOG_SAMPLE_MAX_CHARS), 'journalctl -u ssh'
    return 'Auth log source unavailable', 'none'


def is_self_generated_auth_audit_line(line: str) -> bool:
    lowered = line.lower()
    if 'sudo:' not in lowered or 'command=' not in lowered:
        return False
    if '/var/log/auth.log' in lowered and any(tool in lowered for tool in ('grep', 'awk', 'sed', 'tail', 'cat')):
        return True
    if 'journalctl' in lowered and any(token in lowered for token in ('-u ssh', '-u sshd', ' ssh.service', ' sshd.service')):
        return True
    return False


def filtered_auth_lines(log_text: str, pattern: re.Pattern[str]) -> list[str]:
    return [
        line
        for line in log_text.splitlines()
        if not is_self_generated_auth_audit_line(line) and pattern.search(line)
    ]


def extract_recent_auth_findings(log_text: str) -> list[str]:
    return filtered_auth_lines(log_text, AUTH_SIGNAL_PATTERN)[-40:]


def summarize_auth_risk(log_text: str, source: str) -> str:
    if not log_text or log_text == 'n/a' or log_text.startswith('Auth log source unavailable'):
        return 'No auth log source available'
    suspicious = len(filtered_auth_lines(log_text, AUTH_SUSPICIOUS_PATTERN))
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


def artifact_age(now: dt.datetime, artifact: Path) -> dt.timedelta | None:
    try:
        modified_at = dt.datetime.fromtimestamp(artifact.stat().st_mtime, tz=dt.UTC)
    except OSError:
        return None
    return now - modified_at


def is_status_artifact_stale(
    artifact: Path,
    *,
    now: dt.datetime | None = None,
    max_age: dt.timedelta = STATUS_ARTIFACT_MAX_AGE,
) -> bool:
    reference_now = now or dt.datetime.now(dt.UTC)
    age = artifact_age(reference_now, artifact)
    if age is None:
        return True
    return age > max_age


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
    if is_status_artifact_stale(artifact):
        age = artifact_age(dt.datetime.now(dt.UTC), artifact)
        if age is None:
            return 0, f'latest infra-status artifact {artifact.name} is unavailable for freshness checks'
        return 0, f'latest infra-status artifact {artifact.name} is stale ({int(age.total_seconds() // 3600)}h old)'

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
        lines.append('## Multicast DNS Exposure')
        lines.append(inspect_mdns_exposure(port_lines))
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
