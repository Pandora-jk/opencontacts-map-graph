#!/usr/bin/env python3
"""
Infra Status Check Script for Cron Job "Infra Findings Push"
Runs automated infrastructure checks and generates artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
from pathlib import Path

from infra_audit_common import check_firewall_status as common_check_firewall_status
from infra_audit_common import filtered_auth_lines as common_filtered_auth_lines
from infra_audit_common import inspect_unexpected_listeners as common_inspect_unexpected_listeners
from infra_audit_common import is_self_generated_auth_audit_line as common_is_self_generated_auth_audit_line
from infra_audit_common import summarize_auth_event_sources as common_summarize_auth_event_sources
from infra_audit_common import summarize_external_ports as common_summarize_external_ports
from infra_audit_common import (
    AUTH_LOG_SAMPLE_LIMIT,
    AUTH_LOG_SAMPLE_MAX_CHARS,
    AUTH_SUSPICIOUS_ALERT_THRESHOLD,
    AUTH_SUSPICIOUS_PATTERN,
    auth_log_tail_command,
    journalctl_ssh_tail_command,
)
from infra_disk import build_disk_usage_report
from infra_network import inspect_mdns_exposure

ROOT = Path('/home/ubuntu/.openclaw/workspace')
INFRA = ROOT / 'departments' / 'infra'
ART_DIR = INFRA / 'artifacts' / 'checks'
LOG_DIR = ROOT / 'logs'
ACTIVITY_LOG = LOG_DIR / 'infra-activity.log'
BACKUP_VERIFY_SCRIPT = ROOT / 'scripts' / 'verify-backup-integrity.sh'


def run_cmd(cmd: list[str], max_chars: int = 800) -> str:
    """Run a shell command and return output (max 800 chars)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        txt = (p.stdout or p.stderr).strip()
        return txt[:max_chars] if txt else 'n/a'
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        return f'Error: {str(e)[:200]}'


def check_system_updates() -> str:
    """Check for pending system updates."""
    apt = shutil.which('apt')
    if not apt:
        return 'Package manager not available'

    output = run_cmd(['bash', '-lc', 'apt list --upgradable 2>/dev/null'])
    if output.startswith('Error:'):
        return output
    lines = [line for line in output.splitlines() if '/' in line and 'upgradable from:' in line]
    count = len(lines)
    if count > 0:
        return f'{count} pending updates'
    return 'No pending updates'


def check_disk_usage() -> str:
    """Check disk and inode usage on root; add safe triage when usage is high."""
    lines = build_disk_usage_report()
    return '\n'.join(lines) if lines else 'Disk usage unavailable'


def current_port_lines() -> str:
    return run_cmd(['bash', '-lc', "ss -H -tuln 2>/dev/null | awk '{print $1, $5}' | sort -u | sed -n '1,80p'"])


def check_open_ports(port_lines: str | None = None) -> str:
    """Check for externally exposed listening ports."""
    output = port_lines if port_lines is not None else current_port_lines()
    return common_summarize_external_ports(output)


def check_unexpected_listener_details(port_lines: str | None = None) -> str:
    """Inspect unexpected externally exposed listeners with process-aware detail when visible."""
    output = port_lines if port_lines is not None else current_port_lines()
    return common_inspect_unexpected_listeners(run_cmd, output)


def check_firewall_status() -> str:
    """Summarize host firewall tooling visibility."""
    return common_check_firewall_status(run_cmd, which=shutil.which, render_one_line=one_line)


def parse_sshd_kv(lines: list[str]) -> dict[str, str]:
    cfg: dict[str, str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        key = parts[0].lower()
        value = parts[1].lower()
        if key in {
            'permitrootlogin',
            'passwordauthentication',
            'x11forwarding',
            'permitemptypasswords',
            'maxauthtries',
        }:
            cfg[key] = value
    return cfg


def get_effective_ssh_config() -> dict[str, str]:
    """Get effective SSH daemon settings, preferring `sshd -T`."""
    sshd = shutil.which('sshd')
    if sshd:
        out = run_cmd([sshd, '-T'])
        if out and out != 'n/a' and not out.startswith('Error:'):
            return parse_sshd_kv(out.splitlines())

    ssh_config = Path('/etc/ssh/sshd_config')
    if ssh_config.exists():
        return parse_sshd_kv(ssh_config.read_text(encoding='utf-8', errors='ignore').splitlines())
    return {}


def score_ssh_risk(cfg: dict[str, str]) -> tuple[list[str], list[str]]:
    """Return informational lines and risk findings for SSH settings."""
    info = []
    risks = []

    permit_root_login = cfg.get('permitrootlogin', 'not_set')
    password_auth = cfg.get('passwordauthentication', 'not_set')
    x11_forwarding = cfg.get('x11forwarding', 'not_set')
    empty_passwords = cfg.get('permitemptypasswords', 'not_set')
    max_auth_tries = cfg.get('maxauthtries', 'not_set')

    info.append(f'PermitRootLogin: {permit_root_login}')
    info.append(f'PasswordAuthentication: {password_auth}')
    info.append(f'X11Forwarding: {x11_forwarding}')
    info.append(f'PermitEmptyPasswords: {empty_passwords}')
    info.append(f'MaxAuthTries: {max_auth_tries}')

    if permit_root_login in {'yes', 'without-password', 'prohibit-password'}:
        risks.append(f'RISK: PermitRootLogin={permit_root_login}')
    if password_auth == 'yes':
        risks.append('RISK: PasswordAuthentication enabled')
    if x11_forwarding == 'yes':
        risks.append('RISK: X11Forwarding enabled')
    if empty_passwords == 'yes':
        risks.append('CRITICAL: PermitEmptyPasswords enabled')

    return info, risks


def check_ssh_config() -> str:
    """Check SSH configuration for security issues."""
    cfg = get_effective_ssh_config()
    if not cfg:
        return 'SSH config unavailable'
    info, risks = score_ssh_risk(cfg)
    lines = info + risks
    return '\n'.join(lines)


def is_self_generated_auth_audit_line(line: str) -> bool:
    return common_is_self_generated_auth_audit_line(line)


def suspicious_auth_lines(log_text: str) -> list[str]:
    return common_filtered_auth_lines(log_text, AUTH_SUSPICIOUS_PATTERN)


def count_failed_auth_attempts(log_text: str) -> int:
    return len(suspicious_auth_lines(log_text))


def summarize_failed_auth(log_text: str) -> str:
    count = count_failed_auth_attempts(log_text)
    if count >= AUTH_SUSPICIOUS_ALERT_THRESHOLD:
        return f'ALERT: {count} suspicious auth lines found in sampled logs'
    if count == 0:
        return 'No failed authentication attempts found in sampled logs'
    return f'{count} suspicious auth lines found in sampled logs'


def get_auth_sample() -> tuple[str, str]:
    auth_log = Path('/var/log/auth.log')
    if auth_log.exists():
        return run_cmd(auth_log_tail_command(AUTH_LOG_SAMPLE_LIMIT), max_chars=AUTH_LOG_SAMPLE_MAX_CHARS), 'auth.log'
    journalctl = shutil.which('journalctl')
    if journalctl:
        return run_cmd(journalctl_ssh_tail_command(AUTH_LOG_SAMPLE_LIMIT), max_chars=AUTH_LOG_SAMPLE_MAX_CHARS), 'journalctl -u ssh'
    return '', ''


def check_failed_logins() -> str:
    """Check for recent failed SSH/auth attempts."""
    sampled, source = get_auth_sample()

    if not sampled or sampled == 'n/a':
        return 'No auth log source available'
    if sampled.startswith('Error:'):
        return sampled

    return f"{summarize_failed_auth(sampled)} ({source})"


def check_auth_source_summary() -> str:
    sampled, source = get_auth_sample()
    if not sampled or sampled == 'n/a':
        return 'No auth log source available'
    if sampled.startswith('Error:'):
        return sampled
    summary = common_summarize_auth_event_sources(sampled, suspicious_pattern=AUTH_SUSPICIOUS_PATTERN)
    if summary.startswith('No suspicious auth-event source summary'):
        return f'{summary} ({source})'
    return f'{summary}\nSource: {source}'


def check_backup_integrity() -> str:
    """Check backup integrity status."""
    if BACKUP_VERIFY_SCRIPT.exists():
        output = run_cmd([
            'bash',
            '-lc',
            f"bash '{BACKUP_VERIFY_SCRIPT}' --archive /tmp/latest-workspace-backup.tar.gz --source '{ROOT / 'INCOME-ENGINE.md'}' --enforce-permissions"
        ])
        if output.startswith('Error:') or output == 'n/a':
            return f'FAIL: backup integrity check execution issue ({output})'
        return output
    return 'FAIL: backup verification script not found'


def one_line(value: str, max_len: int = 140) -> str:
    txt = re.sub(r'\s+', ' ', (value or '').strip())
    return (txt[: max_len - 1] + '…') if len(txt) > max_len else txt


def check_service_health() -> str:
    """Check status of critical services."""
    services = ['ssh', 'nginx', 'docker', 'cron']
    output = []

    systemctl = shutil.which('systemctl')
    if systemctl:
        systemctl_usable = True
        for service in services:
            status = run_cmd([systemctl, 'is-active', service])
            if 'Failed to connect to bus' in status or 'System has not been booted with systemd' in status:
                systemctl_usable = False
                break
            output.append(f'{service}: {status or "unknown"}')
        if systemctl_usable:
            return '\n'.join(output)
        output.clear()

    service_cmd = shutil.which('service')
    if service_cmd:
        for service in services:
            status = run_cmd([service_cmd, service, 'status'])
            output.append(f'{service}: {one_line(status, 70)}')
        return '\n'.join(output)

    return 'service-manager: unavailable'


def append_activity(msg: str) -> None:
    """Append message to activity log."""
    ART_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    with ACTIVITY_LOG.open('a', encoding='utf-8') as f:
        f.write(f'[{now}] {msg}\n')


def generate_report() -> tuple[str, list[str]]:
    """Run all checks and generate report."""
    now = dt.datetime.now(dt.UTC)
    timestamp = now.strftime('%Y%m%dT%H%M%SZ')
    run_id = now.strftime('%Y%m%d')

    findings = {
        'timestamp': timestamp,
        'run_id': run_id,
        'checks': {}
    }

    findings['checks']['system_updates'] = {
        'status': 'checked',
        'result': check_system_updates()
    }

    findings['checks']['disk_usage'] = {
        'status': 'checked',
        'result': check_disk_usage()
    }

    port_lines = current_port_lines()
    findings['checks']['open_ports'] = {
        'status': 'checked',
        'result': check_open_ports(port_lines)
    }

    findings['checks']['unexpected_listener_details'] = {
        'status': 'checked',
        'result': check_unexpected_listener_details(port_lines)
    }

    findings['checks']['mdns_exposure'] = {
        'status': 'checked',
        'result': inspect_mdns_exposure(port_lines)
    }

    findings['checks']['firewall_status'] = {
        'status': 'checked',
        'result': check_firewall_status()
    }

    findings['checks']['ssh_config'] = {
        'status': 'checked',
        'result': check_ssh_config()
    }

    findings['checks']['failed_logins'] = {
        'status': 'checked',
        'result': check_failed_logins()
    }

    findings['checks']['auth_source_summary'] = {
        'status': 'checked',
        'result': check_auth_source_summary()
    }

    findings['checks']['backup_integrity'] = {
        'status': 'checked',
        'result': check_backup_integrity()
    }

    findings['checks']['service_health'] = {
        'status': 'checked',
        'result': check_service_health()
    }

    risk_summary = []
    ssh_result = findings['checks']['ssh_config']['result']
    if 'CRITICAL:' in ssh_result:
        risk_summary.append('CRITICAL: unsafe SSH settings detected')
    elif 'RISK:' in ssh_result:
        risk_summary.append('RISK: SSH hardening recommendations present')

    updates_result = findings['checks']['system_updates']['result']
    update_match = re.search(r'(\d+)\s+pending updates', updates_result)
    if update_match and int(update_match.group(1)) > 0:
        risk_summary.append(f'RISK: {update_match.group(1)} system updates pending')

    disk_result = findings['checks']['disk_usage']['result']
    if re.search(r'^(ALERT|CRITICAL):', disk_result, re.MULTILINE):
        risk_summary.append(f'RISK: {disk_result}')

    ports_result = findings['checks']['open_ports']['result']
    if ports_result.startswith('ALERT:'):
        risk_summary.append(f'RISK: {ports_result}')

    mdns_result = findings['checks']['mdns_exposure']['result']
    if re.search(r'^(ALERT|RISK|WARN|HARDENING):', mdns_result, re.MULTILINE):
        risk_summary.append(f'RISK: {mdns_result}')

    firewall_result = findings['checks']['firewall_status']['result']
    if re.search(r'^(ALERT|RISK|WARN):', firewall_result, re.MULTILINE):
        risk_summary.append(f'RISK: {firewall_result}')

    failed_result = findings['checks']['failed_logins']['result']
    if failed_result.startswith('ALERT:'):
        risk_summary.append(f'RISK: {failed_result}')

    backup_result = findings['checks']['backup_integrity']['result']
    if re.search(r'^(ALERT|FAIL|RISK|WARN):', backup_result, re.MULTILINE):
        risk_summary.append(f'RISK: {backup_result}')

    md_lines = [
        f"# Infra Status Check (Run {run_id})",
        '',
        f"- **Timestamp (UTC):** {timestamp}",
        f"- **Run ID:** {run_id}",
        '',
        '## System Updates',
        '',
        f"```\n{findings['checks']['system_updates']['result']}\n```",
        '',
        '## Disk Usage',
        '',
        f"```\n{findings['checks']['disk_usage']['result']}\n```",
        '',
        '## Open Ports',
        '',
        f"```\n{findings['checks']['open_ports']['result']}\n```",
        '',
        '## Unexpected Listener Details',
        '',
        f"```\n{findings['checks']['unexpected_listener_details']['result']}\n```",
        '',
        '## Multicast DNS Exposure',
        '',
        f"```\n{findings['checks']['mdns_exposure']['result']}\n```",
        '',
        '## Firewall Status',
        '',
        f"```\n{findings['checks']['firewall_status']['result']}\n```",
        '',
        '## SSH Configuration',
        '',
        f"```\n{findings['checks']['ssh_config']['result']}\n```",
        '',
        '## Failed Logins (Recent Sample)',
        '',
        f"```\n{findings['checks']['failed_logins']['result']}\n```",
        '',
        '## Auth Source Summary',
        '',
        f"```\n{findings['checks']['auth_source_summary']['result']}\n```",
        '',
        '## Backup Integrity',
        '',
        f"```\n{findings['checks']['backup_integrity']['result']}\n```",
        '',
        '## Service Health',
        '',
        f"```\n{findings['checks']['service_health']['result']}\n```",
        '',
        '## Risk Summary',
        '',
    ]

    if risk_summary:
        for item in risk_summary:
            md_lines.append(f'- {item}')
    else:
        md_lines.append('- No critical risks detected by current checks')

    md_lines.extend([
        '',
        '---',
        '',
        '*Generated by infra-status.py cron job*'
    ])

    md_content = '\n'.join(md_lines)

    summary_lines = [
        '[INFRA FINDINGS]',
        f'Time (UTC): {timestamp}',
        f"Updates: {one_line(findings['checks']['system_updates']['result'])}",
        f"Disk: {one_line(findings['checks']['disk_usage']['result'])}",
        f"Open Ports: {one_line(findings['checks']['open_ports']['result'])}",
        f"Unexpected Listener Detail: {one_line(findings['checks']['unexpected_listener_details']['result'])}",
        f"mDNS: {one_line(findings['checks']['mdns_exposure']['result'])}",
        f"Firewall: {one_line(findings['checks']['firewall_status']['result'])}",
        f"SSH: {one_line(findings['checks']['ssh_config']['result'])}",
        f"Failed Logins: {one_line(findings['checks']['failed_logins']['result'])}",
        f"Auth Sources: {one_line(findings['checks']['auth_source_summary']['result'])}",
        f"Backup: {one_line(findings['checks']['backup_integrity']['result'])}",
        f"Services: {one_line(findings['checks']['service_health']['result'])}",
    ]

    if risk_summary:
        summary_lines.append(f"Risk: {one_line('; '.join(risk_summary))}")
    else:
        summary_lines.append('Risk: none detected by current checks')

    return md_content, summary_lines


def main() -> int:
    parser = argparse.ArgumentParser(description='Infra status check for cron job')
    parser.parse_args()

    md_report, summary_lines = generate_report()

    timestamp = dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')
    artifact_path = ART_DIR / f"{timestamp}-infra-status.md"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(md_report, encoding='utf-8')
    os.chmod(artifact_path, 0o600)

    output = '\n'.join(summary_lines)
    print(output)

    append_activity(f"infra-status run={timestamp} artifact='{artifact_path.relative_to(ROOT)}'")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
