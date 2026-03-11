from __future__ import annotations

import re
from collections.abc import Callable

EXPECTED_EXTERNAL_PORTS = {'tcp': {22}, 'udp': {68}}
LOCAL_LISTENER_PREFIXES = (
    '127.',
    'localhost:',
    '127.0.0.53:',
    '127.0.0.54:',
    '[::1]',
    '[::ffff:127.',
)


def one_line(value: str, max_len: int = 140) -> str:
    txt = re.sub(r'\s+', ' ', (value or '').strip())
    return (txt[: max_len - 1] + '…') if len(txt) > max_len else txt


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


def summarize_external_ports(port_lines: str, expected_external_ports: dict[str, set[int]] | None = None) -> str:
    if not port_lines or port_lines == 'n/a':
        return 'No externally exposed listening ports found'
    if port_lines.startswith('Error:'):
        return port_lines

    external, local_only_count = classify_external_ports(port_lines)
    if not external:
        return f'No externally exposed listening ports (local-only listeners only: {local_only_count})'

    expected = expected_external_ports or EXPECTED_EXTERNAL_PORTS
    unexpected = []
    for entry in sorted(external):
        proto, value = entry.split('/', 1)
        if value.isdigit() and int(value) in expected.get(proto, set()):
            continue
        unexpected.append(entry)

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


def check_firewall_status(
    run_cmd: Callable[[list[str], int], str],
    *,
    which: Callable[[str], str | None],
    render_one_line: Callable[[str, int], str] = one_line,
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
