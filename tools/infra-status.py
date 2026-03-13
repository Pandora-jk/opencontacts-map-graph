#!/usr/bin/env python3
"""
Infra Status Check Script for Cron Job "Infra Findings Push"
Runs automated infrastructure checks and generates artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import os
import re
import shutil
import subprocess
import tempfile
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
from infra_update_health import render_auto_update_health

ROOT = Path('/home/ubuntu/.openclaw/workspace')
INFRA = ROOT / 'departments' / 'infra'
ART_DIR = INFRA / 'artifacts' / 'checks'
LOG_DIR = ROOT / 'logs'
ACTIVITY_LOG = LOG_DIR / 'infra-activity.log'
BACKUP_VERIFY_SCRIPT = ROOT / 'scripts' / 'verify-backup-integrity.sh'
MANAGED_SSHD_CONFIG = ROOT / 'ssh' / '99-openclaw-hardening.conf'
SSH_CONFIG_KEYS = {
    'permitrootlogin',
    'passwordauthentication',
    'x11forwarding',
    'permitemptypasswords',
    'maxauthtries',
    'maxstartups',
    'logingracetime',
    'allowtcpforwarding',
    'allowagentforwarding',
}
SSH_KEY_LABELS = {
    'permitrootlogin': 'PermitRootLogin',
    'passwordauthentication': 'PasswordAuthentication',
    'x11forwarding': 'X11Forwarding',
    'permitemptypasswords': 'PermitEmptyPasswords',
    'maxauthtries': 'MaxAuthTries',
    'maxstartups': 'MaxStartups',
    'logingracetime': 'LoginGraceTime',
    'allowtcpforwarding': 'AllowTcpForwarding',
    'allowagentforwarding': 'AllowAgentForwarding',
}
SSH_VISIBILITY_KEYS = (
    'permitrootlogin',
    'permitemptypasswords',
    'maxauthtries',
    'maxstartups',
    'logingracetime',
    'allowtcpforwarding',
    'allowagentforwarding',
)
KNOWN_SSHD_PATHS = (
    Path('/usr/sbin/sshd'),
    Path('/usr/local/sbin/sshd'),
    Path('/sbin/sshd'),
)
KNOWN_SSH_KEYGEN_PATHS = (
    Path('/usr/bin/ssh-keygen'),
    Path('/bin/ssh-keygen'),
)


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
    return render_auto_update_health(len(lines))


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
    in_match_block = False
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if re.match(r'^Match\b', line, re.IGNORECASE):
            in_match_block = True
            continue
        if in_match_block:
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        key = parts[0].lower()
        value = parts[1].split('#', 1)[0].strip().lower()
        if key in SSH_CONFIG_KEYS and value and key not in cfg:
            cfg[key] = value
    return cfg


def _include_tokens(value: str) -> list[str]:
    return [token.strip('"\'') for token in re.findall(r'"[^"]+"|\'[^\']+\'|\S+', value)]


def load_sshd_config_lines(path: Path, seen: set[Path] | None = None) -> list[str]:
    resolved = path.resolve(strict=False)
    if seen is None:
        seen = set()
    if resolved in seen or not path.exists():
        return []
    seen.add(resolved)

    lines: list[str] = []
    for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith('#'):
            parts = stripped.split(None, 1)
            if len(parts) == 2 and parts[0].lower() == 'include':
                for token in _include_tokens(parts[1]):
                    for match in sorted(glob.glob(token)):
                        lines.extend(load_sshd_config_lines(Path(match), seen))
                continue
        lines.append(raw)
    return lines


def read_sshd_config(path: Path = Path('/etc/ssh/sshd_config')) -> dict[str, str]:
    return parse_sshd_kv(load_sshd_config_lines(path))


def read_flat_sshd_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return parse_sshd_kv(path.read_text(encoding='utf-8', errors='ignore').splitlines())


def find_sshd_binary() -> str | None:
    binary = shutil.which('sshd')
    if binary:
        return binary
    for candidate in KNOWN_SSHD_PATHS:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def find_ssh_keygen_binary() -> str | None:
    binary = shutil.which('ssh-keygen')
    if binary:
        return binary
    for candidate in KNOWN_SSH_KEYGEN_PATHS:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def read_effective_sshd_config_with_temp_hostkey(
    sshd_binary: str,
    path: Path = Path('/etc/ssh/sshd_config'),
) -> dict[str, str]:
    ssh_keygen = find_ssh_keygen_binary()
    if not ssh_keygen:
        return {}

    try:
        with tempfile.TemporaryDirectory(prefix='openclaw-sshd-effective-') as tmpdir:
            stage_dir = Path(tmpdir)
            hostkey = stage_dir / 'ssh_host_ed25519_key'
            config_path = stage_dir / 'sshd_config'
            generated = subprocess.run(
                [ssh_keygen, '-q', '-N', '', '-t', 'ed25519', '-f', str(hostkey)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if generated.returncode != 0:
                return {}

            config_path.write_text(
                f'HostKey {hostkey}\nPidFile {stage_dir / "sshd.pid"}\nInclude {path}\n',
                encoding='utf-8',
            )
            try:
                os.chmod(config_path, 0o644)
            except OSError:
                pass

            out = run_cmd([sshd_binary, '-T', '-f', str(config_path)], max_chars=12000)
    except (OSError, subprocess.SubprocessError):
        return {}

    if not out or out == 'n/a' or out.startswith('Error:'):
        return {}
    return parse_sshd_kv(out.splitlines())


def get_effective_ssh_config() -> dict[str, str]:
    """Get effective SSH daemon settings, preferring `sshd -T`."""
    sshd = find_sshd_binary()
    if sshd:
        out = run_cmd([sshd, '-T'], max_chars=12000)
        if out and out != 'n/a' and not out.startswith('Error:'):
            parsed = parse_sshd_kv(out.splitlines())
            if parsed:
                return parsed
        parsed = read_effective_sshd_config_with_temp_hostkey(sshd)
        if parsed:
            return parsed

    return read_sshd_config()


def missing_ssh_visibility_keys(cfg: dict[str, str]) -> list[str]:
    return [key for key in SSH_VISIBILITY_KEYS if cfg.get(key, 'not_set') == 'not_set']


def render_ssh_key_labels(keys: list[str]) -> str:
    return ', '.join(SSH_KEY_LABELS.get(key, key) for key in keys)


def score_ssh_risk(cfg: dict[str, str], managed_cfg: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    """Return informational lines and risk findings for SSH settings."""
    info = []
    risks = []

    permit_root_login = cfg.get('permitrootlogin', 'not_set')
    password_auth = cfg.get('passwordauthentication', 'not_set')
    x11_forwarding = cfg.get('x11forwarding', 'not_set')
    empty_passwords = cfg.get('permitemptypasswords', 'not_set')
    max_auth_tries = cfg.get('maxauthtries', 'not_set')
    max_startups = cfg.get('maxstartups', 'not_set')
    login_grace_time = cfg.get('logingracetime', 'not_set')
    allow_tcp_forwarding = cfg.get('allowtcpforwarding', 'not_set')
    allow_agent_forwarding = cfg.get('allowagentforwarding', 'not_set')

    info.append(f'PermitRootLogin: {permit_root_login}')
    info.append(f'PasswordAuthentication: {password_auth}')
    info.append(f'X11Forwarding: {x11_forwarding}')
    info.append(f'PermitEmptyPasswords: {empty_passwords}')
    info.append(f'MaxAuthTries: {max_auth_tries}')
    info.append(f'MaxStartups: {max_startups}')
    info.append(f'LoginGraceTime: {login_grace_time}')
    info.append(f'AllowTcpForwarding: {allow_tcp_forwarding}')
    info.append(f'AllowAgentForwarding: {allow_agent_forwarding}')

    if permit_root_login == 'yes':
        risks.append('RISK: PermitRootLogin enabled')
    elif permit_root_login in {'without-password', 'prohibit-password'}:
        info.append('INFO: root SSH login is limited to keys')
    if password_auth == 'yes':
        risks.append('RISK: PasswordAuthentication enabled')
    if x11_forwarding == 'yes':
        risks.append('RISK: X11Forwarding enabled')
    if empty_passwords == 'yes':
        risks.append('CRITICAL: PermitEmptyPasswords enabled')
    if allow_tcp_forwarding == 'yes':
        risks.append('RISK: AllowTcpForwarding enabled')
    if allow_agent_forwarding == 'yes':
        risks.append('RISK: AllowAgentForwarding enabled')
    if max_auth_tries.isdigit() and int(max_auth_tries) > 4:
        risks.append(f'WARN: MaxAuthTries is high ({max_auth_tries})')

    missing_visibility = missing_ssh_visibility_keys(cfg)
    if missing_visibility:
        info.append(f'INFO: live SSH view does not explicitly show: {render_ssh_key_labels(missing_visibility)}')
        if managed_cfg:
            covered = [key for key in missing_visibility if managed_cfg.get(key, 'not_set') != 'not_set']
            if covered:
                info.append(f'INFO: managed workspace sshd drop-in explicitly sets: {render_ssh_key_labels(covered)}')
        risks.append('WARN: effective SSH hardening is only partially visible; some key settings are not explicitly set')
        risks.append('HARDENING: preview a managed sshd drop-in with `python3 tools/infra_sshd_hardening.py --stdout`')
        risks.append('HARDENING: sync the managed workspace sshd config with `python3 tools/infra_sshd_hardening.py --write-managed-config`')
        risks.append(
            'HARDENING: stage/test the install outside /etc with '
            '`python3 tools/infra_sshd_hardening.py --stage-dir /tmp/openclaw-sshd-stage --validate-live`'
        )

    return info, risks


def check_ssh_config() -> str:
    """Check SSH configuration for security issues."""
    cfg = get_effective_ssh_config()
    if not cfg:
        return 'SSH config unavailable'
    info, risks = score_ssh_risk(cfg, managed_cfg=read_flat_sshd_config(MANAGED_SSHD_CONFIG))
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


def first_signal_line(value: str) -> str:
    for raw in (value or '').splitlines():
        line = raw.strip()
        if line.startswith(('CRITICAL:', 'ALERT:', 'RISK:', 'WARN:', 'FAIL:', 'HARDENING:')):
            return line
    return one_line(value)


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
    ssh_signal = first_signal_line(ssh_result)
    if ssh_signal.startswith(('CRITICAL:', 'ALERT:', 'RISK:')):
        risk_summary.append(ssh_signal)
    elif ssh_signal.startswith(('WARN:', 'FAIL:')):
        risk_summary.append(f'RISK: {ssh_signal}')

    updates_result = findings['checks']['system_updates']['result']
    update_match = re.search(r'(\d+)\s+pending updates', updates_result)
    if update_match and int(update_match.group(1)) > 0:
        risk_summary.append(f'RISK: {update_match.group(1)} system updates pending')

    disk_result = findings['checks']['disk_usage']['result']
    if re.search(r'^(ALERT|CRITICAL):', disk_result, re.MULTILINE):
        risk_summary.append(f'RISK: {first_signal_line(disk_result)}')

    ports_result = findings['checks']['open_ports']['result']
    if ports_result.startswith('ALERT:'):
        risk_summary.append(f'RISK: {first_signal_line(ports_result)}')

    mdns_result = findings['checks']['mdns_exposure']['result']
    if re.search(r'^(ALERT|RISK|WARN|HARDENING):', mdns_result, re.MULTILINE):
        risk_summary.append(f'RISK: {first_signal_line(mdns_result)}')

    firewall_result = findings['checks']['firewall_status']['result']
    if re.search(r'^(ALERT|RISK|WARN):', firewall_result, re.MULTILINE):
        risk_summary.append(f'RISK: {first_signal_line(firewall_result)}')

    failed_result = findings['checks']['failed_logins']['result']
    if failed_result.startswith('ALERT:'):
        risk_summary.append(f'RISK: {first_signal_line(failed_result)}')

    backup_result = findings['checks']['backup_integrity']['result']
    if re.search(r'^(ALERT|FAIL|RISK|WARN):', backup_result, re.MULTILINE):
        risk_summary.append(f'RISK: {first_signal_line(backup_result)}')

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
