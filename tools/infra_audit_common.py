from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable
from pathlib import Path

AUTH_LOG_SAMPLE_LIMIT = 400
AUTH_LOG_SAMPLE_MAX_CHARS = 12000
AUTH_SUSPICIOUS_ALERT_THRESHOLD = 5
AUTH_SOURCE_SUMMARY_LIMIT = 5
EXPECTED_EXTERNAL_PORTS = {'tcp': {22}, 'udp': {68}}
UNEXPECTED_LISTENER_DETAIL_LIMIT = 5
LISTENER_HISTORY_ARTIFACT_LIMIT = 12
WORKSPACE_ROOT = Path('/home/ubuntu/.openclaw/workspace')
INFRA_CHECK_ARTIFACT_DIR = WORKSPACE_ROOT / 'departments' / 'infra' / 'artifacts' / 'checks'
LOCAL_LISTENER_PREFIXES = (
    '127.',
    'localhost:',
    '127.0.0.53:',
    '127.0.0.54:',
    '[::1]',
    '[::ffff:127.',
)
AUTH_SUSPICIOUS_PATTERN = re.compile(r'(failed|invalid user|authentication failure|error: pam)', re.IGNORECASE)
AUTH_SOURCE_PATTERNS = (
    re.compile(r'\bfrom\s+([0-9A-Fa-f:.]+)\b'),
    re.compile(
        r'\b(?:connection closed by|disconnected from)\s+invalid user(?:\s+\S+)?\s+([0-9A-Fa-f:.]+)\s+port\b',
        re.IGNORECASE,
    ),
)
AUTH_INVALID_USER_PATTERNS = (
    re.compile(r'\binvalid user\s+(\S+)\s+from\b', re.IGNORECASE),
    re.compile(r'\bfailed password for invalid user\s+(\S+)\s+from\b', re.IGNORECASE),
    re.compile(r'\bfailed password for\s+(\S+)\s+from\b', re.IGNORECASE),
    re.compile(
        r'\b(?:connection closed by|disconnected from)\s+invalid user\s+(\S+)\s+[0-9A-Fa-f:.]+\s+port\b',
        re.IGNORECASE,
    ),
)


def one_line(value: str, max_len: int = 140) -> str:
    txt = re.sub(r'\s+', ' ', (value or '').strip())
    return (txt[: max_len - 1] + '…') if len(txt) > max_len else txt


def ufw_boot_config_status(ufw_config_path: Path = Path('/etc/ufw/ufw.conf')) -> str | None:
    try:
        text = ufw_config_path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        if key.strip().upper() != 'ENABLED':
            continue
        enabled = value.strip().strip('"\'')
        if not enabled:
            return None
        return f'INFO: ufw boot config ENABLED={enabled} ({ufw_config_path})'
    return None


def auth_log_tail_command(limit: int = AUTH_LOG_SAMPLE_LIMIT) -> list[str]:
    return ['bash', '-lc', f'tail -n {limit} /var/log/auth.log 2>/dev/null']


def journalctl_ssh_tail_command(limit: int = AUTH_LOG_SAMPLE_LIMIT) -> list[str]:
    return ['bash', '-lc', f"journalctl -u ssh --since '24 hours ago' --no-pager 2>/dev/null | tail -n {limit}"]


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


def _extract_auth_source(line: str) -> str | None:
    for pattern in AUTH_SOURCE_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(1)
    return None


def _extract_auth_username(line: str) -> str | None:
    for pattern in AUTH_INVALID_USER_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(1)
    return None


def summarize_auth_event_sources(
    log_text: str,
    *,
    suspicious_pattern: re.Pattern[str] = AUTH_SUSPICIOUS_PATTERN,
    alert_threshold: int = AUTH_SUSPICIOUS_ALERT_THRESHOLD,
    detail_limit: int = AUTH_SOURCE_SUMMARY_LIMIT,
) -> str:
    suspicious_lines = filtered_auth_lines(log_text, suspicious_pattern)
    if not suspicious_lines:
        return 'No suspicious auth-event source summary available'

    counts: Counter[str] = Counter()
    users: dict[str, set[str]] = {}
    omitted_without_source = 0
    for line in suspicious_lines:
        source = _extract_auth_source(line)
        if not source:
            omitted_without_source += 1
            continue
        counts[source] += 1
        username = _extract_auth_username(line)
        if username:
            users.setdefault(source, set()).add(username)

    if not counts:
        return (
            f'Auth-event source summary unavailable '
            f'({len(suspicious_lines)} suspicious line(s) lacked a parseable source)'
        )

    top_sources = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    rendered_sources: list[str] = []
    for source, count in top_sources[:detail_limit]:
        usernames = sorted(users.get(source, set()))
        if usernames:
            preview = ', '.join(usernames[:3])
            if len(usernames) > 3:
                preview += ', ...'
            rendered_sources.append(f'{source} x{count} (users: {preview})')
        else:
            rendered_sources.append(f'{source} x{count}')

    level = 'ALERT' if len(suspicious_lines) >= alert_threshold else 'INFO'
    lines = [
        f"{level}: Auth event sources in sampled logs ({len(suspicious_lines)} events / {len(counts)} source(s)): "
        + '; '.join(rendered_sources)
    ]
    if omitted_without_source:
        lines.append(
            f'Note: {omitted_without_source} suspicious auth line(s) lacked a parseable source and were omitted from the source summary'
        )
    if len(top_sources) > detail_limit:
        lines.append(f'HARDENING: {len(top_sources) - detail_limit} additional auth-event source(s) omitted from detail view')
    if len(suspicious_lines) >= alert_threshold:
        lines.append('HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions')
        lines.append('HARDENING: preview a managed sshd drop-in with `python3 tools/infra_sshd_hardening.py --stdout`')
        lines.append('HARDENING: sync the managed workspace sshd config with `python3 tools/infra_sshd_hardening.py --write-managed-config`')
        lines.append(
            'HARDENING: stage/test the sshd install outside /etc with '
            '`python3 tools/infra_sshd_hardening.py --stage-dir /tmp/openclaw-sshd-stage --validate-live`'
        )
        lines.append(
            'HARDENING: install the managed sshd config with '
            '`sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/ssh/99-openclaw-hardening.conf '
            '/etc/ssh/sshd_config.d/99-openclaw-hardening.conf`'
        )
        lines.append(
            'HARDENING: reload ssh and verify with '
            '`sudo systemctl reload ssh && python3 tools/infra_sshd_hardening.py --validate-live` '
            '(expect LIVE_VALIDATION_DONE; LIVE_VALIDATION_FAILED means the managed config is missing/drifted)'
        )
        lines.append('HARDENING: preview a managed SSH ban config with `python3 tools/infra_ssh_ban_hardening.py --stdout`')
        lines.append('HARDENING: sync the managed workspace fail2ban config with `python3 tools/infra_ssh_ban_hardening.py --write-managed-config`')
        lines.append(
            'HARDENING: stage/test the install outside /etc with '
            '`python3 tools/infra_ssh_ban_hardening.py --stage-dir /tmp/openclaw-fail2ban-stage --validate-live`'
        )
        lines.append(
            'HARDENING: staged validation only confirms the managed config content/path; '
            'it does not enable host bans until the live /etc install and fail2ban restart'
        )
        lines.append(
            'HARDENING: install the managed config with '
            '`sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/fail2ban/99-openclaw-sshd.local '
            '/etc/fail2ban/jail.d/99-openclaw-sshd.local`'
        )
        lines.append(
            'HARDENING: restart fail2ban and verify with '
            '`sudo systemctl restart fail2ban && python3 tools/infra_ssh_ban_hardening.py --validate-live` '
            '(expect LIVE_VALIDATION_DONE; LIVE_VALIDATION_FAILED means the managed config is missing/drifted)'
        )
    return '\n'.join(lines)


def is_local_listener(address: str) -> bool:
    return any(address.startswith(prefix) for prefix in LOCAL_LISTENER_PREFIXES)


def classify_external_ports(port_lines: str) -> tuple[list[str], int]:
    external: set[str] = set()
    local_only_count = 0
    for raw in port_lines.splitlines():
        parts = raw.split()
        if len(parts) != 2:
            continue
        proto, address = parts
        if is_local_listener(address):
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


def unexpected_external_listeners(
    port_lines: str,
    expected_external_ports: dict[str, set[int]] | None = None,
) -> list[str]:
    external, _ = classify_external_ports(port_lines)
    expected = expected_external_ports or EXPECTED_EXTERNAL_PORTS
    unexpected: list[str] = []
    for entry in sorted(external):
        proto, value = entry.split('/', 1)
        if value.isdigit() and int(value) in expected.get(proto, set()):
            continue
        unexpected.append(entry)
    return unexpected


def summarize_external_ports(port_lines: str, expected_external_ports: dict[str, set[int]] | None = None) -> str:
    if not port_lines or port_lines == 'n/a':
        return 'No externally exposed listening ports found'
    if port_lines.startswith('Error:'):
        return port_lines

    external, local_only_count = classify_external_ports(port_lines)
    if not external:
        return f'No externally exposed listening ports (local-only listeners only: {local_only_count})'

    unexpected = unexpected_external_listeners(port_lines, expected_external_ports)

    preview = ', '.join(external[:8])
    if len(external) > 8:
        preview += ', ...'

    if unexpected:
        bad = ', '.join(unexpected[:8])
        if len(unexpected) > 8:
            bad += ', ...'
        lines = [f'ALERT: Unexpected externally exposed listeners ({len(unexpected)}): {bad}']
        for entry in unexpected:
            hint = explain_unexpected_listener(entry)
            if hint and hint not in lines:
                lines.append(hint)
        return '\n'.join(lines)

    return f'Externally exposed listeners match allowlist ({len(external)}): {preview}'


def _listener_query(entry: str) -> list[str]:
    proto, value = entry.split('/', 1)
    if value.isdigit():
        ss_flags = '-ulpn' if proto == 'udp' else '-tlpn'
        shell = f"ss -H {ss_flags} 'sport = :{value}' 2>/dev/null | sed -n '1,10p'"
    else:
        ss_flags = '-ulpn' if proto == 'udp' else '-tlpn'
        shell = f"ss -H {ss_flags} 2>/dev/null | grep -F -- '{value}' | sed -n '1,10p'"
    return ['bash', '-lc', shell]


def _listener_shell_hint(entry: str) -> str:
    return _listener_query(entry)[-1]


def _listener_scope(listener_detail: str) -> str | None:
    addresses: set[str] = set()
    lines = [line for line in listener_detail.splitlines() if line.strip()]
    if not lines:
        return None
    for raw in lines:
        parts = raw.split()
        if len(parts) >= 5:
            addresses.add(parts[4])
    if not addresses:
        return None
    return ', '.join(sorted(addresses))


def _listener_processes(listener_detail: str) -> list[tuple[str, str | None]]:
    processes: list[tuple[str, str | None]] = []
    for raw in listener_detail.splitlines():
        match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', raw)
        if match:
            processes.append((match.group(1), match.group(2)))
            continue
        match = re.search(r'users:\(\("([^"]+)"', raw)
        if match:
            processes.append((match.group(1), None))
    return list(dict.fromkeys(processes))


def recent_listener_artifact_hint(
    entry: str,
    *,
    artifact_dir: Path = INFRA_CHECK_ARTIFACT_DIR,
    limit: int = LISTENER_HISTORY_ARTIFACT_LIMIT,
) -> tuple[str, str | None, str | None, str | None] | None:
    if not artifact_dir.exists():
        return None

    entry_pattern = re.escape(entry)
    scope_re = re.compile(rf'^{entry_pattern} scope: (.+)$', re.MULTILINE)
    owner_re = re.compile(rf'^{entry_pattern} owner\(s\): (.+)$', re.MULTILINE)
    pid_re = re.compile(rf'^{entry_pattern} pid\(s\): (.+)$', re.MULTILINE)
    artifacts = sorted(artifact_dir.glob('*.md'), key=lambda path: path.stat().st_mtime, reverse=True)
    for artifact in artifacts[:limit]:
        try:
            text = artifact.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        owner_match = owner_re.search(text)
        if not owner_match:
            continue
        scope_match = scope_re.search(text)
        pid_match = pid_re.search(text)
        return (
            artifact.name,
            scope_match.group(1) if scope_match else None,
            owner_match.group(1),
            pid_match.group(1) if pid_match else None,
        )
    return None


def inspect_unexpected_listeners(
    run_cmd: Callable[[list[str], int], str],
    port_lines: str,
    *,
    expected_external_ports: dict[str, set[int]] | None = None,
    artifact_dir: Path = INFRA_CHECK_ARTIFACT_DIR,
) -> str:
    if not port_lines or port_lines == 'n/a':
        return 'No unexpected listener details to inspect'
    if port_lines.startswith('Error:'):
        return port_lines

    unexpected = unexpected_external_listeners(port_lines, expected_external_ports)
    if not unexpected:
        return 'No unexpected listener details to inspect'

    preview = ', '.join(unexpected[:8])
    if len(unexpected) > 8:
        preview += ', ...'

    lines = [f'ALERT: Detailed inspection for unexpected listeners ({len(unexpected)}): {preview}']
    for entry in unexpected[:UNEXPECTED_LISTENER_DETAIL_LIMIT]:
        detail = run_cmd(_listener_query(entry), max_chars=1200)
        recent_hint = recent_listener_artifact_hint(entry, artifact_dir=artifact_dir)
        if detail.startswith('Error:'):
            lines.append(f'{entry} detail error: {one_line(detail, 180)}')
            if recent_hint:
                artifact_name, scope, owner, pid = recent_hint
                if scope:
                    lines.append(f'INFO: recent artifact scope for {entry}: {scope} ({artifact_name})')
                lines.append(f'INFO: recent artifact attribution for {entry}: owner(s): {owner} ({artifact_name})')
                if pid:
                    lines.append(f'INFO: recent artifact pid(s) for {entry}: {pid} ({artifact_name})')
            lines.append(
                f"HARDENING: inspect {entry} from an unrestricted shell with "
                f"`{_listener_shell_hint(entry)}`"
            )
            continue
        if detail in {'n/a', ''}:
            lines.append(f'{entry} owner not visible from current permissions/capabilities')
            if recent_hint:
                artifact_name, scope, owner, pid = recent_hint
                if scope:
                    lines.append(f'INFO: recent artifact scope for {entry}: {scope} ({artifact_name})')
                lines.append(f'INFO: recent artifact attribution for {entry}: owner(s): {owner} ({artifact_name})')
                if pid:
                    lines.append(f'INFO: recent artifact pid(s) for {entry}: {pid} ({artifact_name})')
            lines.append(
                f"HARDENING: inspect {entry} from an unrestricted shell with "
                f"`{_listener_shell_hint(entry)}`"
            )
            lines.append(
                f'HARDENING: inspect/reconfigure the owning service before allowing external exposure on {entry}'
            )
            lines.append(
                f'HARDENING: if {entry} is not required publicly, bind it to loopback/internal interfaces only '
                'or block it with host/cloud firewall policy'
            )
            continue

        scope = _listener_scope(detail)
        if scope:
            lines.append(f'{entry} scope: {scope}')
        processes = _listener_processes(detail)
        owners = [owner for owner, _ in processes]
        if owners:
            lines.append(f"{entry} owner(s): {', '.join(owners)}")
        else:
            lines.append(f'{entry} owner not visible from current permissions/capabilities')
            if recent_hint:
                artifact_name, hint_scope, owner, pid = recent_hint
                if hint_scope and not scope:
                    lines.append(f'INFO: recent artifact scope for {entry}: {hint_scope} ({artifact_name})')
                lines.append(f'INFO: recent artifact attribution for {entry}: owner(s): {owner} ({artifact_name})')
                if pid:
                    lines.append(f'INFO: recent artifact pid(s) for {entry}: {pid} ({artifact_name})')
            lines.append(
                f"HARDENING: inspect {entry} from an unrestricted shell with "
                f"`{_listener_shell_hint(entry)}`"
            )
        pids = [pid for _, pid in processes if pid]
        if pids:
            lines.append(f"{entry} pid(s): {', '.join(pids)}")
            lines.append(f"HARDENING: inspect the owning process with `ps -fp {' '.join(pids)}`")
        else:
            lines.append(
                f'HARDENING: inspect/reconfigure the owning service before allowing external exposure on {entry}'
            )
        lines.append(
            f'HARDENING: if {entry} is not required publicly, bind it to loopback/internal interfaces only '
            'or block it with host/cloud firewall policy'
        )

    if len(unexpected) > UNEXPECTED_LISTENER_DETAIL_LIMIT:
        remaining = len(unexpected) - UNEXPECTED_LISTENER_DETAIL_LIMIT
        lines.append(f'HARDENING: {remaining} additional unexpected listener(s) omitted from detail view')

    return '\n'.join(lines)


def check_firewall_status(
    run_cmd: Callable[[list[str], int], str],
    *,
    which: Callable[[str], str | None],
    render_one_line: Callable[[str, int], str] = one_line,
    ufw_config_path: Path = Path('/etc/ufw/ufw.conf'),
) -> str:
    lines: list[str] = []
    ufw_lookup = run_cmd(
        [
            'bash',
            '-lc',
            'if command -v ufw >/dev/null 2>&1; then command -v ufw; '
            'elif test -x /usr/sbin/ufw; then printf "/usr/sbin/ufw\\n"; fi',
        ],
        max_chars=100,
    )
    ufw_installed = bool(ufw_lookup and ufw_lookup != 'n/a' and not ufw_lookup.startswith('Error:'))
    nft = which('nft')
    iptables = which('iptables')

    if ufw_installed:
        status = run_cmd(['bash', '-lc', 'sudo ufw status verbose 2>&1 | sed -n "1,20p"'], max_chars=1200)
        if re.search(r'^Status:\s+active\b', status, re.IGNORECASE | re.MULTILINE):
            lines.append('ufw: active')
        elif re.search(r'^Status:\s+inactive\b', status, re.IGNORECASE | re.MULTILINE):
            lines.append('ALERT: ufw installed but inactive')
        elif 'no new privileges' in status.lower() or 'permission denied' in status.lower():
            lines.append('WARN: ufw installed but status visibility is blocked by current privileges')
            lines.append(f'ufw: {render_one_line(status, 180)}')
            boot_config = ufw_boot_config_status(ufw_config_path)
            if boot_config:
                lines.append(boot_config)
            lines.append('HARDENING: verify `sudo ufw status verbose` from an unrestricted host shell')
        else:
            lines.append(f'ufw: {render_one_line(status, 180)}')
    else:
        lines.append('WARN: ufw unavailable on host')

    other_tools = [name for name, found in (('nft', nft), ('iptables', iptables)) if found]
    if other_tools:
        lines.append(f"Other firewall tooling detected: {', '.join(other_tools)}")
    elif not ufw_installed:
        lines.append('RISK: No host firewall tool detected (ufw/nft/iptables unavailable)')

    lines.append('Note: upstream cloud firewalls/security groups are not visible from this host check')
    return '\n'.join(lines)
