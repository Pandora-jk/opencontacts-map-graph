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
from infra_ssh_ban_hardening import (
    fail2ban_binary_status,
    fail2ban_policy_status,
    fail2ban_service_status,
    fail2ban_sshd_status,
    live_config_status as fail2ban_live_config_status,
    managed_config_status as fail2ban_managed_config_status,
)
from infra_sshd_hardening import (
    LIVE_SSHD_MAIN_CONFIG,
    effective_policy_drift as sshd_effective_policy_drift,
    live_config_status as sshd_live_config_status,
    managed_config_status as sshd_managed_config_status,
    read_effective_sshd_settings,
)
from infra_update_health import render_auto_update_health
from infra_audit_common import (
    AUTH_LOG_SAMPLE_LIMIT,
    AUTH_LOG_SAMPLE_MAX_CHARS,
    AUTH_SUSPICIOUS_ALERT_THRESHOLD,
    AUTH_SUSPICIOUS_PATTERN,
    auth_log_tail_command,
    check_firewall_status as common_check_firewall_status,
    firewall_observability_gap_is_hardened as common_firewall_observability_gap_is_hardened,
    filtered_auth_lines as common_filtered_auth_lines,
    inspect_unexpected_listeners as common_inspect_unexpected_listeners,
    is_self_generated_auth_audit_line as common_is_self_generated_auth_audit_line,
    journalctl_ssh_tail_command,
    summarize_auth_event_sources as common_summarize_auth_event_sources,
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
AUTH_SIGNAL_PATTERN = re.compile(
    r'(failed|invalid user|authentication failure|accepted|error: pam|connection closed by invalid user)',
    re.IGNORECASE,
)
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


def inspect_unexpected_listener_details(port_lines: str) -> str:
    return common_inspect_unexpected_listeners(run_cmd, port_lines)


def get_auth_sample() -> tuple[str, str]:
    if Path('/var/log/auth.log').exists():
        return run_cmd(auth_log_tail_command(AUTH_LOG_SAMPLE_LIMIT), max_chars=AUTH_LOG_SAMPLE_MAX_CHARS), 'auth.log'
    if shutil.which('journalctl'):
        return run_cmd(journalctl_ssh_tail_command(AUTH_LOG_SAMPLE_LIMIT), max_chars=AUTH_LOG_SAMPLE_MAX_CHARS), 'journalctl -u ssh'
    return 'Auth log source unavailable', 'none'


def is_self_generated_auth_audit_line(line: str) -> bool:
    return common_is_self_generated_auth_audit_line(line)


def filtered_auth_lines(log_text: str, pattern: re.Pattern[str]) -> list[str]:
    return common_filtered_auth_lines(log_text, pattern)


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


def ssh_hardening_validation_status() -> str:
    lines = [
        sshd_managed_config_status(),
        sshd_live_config_status(),
    ]
    effective_settings, effective_error = read_effective_sshd_settings(include_target=str(LIVE_SSHD_MAIN_CONFIG))
    if effective_error:
        lines.append(effective_error)
        return '\n'.join(lines)
    if not effective_settings:
        lines.append('WARN: effective sshd policy check returned no settings')
        return '\n'.join(lines)

    drift = sshd_effective_policy_drift(effective_settings)
    if drift:
        lines.append('ERROR: effective sshd policy drift detected')
        lines.extend(f'- {item}' for item in drift)
    else:
        lines.append('INFO: effective sshd policy matches the managed hardening')
    return '\n'.join(lines)


def ssh_ban_hardening_status() -> str:
    return '\n'.join(
        [
            fail2ban_managed_config_status(),
            fail2ban_live_config_status(),
            fail2ban_policy_status(),
            fail2ban_binary_status(),
            fail2ban_service_status(),
            fail2ban_sshd_status(),
        ]
    )


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
    pending_updates_match = re.search(r'(\d+)\s+pending updates', text)
    pending_updates = int(pending_updates_match.group(1)) if pending_updates_match else 0

    for line in text.splitlines():
        clean = clean_text(line)
        if clean.startswith('ALERT: Detailed inspection for unexpected listeners'):
            continue
        if (
            line.startswith('WARN: ufw installed but status visibility is blocked by current privileges')
            and common_firewall_observability_gap_is_hardened(text)
        ):
            continue
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
        if 'RISK: auto-updates disabled or drifted' in text:
            score += 80
            reasons.append('auto-updates disabled or drifted')
        if 'RISK: auto-update timers not enabled at boot:' in text:
            score += 75
            reasons.append('auto-update timers are not enabled at boot')
        if 'RISK: pending updates are waiting while auto-updates are disabled' in text:
            score += 60
            reasons.append('pending updates are waiting while auto-updates are disabled')
        if 'RISK: unattended-upgrades appears stalled;' in text:
            score += 95
            reasons.append('unattended-upgrades appears stalled')
        if 'RISK: pending updates remain after an incomplete unattended-upgrades run' in text:
            score += 70
            reasons.append('pending updates remain after an incomplete unattended-upgrades run')
        if 'RISK: security-sensitive updates pending:' in text:
            score += 40
            reasons.append('security-sensitive updates are pending')
        if 'WARN: reboot required by previously installed updates' in text:
            score += 35
            reasons.append('reboot required by previously installed updates')
        stale_match = re.search(r'RISK: pending updates remain and unattended-upgrades has not completed recently \((\d+)h old\)', text)
        if stale_match:
            score += 50
            reasons.append(
                f"pending updates remain and unattended-upgrades has not completed recently ({stale_match.group(1)}h old)"
            )
        elif (
            pending_updates > 0
            and 'INFO: auto-updates enabled' in text
            and 'RISK: pending updates' not in text
            and 'RISK: unattended-upgrades appears stalled;' not in text
            and 'RISK: security-sensitive updates pending:' not in text
            and 'WARN: reboot required by previously installed updates' not in text
        ):
            score += 5
            reasons.append('pending package updates awaiting the next unattended-upgrades window')
        else:
            listed = len(re.findall(r'upgradable from:', text))
            if listed > 0 and 'INFO: auto-updates enabled' not in text:
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
    pending_updates_match = re.search(r'(\d+)\s+pending updates', text)
    pending_updates = int(pending_updates_match.group(1)) if pending_updates_match else 0

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
        elif 'WARN: ufw installed but status visibility is blocked by current privileges' in text and not common_firewall_observability_gap_is_hardened(
            text
        ):
            score += 40
            reasons.append('latest infra-status shows blocked ufw visibility')
        if 'RISK: PermitRootLogin enabled' in text:
            score += 45
            reasons.append('latest infra-status shows PermitRootLogin enabled')
        if 'RISK: PasswordAuthentication enabled' in text:
            score += 55
            reasons.append('latest infra-status shows PasswordAuthentication enabled')
        if 'CRITICAL: PermitEmptyPasswords enabled' in text:
            score += 100
            reasons.append('latest infra-status shows PermitEmptyPasswords enabled')
        if 'RISK: AllowTcpForwarding enabled' in text:
            score += 35
            reasons.append('latest infra-status shows SSH tcp forwarding enabled')
        if 'RISK: AllowAgentForwarding enabled' in text:
            score += 30
            reasons.append('latest infra-status shows SSH agent forwarding enabled')
        if 'RISK: AllowStreamLocalForwarding enabled' in text:
            score += 30
            reasons.append('latest infra-status shows SSH stream-local forwarding enabled')
        if 'RISK: PermitTunnel enabled' in text:
            score += 30
            reasons.append('latest infra-status shows SSH tunneling enabled')
        if 'WARN: MaxAuthTries is high' in text:
            score += 15
            reasons.append('latest infra-status shows high SSH MaxAuthTries')
        if 'WARN: effective SSH hardening is only partially visible' in text:
            score += 20
            reasons.append('latest infra-status shows incomplete SSH hardening visibility')
        if 'WARN: live config missing: /etc/fail2ban/jail.d/99-openclaw-sshd.local' in text:
            score += 55
            reasons.append('latest infra-status shows missing live fail2ban sshd jail')
        if 'WARN: live config drift: /etc/fail2ban/jail.d/99-openclaw-sshd.local' in text:
            score += 45
            reasons.append('latest infra-status shows live fail2ban sshd jail drift')
        if 'WARN: fail2ban service state unavailable from current shell' in text:
            score += 20
            reasons.append('latest infra-status cannot confirm fail2ban service state')
        if 'WARN: fail2ban sshd jail unavailable from current shell' in text:
            score += 20
            reasons.append('latest infra-status cannot confirm fail2ban sshd jail state')
        auth = re.search(r'ALERT: (\d+) suspicious auth lines found', text)
        if auth:
            score += 60
            reasons.append(f'latest infra-status shows {auth.group(1)} suspicious auth lines')
    elif kind == 'updates':
        if 'RISK: auto-updates disabled or drifted' in text:
            score += 80
            reasons.append('latest infra-status shows auto-updates disabled or drifted')
        if 'RISK: auto-update timers not enabled at boot:' in text:
            score += 75
            reasons.append('latest infra-status shows auto-update timers are not enabled at boot')
        if 'RISK: pending updates are waiting while auto-updates are disabled' in text:
            score += 60
            reasons.append('latest infra-status shows pending updates waiting while auto-updates are disabled')
        if 'RISK: unattended-upgrades appears stalled;' in text:
            score += 95
            reasons.append('latest infra-status shows unattended-upgrades appears stalled')
        if 'RISK: pending updates remain after an incomplete unattended-upgrades run' in text:
            score += 70
            reasons.append('latest infra-status shows pending updates after an incomplete unattended-upgrades run')
        if 'RISK: security-sensitive updates pending:' in text:
            score += 40
            reasons.append('latest infra-status shows security-sensitive updates pending')
        if 'WARN: reboot required by previously installed updates' in text:
            score += 35
            reasons.append('latest infra-status shows a pending reboot requirement')
        stale_match = re.search(r'RISK: pending updates remain and unattended-upgrades has not completed recently \((\d+)h old\)', text)
        if stale_match:
            score += 50
            reasons.append(
                'latest infra-status shows pending updates with stale unattended-upgrades completion '
                f'({stale_match.group(1)}h old)'
            )
        elif (
            pending_updates > 0
            and 'INFO: auto-updates enabled' in text
            and 'RISK: pending updates' not in text
            and 'RISK: unattended-upgrades appears stalled;' not in text
            and 'RISK: security-sensitive updates pending:' not in text
            and 'WARN: reboot required by previously installed updates' not in text
        ):
            score += 5
            reasons.append('latest infra-status shows pending updates awaiting the next unattended-upgrades window')
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
            raw_output = run_cmd(['bash', '-lc', "apt list --upgradable 2>/dev/null | sed -n '1,40p'"], max_chars=4000)
            listed = [line for line in raw_output.splitlines() if '/' in line and 'upgradable from:' in line]
            lines.append(render_auto_update_health(len(listed), now=now, package_lines=listed))
            if listed:
                lines.append('')
                lines.append('## Package Listing')
                lines.extend(listed[:40])
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
        lines.append('## Unexpected Listener Details')
        lines.append(inspect_unexpected_listener_details(port_lines))
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
            "(grep -H -Ei '^(PermitRootLogin|PasswordAuthentication|X11Forwarding|MaxAuthTries|PermitEmptyPasswords|MaxStartups|LoginGraceTime|AllowTcpForwarding|AllowAgentForwarding|AllowStreamLocalForwarding|PermitTunnel)\\b' "
            "/etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null | sed 's#^/etc/ssh/##' || "
            "echo 'SSH config unavailable') | sed -n '1,40p'"
        ]))
        lines.append('')
        lines.append('## SSH Hardening Validation')
        lines.append(ssh_hardening_validation_status())
        lines.append('')
        lines.append('## Recent SSH/Auth Findings')
        auth_sample, source = get_auth_sample()
        auth_lines = extract_recent_auth_findings(auth_sample)
        lines.append('\n'.join(auth_lines) if auth_lines else 'No recent SSH/auth findings in sampled logs')
        lines.append('')
        lines.append('## Auth Risk Assessment')
        lines.append(summarize_auth_risk(auth_sample, source))
        lines.append('')
        lines.append('## Auth Source Summary')
        lines.append(common_summarize_auth_event_sources(auth_sample, suspicious_pattern=AUTH_SUSPICIOUS_PATTERN))
        lines.append('')
        lines.append('## SSH Ban Hardening')
        lines.append(ssh_ban_hardening_status())
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
