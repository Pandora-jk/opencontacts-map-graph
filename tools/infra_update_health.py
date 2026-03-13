#!/usr/bin/env python3
"""
Helpers for assessing unattended-upgrades configuration and recent activity.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

AUTO_UPGRADES_CONFIG = Path('/etc/apt/apt.conf.d/20auto-upgrades')
UNATTENDED_UPGRADES_CONFIG = Path('/etc/apt/apt.conf.d/50unattended-upgrades')
UNATTENDED_UPGRADES_LOG = Path('/var/log/unattended-upgrades/unattended-upgrades.log')
AUTO_UPDATE_STALE_AFTER = dt.timedelta(hours=18)
AUTO_UPGRADES_REQUIRED_KEYS = {
    'APT::Periodic::Update-Package-Lists': '1',
    'APT::Periodic::Unattended-Upgrade': '1',
}
UNATTENDED_REQUIRED_ORIGINS = (
    '${distro_id}:${distro_codename}-security',
    '${distro_id}:${distro_codename}-updates',
)
_SETTING_RE = re.compile(r'^\s*([^"\s][^"]*?)\s+"([^"]*)";\s*$')
_RUN_TS_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+INFO\s+(.*)$')
_RUN_COMPLETE_PATTERNS = (
    'All upgrades installed',
    'No packages found that can be upgraded unattended and no pending auto-removals',
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return ''


def parse_auto_upgrade_settings(text: str) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw in text.splitlines():
        match = _SETTING_RE.match(raw.strip())
        if not match:
            continue
        settings[match.group(1).strip()] = match.group(2).strip()
    return settings


def unattended_origins_present(text: str) -> set[str]:
    found: set[str] = set()
    for origin in UNATTENDED_REQUIRED_ORIGINS:
        if origin in text:
            found.add(origin)
    return found


def load_auto_update_config(
    auto_upgrades_path: Path = AUTO_UPGRADES_CONFIG,
    unattended_path: Path = UNATTENDED_UPGRADES_CONFIG,
) -> dict[str, object]:
    auto_text = _read_text(auto_upgrades_path)
    unattended_text = _read_text(unattended_path)
    settings = parse_auto_upgrade_settings(auto_text)
    missing_required = {
        key: expected
        for key, expected in AUTO_UPGRADES_REQUIRED_KEYS.items()
        if settings.get(key) != expected
    }
    origins_present = unattended_origins_present(unattended_text)
    missing_origins = [origin for origin in UNATTENDED_REQUIRED_ORIGINS if origin not in origins_present]
    enabled = not missing_required and not missing_origins
    return {
        'settings': settings,
        'missing_required': missing_required,
        'origins_present': origins_present,
        'missing_origins': missing_origins,
        'enabled': enabled,
        'auto_upgrades_path': auto_upgrades_path,
        'unattended_path': unattended_path,
    }


def parse_latest_unattended_run(
    text: str,
) -> dict[str, object]:
    latest: dict[str, object] = {
        'started_at': None,
        'completed_at': None,
        'completion_line': '',
        'status': 'missing',
    }
    current: dict[str, object] | None = None
    for raw in text.splitlines():
        match = _RUN_TS_RE.match(raw)
        if not match:
            continue
        timestamp = dt.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.UTC)
        message = match.group(2).strip()
        if message == 'Starting unattended upgrades script':
            current = {
                'started_at': timestamp,
                'completed_at': None,
                'completion_line': '',
                'status': 'started',
            }
            latest = current
            continue
        if current is None:
            continue
        if message in _RUN_COMPLETE_PATTERNS:
            current['completed_at'] = timestamp
            current['completion_line'] = message
            current['status'] = 'completed'

    if latest['started_at'] and latest['status'] != 'completed':
        latest['status'] = 'incomplete'
    return latest


def load_latest_unattended_run(log_path: Path = UNATTENDED_UPGRADES_LOG) -> dict[str, object]:
    text = _read_text(log_path)
    latest = parse_latest_unattended_run(text)
    latest['log_path'] = log_path
    latest['log_available'] = bool(text)
    return latest


def render_auto_update_health(
    pending_count: int,
    *,
    now: dt.datetime | None = None,
    config: dict[str, object] | None = None,
    latest_run: dict[str, object] | None = None,
) -> str:
    reference_now = now or dt.datetime.now(dt.UTC)
    current_config = config or load_auto_update_config()
    current_run = latest_run or load_latest_unattended_run()
    lines = [f'{pending_count} pending updates' if pending_count > 0 else 'No pending updates']

    enabled = bool(current_config.get('enabled'))
    settings = current_config.get('settings', {})
    update_value = settings.get('APT::Periodic::Update-Package-Lists', 'unset')
    unattended_value = settings.get('APT::Periodic::Unattended-Upgrade', 'unset')
    if enabled:
        lines.append(
            'INFO: auto-updates enabled '
            f'(APT::Periodic::Update-Package-Lists={update_value}, '
            f'APT::Periodic::Unattended-Upgrade={unattended_value})'
        )
    else:
        reasons: list[str] = []
        missing_required = current_config.get('missing_required', {})
        if missing_required:
            for key, expected in missing_required.items():
                actual = settings.get(key, 'unset')
                reasons.append(f'{key}={actual} (expected {expected})')
        missing_origins = current_config.get('missing_origins', [])
        if missing_origins:
            reasons.append(f'missing origins: {", ".join(missing_origins)}')
        detail = '; '.join(reasons) if reasons else 'required unattended-upgrades settings missing'
        lines.append(f'RISK: auto-updates disabled or drifted ({detail})')

    started_at = current_run.get('started_at')
    completed_at = current_run.get('completed_at')
    status = current_run.get('status', 'missing')
    completion_line = str(current_run.get('completion_line', '')).strip()
    if status == 'completed' and isinstance(completed_at, dt.datetime):
        age = reference_now - completed_at
        age_hours = max(0, int(age.total_seconds() // 3600))
        lines.append(
            'INFO: unattended-upgrades last completed at '
            f'{completed_at.strftime("%Y-%m-%d %H:%M UTC")} ({age_hours}h ago): {completion_line}'
        )
    elif status == 'incomplete' and isinstance(started_at, dt.datetime):
        age = reference_now - started_at
        age_hours = max(0, int(age.total_seconds() // 3600))
        lines.append(
            'WARN: unattended-upgrades last started at '
            f'{started_at.strftime("%Y-%m-%d %H:%M UTC")} ({age_hours}h ago) but no completion was logged'
        )
    else:
        log_path = current_run.get('log_path', UNATTENDED_UPGRADES_LOG)
        lines.append(f'WARN: unattended-upgrades run history unavailable ({log_path})')

    if pending_count <= 0:
        return '\n'.join(lines)

    if not enabled:
        lines.append('RISK: pending updates are waiting while auto-updates are disabled')
        return '\n'.join(lines)

    if status == 'incomplete':
        lines.append('RISK: pending updates remain after an incomplete unattended-upgrades run')
        return '\n'.join(lines)

    if isinstance(completed_at, dt.datetime):
        age = reference_now - completed_at
        if age > AUTO_UPDATE_STALE_AFTER:
            lines.append(
                'RISK: pending updates remain and unattended-upgrades has not completed recently '
                f'({int(age.total_seconds() // 3600)}h old)'
            )
        else:
            lines.append('INFO: pending updates should clear on the next successful unattended-upgrades run')
    else:
        lines.append('WARN: pending updates detected but unattended-upgrades completion history is unavailable')

    return '\n'.join(lines)
