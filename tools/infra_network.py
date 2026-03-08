#!/usr/bin/env python3
from __future__ import annotations

import configparser
import re
import shutil
import subprocess
from pathlib import Path

MDNS_RESOLVED_DROPIN = "[Resolve]\nMulticastDNS=no\nLLMNR=no\n"
WORKSPACE_ROOT = Path('/home/ubuntu/.openclaw/workspace')
MANAGED_MDNS_DROPIN = WORKSPACE_ROOT / 'systemd' / '99-openclaw-no-mdns.conf'
LIVE_MDNS_DROPIN = Path('/etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf')


def run_cmd(cmd: list[str], max_chars: int = 800) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return f'Error: {str(exc)[:200]}'
    text = (proc.stdout or proc.stderr).strip()
    return text[:max_chars] if text else 'n/a'


def _service_state(service: str) -> str | None:
    systemctl = shutil.which('systemctl')
    if systemctl:
        enabled = run_cmd([systemctl, 'is-enabled', service], max_chars=80)
        active = run_cmd([systemctl, 'is-active', service], max_chars=80)
        if not any('Failed to connect to bus' in value or 'System has not been booted with systemd' in value for value in (enabled, active)):
            enabled_label = enabled if enabled not in {'n/a', ''} else 'unknown'
            active_label = active if active not in {'n/a', ''} else 'unknown'
            return f'{service}: enabled={enabled_label}, active={active_label}'

    service_cmd = shutil.which('service')
    if service_cmd:
        status = run_cmd([service_cmd, service, 'status'], max_chars=200)
        if status not in {'n/a', ''} and 'unrecognized service' not in status.lower():
            cleaned = re.sub(r'\s+', ' ', status)
            return f'{service}: {cleaned[:140]}'
    return None


def _resolved_settings(
    resolved_conf: Path = Path('/etc/systemd/resolved.conf'),
    dropins_dir: Path = Path('/etc/systemd/resolved.conf.d'),
) -> tuple[str | None, str | None]:
    parser = configparser.ConfigParser(strict=False)
    paths = [resolved_conf]
    if dropins_dir.is_dir():
        paths.extend(sorted(dropins_dir.glob('*.conf')))

    loaded = False
    for path in paths:
        if not path.exists():
            continue
        try:
            parser.read(path, encoding='utf-8')
            loaded = True
        except (configparser.Error, OSError):
            continue
    if not loaded or not parser.has_section('Resolve'):
        return None, None

    mdns = parser.get('Resolve', 'MulticastDNS', fallback=None)
    llmnr = parser.get('Resolve', 'LLMNR', fallback=None)
    return mdns, llmnr


def _dropin_mode(path: Path) -> int | None:
    try:
        return path.stat().st_mode & 0o777
    except OSError:
        return None


def _dropin_status(path: Path, *, label: str, ready_word: str) -> str:
    if not path.exists():
        return f'{label} drop-in missing: {path}'
    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        return f'{label} drop-in unreadable: {exc}'
    if content != MDNS_RESOLVED_DROPIN:
        return f'{label} drop-in drift: {path}'
    mode = _dropin_mode(path)
    if mode is None:
        return f'{label} drop-in ready: {path}'
    if mode != 0o644:
        return f'WARN: {label} drop-in permissions are {mode:04o} (expected 0644): {path}'
    return f'{label} drop-in {ready_word}: {path} (mode 0644)'


def managed_mdns_dropin_status(path: Path = MANAGED_MDNS_DROPIN) -> str:
    return _dropin_status(path, label='managed', ready_word='ready')


def live_mdns_dropin_status(path: Path = LIVE_MDNS_DROPIN) -> str:
    return _dropin_status(path, label='live', ready_word='installed')


def _nsswitch_hosts_line(path: Path = Path('/etc/nsswitch.conf')) -> str | None:
    if not path.exists():
        return None
    try:
        for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = raw.strip()
            if line.startswith('hosts:'):
                return re.sub(r'\s+', ' ', line)
    except OSError:
        return None
    return None


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
    preview = ', '.join(sorted(addresses))
    return f'Listener scope: {preview} ({len(lines)} socket(s))'


def inspect_mdns_exposure(
    port_lines: str,
    *,
    managed_dropin: Path = MANAGED_MDNS_DROPIN,
    live_dropin: Path = LIVE_MDNS_DROPIN,
    resolved_conf: Path = Path('/etc/systemd/resolved.conf'),
    resolved_dropins_dir: Path = Path('/etc/systemd/resolved.conf.d'),
    nsswitch_path: Path = Path('/etc/nsswitch.conf'),
) -> str:
    if 'udp/5353' not in port_lines and ':5353' not in port_lines:
        return 'No external mDNS listener detected'

    lines = ['ALERT: External mDNS listener detected on udp/5353']

    listener_detail = run_cmd(['bash', '-lc', "ss -H -ulpn 'sport = :5353' 2>/dev/null | sed -n '1,10p'"], max_chars=1200)
    if listener_detail not in {'n/a', ''} and not listener_detail.startswith('Error:'):
        scope = _listener_scope(listener_detail)
        if scope:
            lines.append(scope)
        if 'users:((' in listener_detail:
            owner = []
            for raw in listener_detail.splitlines():
                match = re.search(r'users:\(\("([^"]+)"', raw)
                if match:
                    owner.append(match.group(1))
            if owner:
                lines.append(f"Listener owner(s): {', '.join(sorted(dict.fromkeys(owner)))}")
            else:
                lines.append('Listener details captured but owning process was not parsed cleanly')
        else:
            lines.append('Listener owner not visible from current permissions/capabilities')
    elif listener_detail.startswith('Error:'):
        lines.append(f'mDNS listener detail error: {listener_detail}')

    for service in ('systemd-resolved', 'avahi-daemon'):
        state = _service_state(service)
        if state:
            lines.append(state)

    mdns, llmnr = _resolved_settings(resolved_conf=resolved_conf, dropins_dir=resolved_dropins_dir)
    if mdns is None and llmnr is None:
        lines.append('systemd-resolved config: no explicit MulticastDNS/LLMNR override found')
    else:
        lines.append(
            'systemd-resolved config: '
            f"MulticastDNS={mdns or 'default'}, LLMNR={llmnr or 'default'}"
        )
    lines.append(managed_mdns_dropin_status(managed_dropin))
    lines.append(live_mdns_dropin_status(live_dropin))

    hosts_line = _nsswitch_hosts_line(nsswitch_path)
    if hosts_line:
        lines.append(f'nsswitch hosts: {hosts_line}')
        if 'mdns' not in hosts_line.lower():
            lines.append('RISK: local host resolution does not reference mdns; external udp/5353 is less likely to be required')
    else:
        lines.append('nsswitch hosts: unavailable')

    if mdns is None or mdns.lower() != 'no':
        lines.append('HARDENING: set MulticastDNS=no if this host does not require mDNS service discovery')
    if llmnr is None or llmnr.lower() != 'no':
        lines.append('HARDENING: set LLMNR=no on public/cloud hosts unless explicitly required')
    lines.append('HARDENING: preview the managed drop-in with `python3 tools/infra_mdns_hardening.py --stdout`')
    lines.append('HARDENING: sync the managed workspace drop-in with `python3 tools/infra_mdns_hardening.py --write-managed-dropin`')
    lines.append(
        'HARDENING: stage/test the install outside /etc with '
        '`python3 tools/infra_mdns_hardening.py --install-to /tmp/resolved.conf.d/99-openclaw-no-mdns.conf '
        '--validate-live --live-dropin-path /tmp/resolved.conf.d/99-openclaw-no-mdns.conf '
        '--resolved-dropins-dir /tmp/resolved.conf.d`'
    )
    lines.append(
        'HARDENING: install the managed drop-in with '
        '`sudo install -D -m 0644 /home/ubuntu/.openclaw/workspace/systemd/99-openclaw-no-mdns.conf '
        '/etc/systemd/resolved.conf.d/99-openclaw-no-mdns.conf`'
    )
    lines.append('HARDENING: restart resolved and verify with `sudo systemctl restart systemd-resolved && python3 tools/infra_mdns_hardening.py --validate-live`')
    lines.append('HARDENING: if mDNS is unnecessary, disable avahi-daemon/systemd-resolved mDNS support or block udp/5353 upstream')
    return '\n'.join(lines)
